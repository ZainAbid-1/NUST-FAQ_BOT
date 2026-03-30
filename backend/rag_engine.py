import os
import json
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class HybridRAGEngine:
    def __init__(self, data_dir='data', models_dir='models'):
        print("Initializing Hybrid RAG Engine...")
        self.data_dir = data_dir
        self.models_dir = models_dir
        
        # 1. Load Embedder
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Load FAISS mapping & Index
        self.index = faiss.read_index(f'{self.data_dir}/faqs_index.bin')
        with open(f'{self.data_dir}/faqs_chunks.json', 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
            
        # 3. Load BM25 Index
        with open(f'{self.data_dir}/faqs_bm25.pkl', 'rb') as f:
            self.bm25 = pickle.load(f)
            
        # 4. Load LLM
        os.makedirs(self.models_dir, exist_ok=True)
        model_name = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
        model_path = os.path.join(self.models_dir, model_name)
        
        if not os.path.exists(model_path):
            print(f"Downloading {model_name} (approx 400MB). This is much faster than the old model...")
            model_path = hf_hub_download(repo_id="Qwen/Qwen2.5-0.5B-Instruct-GGUF", 
                                         filename=model_name,
                                         local_dir=self.models_dir)
                                         
        print("Loading Qwen2.5-0.5B into memory...")
        import multiprocessing
        # CPU optimization: For llama.cpp, using physical cores (approx half of logical cores)
        # avoids hyperthreading overhead and significantly drops inference latency
        n_threads = max(1, multiprocessing.cpu_count() // 2) if multiprocessing.cpu_count() else 4
        self.llm = Llama(
            model_path=model_path, 
            n_ctx=768, 
            n_batch=256, 
            n_threads=n_threads, 
            use_mlock=True,
            verbose=False
        )
        print("Engine Ready!")

    def query(self, user_query, history=None, top_k=3):
        if history is None:
            history = []
            
        search_query = user_query
        if history:
            # Gather up to 3 most recent user messages to retain the full topical context for semantic search
            all_user_msgs = [m['content'] for m in history if m['role'] == 'user']
            if all_user_msgs:
                search_query = " ".join(all_user_msgs[-3:]) + " " + user_query

        # 1. FAISS Semantic Search
        q_emb = self.embedder.encode([search_query])
        q_emb = np.array(q_emb).astype('float32')
        faiss.normalize_L2(q_emb)
        faiss_scores, faiss_indices = self.index.search(q_emb, k=top_k*2)
        
        # 2. BM25 Keyword Search
        tokenized_query = search_query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:top_k*2]
        
        # 3. Reciprocal Rank Fusion / Simple normalization fusion
        combined_scores = {}
        for rank, idx in enumerate(faiss_indices[0]):
            combined_scores[idx] = combined_scores.get(idx, 0) + (1.0 / (rank + 60))
        for rank, idx in enumerate(bm25_top_indices):
            combined_scores[idx] = combined_scores.get(idx, 0) + (1.0 / (rank + 60))
            
        # Sort fused scores
        best_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Ensure we have the top semantic score for confidence logic
        top_semantic_score = float(faiss_scores[0][0])
        
        retrieved_contexts = []
        citations = []
        for idx_tuple in best_indices:
            idx = idx_tuple[0]
            chunk = self.chunks[idx]
            retrieved_contexts.append(chunk['text'])
            citations.append({
                "category": chunk['category'],
                "question": chunk['question']
            })

        context_block = "\n\n".join(retrieved_contexts)
        
        # Direct-Match Bypassing (Instant Response)
        if top_semantic_score >= 0.75:
            return {
                "answer": self.chunks[best_indices[0][0]]['answer'],
                "citations": citations,
                "confidence_status": "green",
                "top_similarity": top_semantic_score
            }

        # Early Exit for Completely Irrelevant Queries (Instant Response)
        if top_semantic_score < 0.35:
            return {
                "answer": "I don't have information on this topic. I am specifically programmed to answer NUST Admissions FAQs. How else can I help you?",
                "citations": [],
                "confidence_status": "red",
                "top_similarity": top_semantic_score
            }

        # Confidence Threshold Fallback
        is_uncertain = top_semantic_score < 0.55
        
        history_msgs = ""
        for msg in history:
            history_msgs += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"

        prompt = f"""<|im_start|>system
You are a strict offline Admissions Assistant for NUST (National University of Sciences & Technology, Pakistan).
Your ONLY task is to answer the user's question using EXACTLY the information in the provided Context.
- NEVER add examples, exams, dates, or rules not present in the Context.
- Do NOT generate lists unless they exist in the Context.
Context:
{context_block}<|im_end|>
{history_msgs}<|im_start|>user
{user_query}<|im_end|>
<|im_start|>assistant
"""
        
        if is_uncertain:
            prompt = f"""<|im_start|>system
You are a strict offline Admissions Assistant for NUST (National University of Sciences & Technology, Pakistan).
The provided context may not exactly answer the user's question. If the context contains a partial answer, provide what you can.
- NEVER add examples, exams, dates, or rules not present in the Context.
Context:
{context_block}<|im_end|>
{history_msgs}<|im_start|>user
{user_query}<|im_end|>
<|im_start|>assistant
I'm not completely certain — """

        # Generate Generation with optimized max_tokens and 0.0 temperature to prevent hallucination
        response = self.llm(prompt, max_tokens=150, stop=["<|im_end|>", "<|im_start|>"], temperature=0.0)
        generated_text = response['choices'][0]['text'].strip()
        
        if is_uncertain:
            generated_text = "I'm not completely certain — " + generated_text
            
        return {
            "answer": generated_text,
            "citations": citations,
            "confidence_status": "red" if is_uncertain else "green",
            "top_similarity": top_semantic_score
        }

# Test block
if __name__ == "__main__":
    engine = HybridRAGEngine()
    res = engine.query("What are the medical requirements for MBBS?")
    print(res)
