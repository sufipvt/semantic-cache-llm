
"""Redis-based semantic cache implementation."""

import redis
import uuid
import numpy as np

from src.embeddings import generate_embedding


# ==========================================
# 1. REDIS CONNECTION
# ==========================================

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=False,
    socket_connect_timeout=5,
    socket_timeout=5
)


def check_redis_connection():
    """Check whether Redis is available."""

    try:
        return r.ping()

    except redis.exceptions.RedisError as e:
        print(f"Redis connection failed: {e}")
        return False


# ==========================================
# 2. CONFIGURATION
# ==========================================

INDEX_NAME = "llm_cache_idx"
KEY_PREFIX = "llmcache:"
VECTOR_DIM = 384
TTL = 3600
THRESHOLD = 0.20


# ==========================================
# 3. CACHE STATISTICS
# ==========================================

total_queries = 0
cache_hits = 0
cache_misses = 0


def get_cache_stats():
    """Return cache performance statistics."""

    hit_rate = (
        (cache_hits / total_queries) * 100
        if total_queries > 0
        else 0
    )

    return {
        "total_queries": total_queries,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "hit_rate": round(hit_rate, 2)
    }


# ==========================================
# 4. INPUT VALIDATION
# ==========================================

def validate_question(question: str):
    """Validate incoming questions."""

    if not isinstance(question, str):
        raise ValueError("Question must be a string.")

    if not question.strip():
        raise ValueError("Question cannot be empty.")


# ==========================================
# 5. INTENT CLASSIFICATION
# ==========================================

def classify_intent(question: str) -> str:
    """Classify a question into an intent category."""

    question = question.lower().strip()

    comparison_patterns = [
        "difference between",
        "compare",
        "versus",
        " vs ",
    ]

    troubleshooting_patterns = [
        "not working",
        "error",
        "issue",
        "problem",
        "fix",
        "troubleshoot",
        "debug",
    ]

    procedure_patterns = [
        "how do i",
        "how can i",
        "how to",
        "steps to",
        "install",
        "configure",
        "set up",
        "setup",
        "create",
        "build",
        "cook",
        "make",
    ]

    definition_patterns = [
        "what is",
        "what are",
        "who is",
        "define",
        "explain",
        "describe",
        "meaning of",
        "how does",
        "how do",
        "how is",
        "what happens",
    ]

    if any(p in question for p in comparison_patterns):
        return "comparison"

    if any(p in question for p in troubleshooting_patterns):
        return "troubleshooting"

    if any(p in question for p in procedure_patterns):
        return "procedure"

    if any(p in question for p in definition_patterns):
        return "definition"

    return "general"


# ==========================================
# 6. ADD ANSWER TO CACHE
# ==========================================

def add_to_cache(question: str, answer: str, embedding=None):
    """Store an answer and its embedding in Redis."""

    validate_question(question)

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Answer cannot be empty.")

    # Reuse an existing embedding if provided
    if embedding is None:
        embedding = generate_embedding(question)

    vector_bytes = np.array(
        embedding,
        dtype=np.float32
    ).tobytes()

    intent = classify_intent(question)

    cache_key = f"{KEY_PREFIX}{uuid.uuid4()}"

    try:

        # Store the record and TTL atomically
        with r.pipeline(transaction=True) as pipe:

            pipe.hset(
                cache_key,
                mapping={
                    "question": question,
                    "response": answer,
                    "intent": intent,
                    "embedding": vector_bytes
                }
            )

            pipe.expire(cache_key, TTL)

            pipe.execute()

        return True

    except redis.exceptions.RedisError as e:

        print(f"Redis storage failed: {e}")
        return False


# ==========================================
# 7. SEARCH CACHE
# ==========================================

def search_cache(question: str, embedding=None):
    """Search Redis for a semantically similar cached answer."""

    global total_queries, cache_hits, cache_misses

    validate_question(question)

    # Count incoming user query
    total_queries += 1

    # Reuse an existing embedding if provided
    if embedding is None:
        embedding = generate_embedding(question)

    query_vector = np.array(
        embedding,
        dtype=np.float32
    ).tobytes()

    # Classify incoming question
    query_intent = classify_intent(question)

    # Search Redis using vector similarity
    try:

        results = r.execute_command(
            "FT.SEARCH",
            INDEX_NAME,
            f"@intent:{{{query_intent}}}=>[KNN 1 @embedding $vec AS distance]",
            "PARAMS", "2", "vec", query_vector,
            "SORTBY", "distance",
            "RETURN", "3", "question", "response", "distance",
            "DIALECT", "2"
        )

    except redis.exceptions.RedisError as e:

        print(f"Redis search failed: {e}")

        cache_misses += 1

        return None

    # Check whether matching records exist
    if results[b"total_results"] == 0:

        cache_misses += 1

        print("CACHE MISS: No matching intent")

        return None

    # Validate returned cache record
    try:

        record = results[b"results"][0]

        data = record[b"extra_attributes"]

        distance = float(data[b"distance"])

        cached_response = data[b"response"].decode("utf-8")

        if not cached_response.strip():
            raise ValueError("Cached response is empty.")

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        AttributeError
    ) as e:

        print(f"Invalid cache record: {e}")

        cache_misses += 1

        return None

    # Display search information
    print("Query intent:", query_intent)

    print("Similarity distance:", round(distance, 4))

    # Check similarity threshold
    if distance <= THRESHOLD:

        cache_hits += 1

        print("CACHE HIT")

        return cached_response

    cache_misses += 1

    print("CACHE MISS: Similarity below threshold")

    return None
