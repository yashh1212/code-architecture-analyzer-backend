from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path

from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from llm.gemini import ask_llm   # or gemini client

router = APIRouter()


# -------------------------
# Request Schema
# -------------------------
class ChatRequest(BaseModel):
    repo_id: str
    question: str


# -------------------------
# Architecture-Level Chat Route
# -------------------------
@router.post("/ask")
def ask_architecture_question(data: ChatRequest):

    repo_path = Path(f"repos/{data.repo_id}")

    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not found")

    # -------------------------
    # Load Vector Index
    # -------------------------
    embedder = Embedder()
    store = VectorStore(dim=384)

    try:
        store.load(repo_id=data.repo_id)
    except:
        raise HTTPException(
            status_code=400,
            detail="Repository not indexed yet"
        )

    # -------------------------
    # Embed Question
    # -------------------------
    query_vector = embedder.embed([data.question])[0]

    # -------------------------
    # Semantic Retrieval
    # -------------------------
    results = store.search(query_vector, top_k=6)

    if not results:
        return {
            "answer": "No relevant architecture context found.",
            "sources": []
        }

    # -------------------------
    # Build Context Block
    # -------------------------
    context_blocks = []

    for r in results:
        context_blocks.append(
            f"""
File: {r.get('file')}
Role: {r.get('role')}
Framework: {r.get('framework')}
Type: {r.get('type')}

Code:
{r.get('content')}
"""
        )

    context = "\n\n".join(context_blocks)

    # -------------------------
    # Strong Architecture Prompt
    # -------------------------
    prompt = f"""
You are a senior software architect analyzing a real production codebase.

Below are relevant code sections retrieved from the repository.

=== REPOSITORY CONTEXT START ===
{context}
=== REPOSITORY CONTEXT END ===

User Question:
{data.question}

Instructions:
- Give an architecture-level explanation
- Mention execution flow
- Mention involved layers (frontend/backend/service/db)
- Reference specific files when possible
- Avoid guessing if not found in context
- Keep answer technical and structured

Provide answer in clear paragraphs.
"""

    # -------------------------
    # Call LLM
    # -------------------------
    answer = ask_llm(prompt)

    return {
        "answer": answer,
        "sources": list(set([r.get("file") for r in results]))
    }
