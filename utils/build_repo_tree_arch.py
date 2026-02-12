from pathlib import Path
import json

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
}

IGNORE_FILES_PREFIX = "."
FRONTEND_COMPONENT_EXT = {".tsx", ".jsx"}
BACKEND_ROUTE_KEYWORDS = {"router", "route", "app.get", "app.post"}
MODEL_KEYWORDS = {"schema", "model"}
SERVICE_KEYWORDS = {"service", "usecase", "logic"}
DB_KEYWORDS = {"mongoose", "prisma", "sequelize", "mongodb", "postgres"}

COMMON_DEPENDENCIES = {
    "react", "express", "mongoose", "redux", "jsonwebtoken",
    "jwt", "bcrypt", "axios", "tailwindcss",
    "next", "nestjs", "fastapi", "flask", "django"
}


def build_file_tree(path: Path):
    """
    Recursively build file tree in frontend-friendly format.
    """
    if path.is_file():
        return {
            "name": path.name,
            "type": "file",
            "ext": path.suffix.replace(".", "") if path.suffix else "",
        }

    children = []
    for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if child.name.startswith(IGNORE_FILES_PREFIX):
            continue
        if child.is_dir() and child.name in IGNORE_DIRS:
            continue

        children.append(build_file_tree(child))

    return {
        "name": path.name,
        "type": "folder",
        "children": children,
    }


def analyze_repo_architecture(repo_path: str) -> dict:
    repo = Path(repo_path)

    components = api_routes = models = services = 0
    frontend_entry = backend_entry = None
    detected_frontend = detected_backend = detected_db = False
    detected_dependencies = set()

    # -------------------------
    # package.json dependencies
    # -------------------------
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            deps = pkg.get("dependencies", {}) | pkg.get("devDependencies", {})
            for d in deps:
                if d.lower() in COMMON_DEPENDENCIES:
                    detected_dependencies.add(d.lower())
        except Exception:
            pass

    # -------------------------
    # requirements.txt (Python)
    # -------------------------
    req_file = repo / "requirements.txt"
    if req_file.exists():
        for line in req_file.read_text().splitlines():
            name = line.split("==")[0].lower()
            detected_dependencies.add(name)

    # -------------------------
    # Code scanning
    # -------------------------
    for file in repo.rglob("*"):
        if not file.is_file():
            continue

        name = file.name.lower()
        ext = file.suffix.lower()

        try:
            content = file.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue

        # Components
        if ext in FRONTEND_COMPONENT_EXT and "component" in content:
            components += 1
            detected_frontend = True

        # API Routes
        if any(k in content for k in BACKEND_ROUTE_KEYWORDS):
            api_routes += 1
            detected_backend = True

        # Models
        if any(k in name for k in MODEL_KEYWORDS):
            models += 1

        # Services
        if any(k in name for k in SERVICE_KEYWORDS):
            services += 1

        # DB detection
        if any(k in content for k in DB_KEYWORDS):
            detected_db = True

        # Dependency inference from imports
        for dep in COMMON_DEPENDENCIES:
            if f"from '{dep}'" in content or f'from "{dep}"' in content:
                detected_dependencies.add(dep)

        # Entry points
        if name in {"index.tsx", "main.tsx"}:
            frontend_entry = str(file.relative_to(repo))

        if name in {"index.ts", "server.ts", "app.ts"} and "express" in content:
            backend_entry = str(file.relative_to(repo))

    # -------------------------
    # Data flow inference
    # -------------------------
    data_flow = []
    if detected_frontend:
        data_flow.append({"name": "Frontend", "tech": "React"})
    if detected_backend:
        data_flow.append({"name": "API Layer", "tech": "Express"})
    if services:
        data_flow.append({"name": "Services", "tech": "Business Logic"})
    if detected_db:
        data_flow.append({"name": "Database", "tech": "MongoDB"})

    return {
        "stats": {
            "components": components,
            "api_routes": api_routes,
            "models": models,
            "services": services,
        },
        "data_flow": data_flow,
        "entry_points": [
            {"file": frontend_entry, "type": "frontend"} if frontend_entry else None,
            {"file": backend_entry, "type": "backend"} if backend_entry else None,
        ],
        "key_dependencies": sorted(detected_dependencies),
    }