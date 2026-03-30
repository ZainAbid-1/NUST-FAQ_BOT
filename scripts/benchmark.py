import time
import psutil
import os
import sys

# Append parent dir so we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.rag_engine import HybridRAGEngine

def print_memory_usage(prefix=""):
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    ram_mb = mem_info.rss / (1024 * 1024)
    print(f"[{prefix}] Current RAM usage: {ram_mb:.2f} MB")
    return ram_mb

def main():
    print("=== NUST Offline FAQ Bot Benchmark ===")
    print_memory_usage("START")
    
    start_init = time.time()
    engine = HybridRAGEngine(
        data_dir=os.path.join(os.path.dirname(__file__), '..', 'data'),
        models_dir=os.path.join(os.path.dirname(__file__), '..', 'models')
    )
    init_time = time.time() - start_init
    print(f"Engine Initialization Time: {init_time:.2f}s")
    base_ram = print_memory_usage("POST-INIT")
    
    if base_ram > 4000:
        print("[WARNING] RAM usage exceeds the 4GB (4000MB) budget!")
    else:
        print("[PASS] RAM usage is strictly well under 4GB footprint.")

    test_queries = [
        "What are the requirements for MBBS admission?",
        "How is the BSHND merit formula calculated?",
        "When does the Fall semester begin?",
        "Who won the world cup in 2022?" # Expected to trigger Red confidence
    ]

    total_latency = 0
    print("\nStarting generation benchmark...")
    
    for i, q in enumerate(test_queries):
        print(f"\nQuery {i+1}: '{q}'")
        start = time.time()
        res = engine.query(q)
        latency = time.time() - start
        total_latency += latency
        
        print(f"Latency: {latency:.2f}s | Confidence: {res['confidence_status']} | Top Similarity: {res['top_similarity']:.2f}")
        print(f"Answer snippet: {res['answer'][:100]}...")
        
        if latency > 1.5:
            print("[WARNING] Generation latency exceeded 1.5s.")
        else:
            print("[PASS] Generation latency < 1.5s.")
            
    avg_latency = total_latency / len(test_queries)
    print(f"\n=== Benchmark Complete ===")
    print(f"Average latency per query: {avg_latency:.2f}s")
    print_memory_usage("END")

if __name__ == "__main__":
    main()
