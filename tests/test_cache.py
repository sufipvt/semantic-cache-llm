
import time

from src import cache


def reset_cache():
    """Reset global cache state before each test."""
    cache.index.reset()
    cache.cached_question.clear()
    cache.cached_answer.clear()
    cache.cached_timestamps.clear()
    cache.total_queries = 0
    cache.cache_hits = 0
    cache.cache_misses = 0


def test_cache_hit():
    reset_cache()

    question = "What is an API?"
    expected_answer = "An API allows software applications to communicate."

    cache.add_to_cache(question, expected_answer)

    result = cache.search_cache(question)

    assert result == expected_answer


def test_cache_miss():
    reset_cache()

    cache.add_to_cache(
        "What is an API?",
        "An API allows software applications to communicate."
    )

    result = cache.search_cache("What is machine learning?")

    assert result is None


def test_intent_mismatch():
    reset_cache()

    cache.add_to_cache(
        "What is an API?",
        "An API allows software applications to communicate."
    )

    result = cache.search_cache("How do I build an API?")

    assert result is None


def test_ttl_expiration():
    reset_cache()

    cache.add_to_cache(
        "What is an API?",
        "An API allows software applications to communicate."
    )

    # Simulate an expired entry
    cache.cached_timestamps[0] = time.time() - cache.TTL - 10

    result = cache.search_cache("What is an API?")

    assert result is None

def test_cache_statistics():
    reset_cache()

    cache.add_to_cache(
        "What is an API?",
        "An API allows software applications to communicate."
    )

    cache.search_cache("What is an API?")          # Hit
    cache.search_cache("What is machine learning?")  # Miss

    assert cache.total_queries == 2
    assert cache.cache_hits == 1
    assert cache.cache_misses == 1
    assert cache.total_queries == cache.cache_hits + cache.cache_misses