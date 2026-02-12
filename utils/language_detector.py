from pathlib import Path

def detect_language(file_path: Path) -> str | None:
    suffix = file_path.suffix.lower()

    if suffix == ".py":
        return "python"
    if suffix in {".js", ".jsx"}:
        return "javascript"
    if suffix in {".ts", ".tsx"}:
        return "typescript"  # future
    if suffix == ".java":
        return "java"  # future

    return None
