# ingestion/file_filter.py

IGNORED_DIRS = {
    "node_modules", ".git", "dist", "build",
    "__pycache__", ".venv", "env"
}

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".lock", ".zip", ".exe"
}

def is_valid_file(path: str) -> bool:
    for part in path.split("/"):
        if part in IGNORED_DIRS:
            return False
    return not any(path.endswith(ext) for ext in IGNORED_EXTENSIONS)
