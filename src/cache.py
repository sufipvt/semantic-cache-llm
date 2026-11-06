"""Semantic cache implementation."""
import faiss
import numpy as np
from src.embeddings import generate_embedding
import time 

total_queries = 0
cache_hits = 0
cache_misses = 0

# create faiss index
index = faiss.IndexFlatIP(384)  # 384 is the dimension of the embeddings

#store question and answers
cached_question = []
cached_answer = []
cached_timestamps = []  # Store timestamps for each cached entry
TTL = 3600  # Time-to-live in seconds (1 hour)

#minimum threshold required for cached hit
THRESHOLD = 0.80

def add_to_cache(question: str, answer: str):
    embedding = generate_embedding(question)
    #store the vector in faiss index
    index.add(np.array([embedding], dtype = np.float32))

    cached_question.append(question)
    cached_answer.append(answer)
    cached_timestamps.append(time.time())  # Store the current timestamp


def search_cache(question: str):
    global total_queries, cache_hits, cache_misses

    total_queries += 1

    # If the cache is empty, count a miss
    if index.ntotal == 0:
        cache_misses += 1
        return None

    # Generate embedding
    embedding = generate_embedding(question)
    vector = np.array([embedding], dtype=np.float32)

    # Find the most similar stored question
    scores, indices = index.search(vector, 1)

    similarity = float(scores[0][0])
    match_index = int(indices[0][0])

    print("Similarity score:", round(similarity, 4))

    if similarity >= THRESHOLD:

        # Check TTL
        if is_expired(match_index):
            print("CACHE EXPIRED — CACHE MISS")
            cache_misses += 1
            return None

        # Check intent
        cached_type = get_question_type(cached_question[match_index])
        new_type = get_question_type(question)

        if cached_type != new_type:
            print("INTENT MISMATCH — CACHE MISS")
            cache_misses += 1
            return None

        print("CACHE HIT")
        cache_hits += 1
        return cached_answer[match_index]

    print("CACHE MISS")
    cache_misses += 1

    return None


def is_expired(match_index):
    current_time = time.time()
    created_time = cached_timestamps[match_index]
    age = current_time - created_time
    return age > TTL

def get_question_type(question):
    question = question.lower().strip()

    definition_words = [
        "what is",
        "what are",
        "define",
        "explain"
    ]

    action_words = [
        "how do i",
        "how can i",
        "how to",
        "steps to",
        "ways to"
    ]

    if any(word in question for word in action_words):
        return "action"

    if any(word in question for word in definition_words):
        return "definition"

    return "general"

if __name__ == "__main__":

    # Add one question to cache
    add_to_cache(
        "What is an API?",
        "An API allows software applications to communicate."
    )

    questions = [
        "What is an API?",
        "How do I build an API?",
        "What is machine learning?",
        "Explain an API",
        "Tell me about APIs"
    ]

    for question in questions:
        print("\nQuestion:", question)
        answer = search_cache(question)
        print("Answer:", answer)

    print("\n========== CACHE STATISTICS ==========")
    print("Total queries:", total_queries)
    print("Cache hits:", cache_hits)
    print("Cache misses:", cache_misses)