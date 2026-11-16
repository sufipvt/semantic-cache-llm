import time
import statistics

from src.llm import get_llm_response
from src.cache import search_cache


QUESTION = "What is machine learning?"
ITERATIONS = 10

llm_times = []
cache_times = []


# Warm up embedding model and Redis search
search_cache(QUESTION)


# Benchmark direct Groq calls
print("Benchmarking direct Groq calls...")

for i in range(ITERATIONS):
    start = time.perf_counter()

    get_llm_response(QUESTION)

    elapsed = time.perf_counter() - start
    llm_times.append(elapsed)

    print(f"LLM {i + 1}: {elapsed:.4f}s")


# Benchmark Redis cache hits
print("\nBenchmarking Redis cache hits...")

for i in range(ITERATIONS):
    start = time.perf_counter()

    answer = search_cache(QUESTION)

    elapsed = time.perf_counter() - start
    cache_times.append(elapsed)

    if answer is None:
        raise RuntimeError("Expected cache hit, but received cache miss.")

    print(f"Cache {i + 1}: {elapsed:.4f}s")


# Calculate statistics
avg_llm = statistics.mean(llm_times)
avg_cache = statistics.mean(cache_times)

median_llm = statistics.median(llm_times)
median_cache = statistics.median(cache_times)

speedup = avg_llm / avg_cache

print("\n========== FINAL BENCHMARK ==========")

print(f"Iterations: {ITERATIONS}")

print(f"\nLLM Average: {avg_llm:.4f}s")
print(f"LLM Median: {median_llm:.4f}s")
print(f"LLM Min: {min(llm_times):.4f}s")
print(f"LLM Max: {max(llm_times):.4f}s")

print(f"\nCache Average: {avg_cache:.4f}s")
print(f"Cache Median: {median_cache:.4f}s")
print(f"Cache Min: {min(cache_times):.4f}s")
print(f"Cache Max: {max(cache_times):.4f}s")

print(f"\nSpeed Improvement: {speedup:.2f}x")

print(f"LLM Calls Avoided: {ITERATIONS}")
print(f"Cache Correctness: {answer is not None}")