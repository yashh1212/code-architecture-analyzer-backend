from typing import Dict, List


# ---------- DETECTION RULES ----------

ML_KEYWORDS = {"fit", "predict", "transform", "model"}
AUTH_KEYWORDS = {"auth", "login", "token", "jwt"}
API_KEYWORDS = {"route", "request", "response"}
DB_KEYWORDS = {"db", "session", "query", "commit"}


def detect_framework(imports: List[str]) -> str | None:
    joined = " ".join(imports).lower()
    if "fastapi" in joined:
        return "fastapi"
    if "flask" in joined:
        return "flask"
    if "django" in joined:
        return "django"
    if "sklearn" in joined:
        return "sklearn"
    if "torch" in joined:
        return "pytorch"
    if "express" in joined:
        return "express"
    return None


def detect_role(signals: List[str]) -> str | None:
    s = set(signals)
    if s & ML_KEYWORDS:
        return "ml_logic"
    if s & AUTH_KEYWORDS:
        return "authentication"
    if s & API_KEYWORDS:
        return "api"
    if s & DB_KEYWORDS:
        return "database"
    return "utility"


# ---------- MAIN ENRICHER ----------

def enrich_chunk(chunk: Dict) -> Dict:
    metadata = chunk.get("metadata", {})

    imports = metadata.get("imports", [])
    calls = metadata.get("calls", [])
    symbols = [chunk.get("name", "")]

    signals = list(set(symbols + calls))

    enriched_metadata = {
        **metadata,
        "language": chunk.get("language"),
        "file": chunk.get("file"),
        "chunk_type": chunk.get("type"),
        "symbols": symbols,
        "dependencies": imports,
        "calls": calls,
        "signals": signals,
        "framework": detect_framework(imports),
        "role": detect_role(signals),
    }

    chunk["metadata"] = enriched_metadata
    return chunk
