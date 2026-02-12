from parsing.python_parser import parse_python_code
from parsing.js_parser import parse_js

def parse_code(code: str, language: str) -> dict:
    if language == "python":
        return parse_python_code(code)

    if language == "javascript":
        return parse_js(code)

    # unsupported language (safe fallback)
    return {}
