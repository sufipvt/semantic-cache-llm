"""Semantic cache implementation."""
import faiss
import numpy as np
from src.embeddings import generate_embedding
import time 
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
    embedding = generate_embedding(question)
    # If the cache is empty, return a cache miss
    if index.ntotal == 0:
        return None
    # convert the new question embedding to a numpy array
    embedding = generate_embedding(question)
    vector = np.array([embedding], dtype=np.float32)

    #find the most similar stored question in the cache
    scores,indices = index.search(vector, 1)  # 1 - returns single most similar stored vector - search for the closest vector

    # extract score and position
    similarity = float(scores[0][0])
    match_index = int(indices[0][0])

    print("Similarity score:", round(similarity, 4))

    if similarity >= THRESHOLD:
        if is_expired(match_index):
            print("CACHE EXPIRED — CACHE MISS")
            return None

        cached_type = get_question_type(cached_question[match_index])
        new_type = get_question_type(question)

        if cached_type != new_type:
            print("INTENT MISMATCH — CACHE MISS")
            return None

        print("CACHE HIT")
        return cached_answer[match_index]

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

    questions = [
        "What is an API?",
        "Explain an API",
        "How do I build an API?",
        "How can I use an API?",
        "Tell me about APIs"
    ]

    for question in questions:
        print(question, "->", get_question_type(question))