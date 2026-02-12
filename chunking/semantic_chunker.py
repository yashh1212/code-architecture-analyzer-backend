from typing import List, Dict


def build_semantic_chunks(
    *,
    file_path: str,
    language: str,
    raw_code: str,
    parsed_data: Dict
) -> List[Dict]:
    """
    Build semantic chunks from parsed code.
    Works for Python, JavaScript, or any language with parser output.
    """

    chunks = []

    # -------------------------
    # PYTHON CHUNKING
    # -------------------------
    if language == "python":
        # Function chunks
        for fn_name, fn_meta in parsed_data.get("functions", {}).items():
            chunks.append({
                "type": "function",
                "name": fn_name,
                "language": "python",
                "file": file_path,
                "content": extract_block(raw_code, fn_name),
                "metadata": {
                    "args": fn_meta.get("args"),
                    "decorators": fn_meta.get("decorators"),
                    "returns": fn_meta.get("returns"),
                    "imports": parsed_data.get("imports"),
                    "calls": parsed_data.get("function_calls"),
                },
            })

        # Class chunks
        for class_name, class_meta in parsed_data.get("classes", {}).items():
            chunks.append({
                "type": "class",
                "name": class_name,
                "language": "python",
                "file": file_path,
                "content": extract_block(raw_code, class_name),
                "metadata": {
                    "bases": class_meta.get("bases"),
                    "methods": class_meta.get("methods"),
                    "imports": parsed_data.get("imports"),
                },
            })

    # -------------------------
    # JAVASCRIPT CHUNKING
    # -------------------------
    elif language == "javascript":
        # Function chunks
        for fn_name in parsed_data.get("functions", []):
            chunks.append({
                "type": "function",
                "name": fn_name,
                "language": "javascript",
                "file": file_path,
                "content": extract_block(raw_code, fn_name),
                "metadata": {
                    "imports": parsed_data.get("imports"),
                },
            })

        # Route chunks
        for route in parsed_data.get("routes", []):
            chunks.append({
                "type": "route",
                "name": f"{route['method']} {route['path']}",
                "language": "javascript",
                "file": file_path,
                "content": extract_route_block(raw_code, route["path"]),
                "metadata": {
                    "method": route["method"],
                    "path": route["path"],
                },
            })

    # -------------------------
    # FALLBACK FILE CHUNK
    # -------------------------
    if not chunks:
        chunks.append({
            "type": "file",
            "name": file_path,
            "language": language,
            "file": file_path,
            "content": raw_code[:2000],  # safety limit
            "metadata": {
                "imports": parsed_data.get("imports", []),
            },
        })

    return chunks

def extract_block(code: str, keyword: str, max_lines: int = 50) -> str:
    """
    Extract code block starting from keyword (best-effort).
    """
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if keyword in line:
            return "\n".join(lines[i:i + max_lines])
    return ""


def extract_route_block(code: str, route_path: str, max_lines: int = 30) -> str:
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if route_path in line:
            return "\n".join(lines[i:i + max_lines])
    return ""
