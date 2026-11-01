"""Embedding generation utilities."""

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(text: str):
    """Generate an embedding for the given text."""
    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )
    return embedding
