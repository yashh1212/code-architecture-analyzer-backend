import ast
from typing import Dict, List


class UniversalPythonParser(ast.NodeVisitor):
    def __init__(self):
        self.data = {
            "imports": set(),
            "from_imports": set(),
            "functions": {},
            "classes": {},
            "function_calls": set(),
            "assignments": set(),
            "decorators": set(),
        }

    # ---------- IMPORTS ----------
    def visit_Import(self, node):
        for alias in node.names:
            self.data["imports"].add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.data["from_imports"].add(node.module)
        self.generic_visit(node)

    # ---------- FUNCTIONS ----------
    def visit_FunctionDef(self, node):
        self.data["functions"][node.name] = {
            "args": [arg.arg for arg in node.args.args],
            "decorators": [self._get_name(d) for d in node.decorator_list],
            "returns": self._get_name(node.returns),
        }

        for d in node.decorator_list:
            self.data["decorators"].add(self._get_name(d))

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    # ---------- CLASSES ----------
    def visit_ClassDef(self, node):
        self.data["classes"][node.name] = {
            "bases": [self._get_name(b) for b in node.bases],
            "methods": [],
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.data["classes"][node.name]["methods"].append(item.name)

        self.generic_visit(node)

    # ---------- FUNCTION CALLS ----------
    def visit_Call(self, node):
        func_name = self._get_name(node.func)
        if func_name:
            self.data["function_calls"].add(func_name)
        self.generic_visit(node)

    # ---------- ASSIGNMENTS ----------
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.data["assignments"].add(target.id)
        self.generic_visit(node)

    # ---------- HELPERS ----------
    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None


def parse_python_code(code: str) -> Dict:
    tree = ast.parse(code)
    parser = UniversalPythonParser()
    parser.visit(tree)

    # Convert sets → sorted lists (JSON-safe)
    return {
        "imports": sorted(parser.data["imports"]),
        "from_imports": sorted(parser.data["from_imports"]),
        "functions": parser.data["functions"],
        "classes": parser.data["classes"],
        "function_calls": sorted(parser.data["function_calls"]),
        "assignments": sorted(parser.data["assignments"]),
        "decorators": sorted(parser.data["decorators"]),
    }
