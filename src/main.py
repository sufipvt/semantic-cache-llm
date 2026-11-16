from src.cache import (
    search_cache,
    add_to_cache,
    check_redis_connection,
    validate_question
)

from src.embeddings import generate_embedding
from src.llm import get_llm_response


def ask_question(question: str) -> str:

    print(f"\nUser Question: {question}")

    # Step 1: Validate input
    validate_question(question)

    embedding = None
    redis_available = check_redis_connection()

    # Step 2: Generate embedding and search cache
    if redis_available:

        try:
            print("Redis is available. Generating embedding...")
            embedding = generate_embedding(question)

        except Exception as e:
            print(f"Embedding generation failed: {e}")

        # Search cache only if embedding generation succeeded
        if embedding is not None:

            try:
                print("Searching Redis cache...")

                cached_answer = search_cache(question, embedding)

                if cached_answer is not None:
                    print("Returning cached response.")
                    return cached_answer

            except Exception as e:
                print(f"Cache lookup failed: {e}")

    else:
        print("Redis unavailable. Skipping cache.")

    # Step 3: Generate answer using Groq
    print("Calling Groq LLM...")

    answer = get_llm_response(question)

    # Step 4: Store response if caching is possible
    if redis_available and embedding is not None:

        stored = add_to_cache(question, answer, embedding)

        if stored:
            print("Response stored in Redis.")
        else:
            print("Answer generated but could not be cached.")

    else:
        print("Skipping cache storage.")

    # Step 5: Return answer
    return answer