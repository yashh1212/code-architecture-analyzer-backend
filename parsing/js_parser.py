import re
from typing import Dict, List, Set


# ---------- REGEX PATTERNS ----------

FUNCTION_DECLARATION = re.compile(
    r"""
    function\s+(?P<name>[a-zA-Z_$][\w$]*)\s*\(
    """,
    re.VERBOSE,
)

FUNCTION_EXPRESSION = re.compile(
    r"""
    (?P<name>[a-zA-Z_$][\w$]*)\s*=\s*function\s*\(
    """,
    re.VERBOSE,
)

ARROW_FUNCTION = re.compile(
    r"""
    (?:(?:const|let|var)\s+)?
    (?P<name>[a-zA-Z_$][\w$]*)\s*=\s*
    \(?.*?\)?\s*=>
    """,
    re.VERBOSE,
)

CLASS_DECLARATION = re.compile(
    r"""
    class\s+(?P<name>[a-zA-Z_$][\w$]*)
    """,
    re.VERBOSE,
)

ES_IMPORT = re.compile(
    r"""
    import\s+(?:[\s\S]+?\s+from\s+)?["'](?P<module>[^"']+)["']
    """,
    re.VERBOSE,
)

COMMONJS_IMPORT = re.compile(
    r"""
    require\(\s*["'](?P<module>[^"']+)["']\s*\)
    """,
    re.VERBOSE,
)

# Express / Router routes
ROUTE_PATTERN = re.compile(
    r"""
    (?:app|router)\.
    (?P<method>get|post|put|delete|patch|options|head)\s*
    \(\s*["'](?P<path>[^"']+)["']
    """,
    re.VERBOSE | re.IGNORECASE,
)


# ---------- PARSER ----------

def parse_js(code: str) -> Dict:
    functions: Set[str] = set()
    classes: Set[str] = set()
    imports: Set[str] = set()
    routes: List[Dict] = []

    for match in FUNCTION_DECLARATION.finditer(code):
        functions.add(match.group("name"))

    for match in FUNCTION_EXPRESSION.finditer(code):
        functions.add(match.group("name"))

    for match in ARROW_FUNCTION.finditer(code):
        functions.add(match.group("name"))

    for match in CLASS_DECLARATION.finditer(code):
        classes.add(match.group("name"))

    for match in ES_IMPORT.finditer(code):
        imports.add(match.group("module"))

    for match in COMMONJS_IMPORT.finditer(code):
        imports.add(match.group("module"))

    for match in ROUTE_PATTERN.finditer(code):
        routes.append(
            {
                "method": match.group("method").upper(),
                "path": match.group("path"),
            }
        )

    return {
        "functions": sorted(functions),
        "classes": sorted(classes),
        "imports": sorted(imports),
        "routes": routes,
    }
