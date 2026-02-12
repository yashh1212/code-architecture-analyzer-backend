import faiss
import pickle
from pathlib import Path


class VectorStore:

    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    # -------------------------
    # Add vectors
    # -------------------------
    def add(self, vectors, metadatas):
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    # -------------------------
    # Save per repo
    # -------------------------
    def save(self, repo_id: str):

        base_path = Path("vector_indexes") / repo_id
        base_path.mkdir(parents=True, exist_ok=True)

        index_path = base_path / "index.faiss"
        metadata_path = base_path / "metadata.pkl"

        faiss.write_index(self.index, str(index_path))

        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    # -------------------------
    # Load per repo
    # -------------------------
    def load(self, repo_id: str):

        base_path = Path("vector_indexes") / repo_id

        index_path = base_path / "index.faiss"
        metadata_path = base_path / "metadata.pkl"

        self.index = faiss.read_index(str(index_path))

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

    # -------------------------
    # Search
    # -------------------------
    def search(self, query_vector, top_k=5):

        distances, indices = self.index.search(
            query_vector.reshape(1, -1), top_k
        )

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results
