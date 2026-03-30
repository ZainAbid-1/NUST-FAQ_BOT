import json
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

def main():
    print("Loading FAQs...")
    with open('data/nust_faqs.json', 'r', encoding='utf-8') as f:
        faqs = json.load(f)

    # 1. Prepare chunks
    # Since most FAQs are small, we treat one FAQ as one chunk
    # We will format it properly
    chunks = []
    for faq in faqs:
        text = f"Category: {faq['category']}\nQuestion: {faq['question']}\nAnswer: {faq['answer']}"
        chunks.append({
            "text": text,
            "category": faq['category'],
            "question": faq['question'],
            "answer": faq['answer']
        })
        
    texts = [c["text"] for c in chunks]

    # 2. Build FAISS Index
    print("Loading all-MiniLM-L6-v2 embedding model...")
    # This model outputs 384 dimensional vectors, runs very fast on CPU
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # Normalize vectors for Cosine Similarity in FAISS (Inner Product becomes Cosine)
    faiss.normalize_L2(embeddings)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) # Inner product with normalized vectors = Cosine Sim
    index.add(embeddings)
    
    print("Saving FAISS index...")
    faiss.write_index(index, 'data/faqs_index.bin')

    # 3. Build BM25 Index
    print("Building BM25 Keyword index...")
    # Tokenize by splitting on whitespace and converting to lowercase
    tokenized_corpus = [doc.lower().split(" ") for doc in texts]
    bm25 = BM25Okapi(tokenized_corpus)
    
    print("Saving BM25 index...")
    with open('data/faqs_bm25.pkl', 'wb') as f:
        pickle.dump(bm25, f)
        
    # Save the chunk references
    with open('data/faqs_chunks.json', 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=4)
        
    print("Hybrid Indexing completed successfully. Total Data Size < 100MB.")

if __name__ == "__main__":
    main()
