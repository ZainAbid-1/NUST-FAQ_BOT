@echo off
echo ==============================================
echo   NUST Offline Admissions FAQ Assistant
echo   Powered by Hybrid RAG (FAISS + BM25) + Phi-3
echo ==============================================

if not exist venv\Scripts\activate.bat (
    echo [ERROR] Virtual Environment not found. Please run Phase 1 setup first.
    pause
    exit /b 1
)

echo Activating Virtual Environment...
call venv\Scripts\activate.bat

echo Starting Server...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause
