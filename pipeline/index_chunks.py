from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from enrichment.enrich_pipeline import enrich_chunks

def index_chunks(chunks):
    embedder = Embedder()
    store = VectorStore(dim=384)

    texts = []
    metadatas = []

    for chunk in chunks:
        text = f"""
        {chunk['type']} {chunk['name']}
        Role: {chunk['metadata']['role']}
        Framework: {chunk['metadata']['framework']}
        File: {chunk['file']}

        {chunk['content']}
        """
        texts.append(text)
        metadatas.append(chunk["metadata"])

    vectors = embedder.embed(texts)
    store.add(vectors, metadatas)

    return store
