from pathlib import Path

from utils.language_detector import detect_language
from parsing.parser_router import parse_code
from chunking.semantic_chunker import build_semantic_chunks
from enrichment.enrich_pipeline import enrich_chunks
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore


def process_repository(repo_id: str):

    repo_path = Path(f"repos/{repo_id}")

    if not repo_path.exists():
        raise ValueError("Repository not found")

    embedder = Embedder()
    store = VectorStore(dim=384)

    all_chunks = []

    # -------------------------
    # STEP 1: Parse + Chunk
    # -------------------------
    for file in repo_path.rglob("*"):

        if not file.is_file():
            continue

        language = detect_language(file)
        if not language:
            continue

        try:
            code = file.read_text(encoding="utf-8", errors="ignore")
        except:
            continue

        parsed = parse_code(code, language)

        chunks = build_semantic_chunks(
            file_path=str(file),
            language=language,
            raw_code=code,
            parsed_data=parsed
        )

        all_chunks.extend(chunks)

    # -------------------------
    # STEP 2: Enrichment
    # -------------------------
    enriched_chunks = enrich_chunks(all_chunks)

    # -------------------------
    # STEP 3: Prepare Embeddings
    # -------------------------
    texts = []
    metadatas = []

    for chunk in enriched_chunks:

        meta = chunk["metadata"]

        text = f"""
        Language: {meta['language']}
        Type: {chunk['type']}
        Name: {chunk['name']}
        Role: {meta['role']}
        Framework: {meta['framework']}
        File: {meta['file']}
        Signals: {meta['signals']}

        Code:
        {chunk['content']}
        """

        texts.append(text)
        metadatas.append({
            **meta,
            "content": chunk["content"],
            "type": chunk["type"],
            "name": chunk["name"]
        })

    # -------------------------
    # STEP 4: Embed
    # -------------------------
    vectors = embedder.embed(texts)

    # -------------------------
    # STEP 5: Save FAISS index
    # -------------------------
    store.add(vectors, metadatas)
    store.save(repo_id)

    return {
        "status": "processed",
        "chunks_indexed": len(vectors)
    }
