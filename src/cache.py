"""Semantic cache implementation."""
import faiss
import numpy as np
from src.embeddings import generate_embedding

# create faiss index
index = faiss.IndexFlatIP(384)  # 384 is the dimension of the embeddings

#store question and answers
cached_question = []
cached_answer = []

#minimum threshold required for cached hit
THRESHOLD = 0.80

def add_to_cache(question: str, answer: str):
    embedding = generate_embedding(question)
    #store the vector in faiss index
    index.add(np.array([embedding], dtype = np.float32))

    cached_question.append(question)
    cached_answer.append(answer)

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
        print("CACHE HIT")
        return cached_answer[match_index]
    else:
        print("CACHE MISS")
        return None
    

    