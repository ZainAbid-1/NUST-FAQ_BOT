# 🎓 NUST Offline Admissions FAQ Bot

A **100% offline**, high-performance RAG (Retrieval-Augmented Generation) chatbot for answering NUST admissions-related FAQs. Powered by a hybrid FAISS + BM25 retrieval system and a local GGUF LLM, with a sleek NUST-branded web interface.

---

## 🚀 Features

- 🔒 **Fully Offline** — no internet required after setup
- ⚡ **Hybrid Retrieval** — FAISS semantic search + BM25 keyword matching
- 🤖 **Local LLM** — runs `Phi-3-mini-4k-instruct` or `Qwen2.5-0.5B` via `llama-cpp-python`
- 💬 **Chat History** — context-aware follow-up question support
- 🌐 **FastAPI Backend** + clean HTML/CSS/JS frontend
- 🏫 **NUST Branded** UI

---

## 📁 Project Structure

```
nust-faq-bot/
├── backend/
│   ├── main.py          # FastAPI server & API endpoints
│   └── rag_engine.py    # Hybrid RAG pipeline
├── frontend/
│   ├── index.html       # Main UI
│   ├── style.css        # Styling
│   └── app.js           # Frontend logic
├── data/
│   ├── nust_faqs.json       # Source FAQ data
│   ├── faqs_chunks.json     # Chunked FAQ data
│   ├── faqs_index.bin       # FAISS vector index
│   ├── faqs_bm25.pkl        # BM25 index
│   ├── faqs.html            # Scraped FAQ HTML
│   └── bshnd.html           # Scraped Admissions HTML
├── scripts/
│   ├── scrape_faqs.py       # Web scraper for NUST FAQs
│   ├── build_hybrid_index.py # Builds FAISS + BM25 index
│   └── benchmark.py         # Performance benchmarking
├── models/              # Place your .gguf model files here (not included)
├── requirements.txt     # Python dependencies
└── run.bat              # Windows startup script
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/ZainAbid-1/NUST-FAQ_BOT.git
cd NUST-FAQ_BOT
```

### 2. Create & activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the LLM model
Download one of the following GGUF models and place it in the `models/` folder:

- **Phi-3-mini-4k-instruct-q4.gguf** (Recommended, ~2.3 GB)  
  → [Download from HuggingFace](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)

- **qwen2.5-0.5b-instruct-q4_k_m.gguf** (Lightweight, ~491 MB)  
  → [Download from HuggingFace](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF)

### 5. Run the server
```bash
run.bat
```
Then open your browser at: **http://127.0.0.1:8000**

---

## 🛠️ Rebuilding Indexes (Optional)

If you want to re-scrape or rebuild the FAISS/BM25 indexes:

```bash
python scripts/scrape_faqs.py
python scripts/build_hybrid_index.py
```

---

## 📋 Requirements

- Python 3.10+
- Windows (for `run.bat`; Linux/Mac users can run `uvicorn backend.main:app` directly)
- Minimum 8 GB RAM recommended

---

## 📄 License

This project is open-source and built for educational purposes at NUST.
