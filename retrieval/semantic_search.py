# retrieval/semantic_search.py
import faiss
import numpy as np

class SemanticSearch:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, vectors, meta):
        self.index.add(np.array(vectors))
        self.metadata.extend(meta)

    def search(self, vector, k=5):
        distances, indices = self.index.search(
            np.array([vector]), k
        )
        return [self.metadata[i] for i in indices[0]]
