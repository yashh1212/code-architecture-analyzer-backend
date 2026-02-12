from pathlib import Path
from parsing.python_parser import parse_python_code

REPO_PATH = Path("repos/heart_disease_repo")

py_files = list(REPO_PATH.rglob("*.py"))

print(f"\nFound {len(py_files)} Python files\n")

for file in py_files:
    print(f"📄 {file.relative_to(REPO_PATH)}")

    code = file.read_text(encoding="utf-8", errors="ignore")
    parsed = parse_python_code(code)

    print("Imports:", parsed["imports"])
    print("From Imports:", parsed["from_imports"])
    print("Functions:", list(parsed["functions"].keys()))
    print("Classes:", parsed["classes"])
    print("Calls:", parsed["function_calls"])
    print("Assignments:", parsed["assignments"])
    print("Decorators:", parsed["decorators"])
    print("-" * 60)
