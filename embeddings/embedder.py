from sentence_transformers import SentenceTransformer
from typing import List

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: List[str]):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        )

def build_embedding_text(chunk):
    meta = chunk["metadata"]

    return f"""
    Type: {chunk['type']}
    Name: {chunk['name']}
    Role: {meta['role']}
    Framework: {meta['framework']}
    File: {meta['file']}
    Signals: {meta['signals']}

    Code:
    {chunk['content']}
    """
