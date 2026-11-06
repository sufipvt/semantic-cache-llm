import time
import statistics
from src.cache import add_to_cache, search_cache
from src.llm import get_llm_response

QUESTION = " what is machine learning?"
CACHED_ANSWER = "Machine learning enables computers to learn patterns from data."

def benchmark_cache():
    add_to_cache(QUESTION, CACHED_ANSWER)
    cache_time = []
    print("\nBenchmarking cache hits...")

    for i in range(5):
        start = time.perf_counter()
        answer = search_cache(QUESTION)
        end = time.perf_counter()
        if answer is not None:
            cache_time.append(end - start)
    return cache_time

def benchmark_llm():
    llm_time = []
    print("\nBenchmarking LLM responses...")

    for i in range(3):
        start = time.perf_counter()
        answer = get_llm_response(QUESTION)
        end = time.perf_counter()
        llm_time.append(end - start)
    return llm_time


if __name__ == "__main__":

    cache_times = benchmark_cache()
    llm_times = benchmark_llm()

    avg_cache = statistics.mean(cache_times)
    avg_llm = statistics.mean(llm_times)

    print("\n========== BENCHMARK RESULTS ==========")

    print(f"Average cache latency: {avg_cache * 1000:.2f} ms")
    print(f"Average LLM latency:   {avg_llm:.2f} seconds")

    speedup = avg_llm / avg_cache

    print(f"Cache speed improvement: {speedup:.2f}x")

