from pathlib import Path
from parsing.python_parser import parse_python_code
from chunking.semantic_chunker import build_semantic_chunks

REPO_PATH = Path("repos/heart_disease_repo")

for file in REPO_PATH.glob("*.py"):
    code = file.read_text(encoding="utf-8", errors="ignore")
    parsed = parse_python_code(code)

    chunks = build_semantic_chunks(
        file_path=str(file),
        language="python",
        raw_code=code,
        parsed_data=parsed
    )

    print(f"\n📄 {file.name} → {len(chunks)} chunks")
    for c in chunks:
        print(f"  🔹 {c['type']} → {c['name']}")
