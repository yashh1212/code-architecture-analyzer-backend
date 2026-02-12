from parsing.js_parser import parse_js
from pathlib import Path

sample_path = Path(__file__).parent / "sample.js"
with open(sample_path, "r", encoding="utf-8") as f:
    code = f.read()

result = parse_js(code)

print("Functions:", result["functions"])
print("Imports:", result["imports"])
print("Routes:", result["routes"])
