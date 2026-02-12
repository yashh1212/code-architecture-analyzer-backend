from pathlib import Path

from utils.language_detector import detect_language
from parsing.parser_router import parse_code
from chunking.semantic_chunker import build_semantic_chunks
from enrichment.enrich_pipeline import enrich_chunks
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore


REPO_PATH = Path("repos/44f84827-b042-4b74-810a-e42fc4858e25")

embedder = Embedder()
store = VectorStore(dim=384)

all_chunks = []

# -------------------------
# UNIVERSAL FILE LOOP
# -------------------------
for file in REPO_PATH.rglob("*"):
    if not file.is_file():
        continue

    language = detect_language(file)
    if not language:
        continue  

    code = file.read_text(encoding="utf-8", errors="ignore")
    parsed = parse_code(code, language)

    chunks = build_semantic_chunks(
        file_path=str(file),
        language=language,
        raw_code=code,
        parsed_data=parsed
    )

    all_chunks.extend(chunks)

# -------------------------
# Enrich metadata
# -------------------------
enriched_chunks = enrich_chunks(all_chunks)

# -------------------------
# Prepare embedding inputs
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
    metadatas.append(meta)

# -------------------------
# Embed + index
# -------------------------
vectors = embedder.embed(texts)
store.add(vectors, metadatas)

print(f"\n✅ Indexed {len(vectors)} chunks from MULTI-LANGUAGE repo")

# -------------------------
# Test semantic retrieval
# -------------------------
queries = [
    "Where is the machine learning model loaded?",
    "Where are API routes defined?",
    "Which file handles authentication?",
]

for q in queries:
    print(f"\n🔍 Query: {q}")
    q_vec = embedder.embed([q])[0]
    results = store.search(q_vec, top_k=3)

    for r in results:
        print(f"- {r['file']} | role={r['role']} | framework={r['framework']}")
        
