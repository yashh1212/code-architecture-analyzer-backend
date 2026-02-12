"""
Optimized Repository Architecture Analyzer
Analyzes codebase structure, dependencies, and data flow
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional
import re


class RepoArchitectureAnalyzer:
    """Analyzes repository architecture and generates insights"""
    
    # Constants
    FRONTEND_COMPONENT_EXT = {'.jsx', '.tsx', '.vue', '.svelte'}
    FRONTEND_KEYWORDS = {'component', 'usestate', 'useeffect', 'props', 'render('}
    
    BACKEND_ROUTE_KEYWORDS = {
        'router.get', 'router.post', 'router.put', 'router.delete',
        'app.get', 'app.post', 'app.put', 'app.delete',
        '@app.route', '@router.route', 'fastapi', 'flask',
        'express.router', 'apicontroller'
    }
    
    MODEL_KEYWORDS = {'model', 'schema', 'entity'}
    SERVICE_KEYWORDS = {'service', 'repository', 'dao'}
    
    DB_KEYWORDS = {
        'mongoose', 'mongodb', 'sequelize', 'typeorm', 'prisma',
        'sqlalchemy', 'pymongo', 'pg', 'mysql', 'postgresql',
        'find(', 'findone', 'create(', 'update(', 'delete(',
        'collection.', 'db.collection'
    }
    
    COMMON_DEPENDENCIES = {
        # Frontend
        'react', 'vue', 'angular', 'svelte', 'next', 'nuxt',
        'redux', 'zustand', 'mobx', 'axios', 'fetch',
        
        # Backend
        'express', 'fastify', 'koa', 'nestjs', 'flask', 'django',
        'fastapi', 'spring', 'gin', 'fiber',
        
        # Database
        'mongoose', 'mongodb', 'sequelize', 'typeorm', 'prisma',
        'pg', 'mysql', 'sqlite3', 'redis',
        
        # Python
        'pandas', 'numpy', 'requests', 'sqlalchemy', 'pydantic'
    }
    
    # Directories to skip
    SKIP_DIRS = {
        'node_modules', 'venv', 'env', '.git', 'dist', 'build',
        '__pycache__', '.next', '.nuxt', 'coverage', 'out'
    }
    
    def __init__(self, repo_path: str):
        self.repo = Path(repo_path)
        if not self.repo.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        self.components = 0
        self.api_routes = 0
        self.models = 0
        self.services = 0
        self.frontend_entry = None
        self.backend_entry = None
        self.detected_frontend = False
        self.detected_backend = False
        self.detected_db = False
        self.detected_dependencies: Set[str] = set()
        self.frontend_tech = None
        self.backend_tech = None
        self.db_tech = None
    
    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        parts = path.parts
        return any(skip_dir in parts for skip_dir in self.SKIP_DIRS)
    
    def analyze_package_json(self) -> None:
        """Analyze package.json for dependencies"""
        package_json = self.repo / "package.json"
        if not package_json.exists():
            return
        
        try:
            pkg = json.loads(package_json.read_text(encoding='utf-8'))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            for dep_name in deps.keys():
                dep_lower = dep_name.lower()
                
                # Check exact matches and partial matches
                if dep_lower in self.COMMON_DEPENDENCIES:
                    self.detected_dependencies.add(dep_lower)
                
                # Detect frontend frameworks
                if dep_lower in {'react', 'react-dom'}:
                    self.frontend_tech = 'React'
                    self.detected_frontend = True
                elif dep_lower in {'vue', '@vue/cli'}:
                    self.frontend_tech = 'Vue'
                    self.detected_frontend = True
                elif dep_lower.startswith('@angular/'):
                    self.frontend_tech = 'Angular'
                    self.detected_frontend = True
                
                # Detect backend frameworks
                if dep_lower in {'express', 'fastify', 'koa'}:
                    self.backend_tech = dep_lower.capitalize()
                    self.detected_backend = True
                
                # Detect databases
                if dep_lower in {'mongoose', 'mongodb'}:
                    self.db_tech = 'MongoDB'
                    self.detected_db = True
                elif dep_lower in {'pg', 'postgresql'}:
                    self.db_tech = 'PostgreSQL'
                    self.detected_db = True
                elif dep_lower in {'mysql', 'mysql2'}:
                    self.db_tech = 'MySQL'
                    self.detected_db = True
                    
        except Exception as e:
            print(f"Warning: Could not parse package.json: {e}")
    
    def analyze_requirements_txt(self) -> None:
        """Analyze requirements.txt for Python dependencies"""
        req_file = self.repo / "requirements.txt"
        if not req_file.exists():
            return
        
        try:
            content = req_file.read_text(encoding='utf-8')
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract package name (before ==, >=, etc.)
                name = re.split(r'[=<>!]', line)[0].strip().lower()
                
                if name in self.COMMON_DEPENDENCIES:
                    self.detected_dependencies.add(name)
                
                # Detect frameworks
                if name in {'flask', 'django', 'fastapi'}:
                    self.backend_tech = name.capitalize()
                    self.detected_backend = True
                
                # Detect databases
                if name in {'pymongo', 'mongoengine'}:
                    self.db_tech = 'MongoDB'
                    self.detected_db = True
                elif name in {'sqlalchemy', 'psycopg2'}:
                    self.db_tech = 'PostgreSQL'
                    self.detected_db = True
                    
        except Exception as e:
            print(f"Warning: Could not parse requirements.txt: {e}")
    
    def analyze_file(self, file: Path) -> None:
        """Analyze individual file for patterns"""
        if self.should_skip(file):
            return
        
        name = file.name.lower()
        ext = file.suffix.lower()
        
        try:
            content = file.read_text(encoding='utf-8', errors='ignore').lower()
        except Exception:
            return
        
        # Frontend components
        if ext in self.FRONTEND_COMPONENT_EXT:
            if any(kw in content for kw in self.FRONTEND_KEYWORDS):
                self.components += 1
                self.detected_frontend = True
                
                # Detect React specifically
                if 'react' in content or 'usestate' in content:
                    self.frontend_tech = 'React'
        
        # API routes
        route_count = sum(1 for kw in self.BACKEND_ROUTE_KEYWORDS if kw in content)
        if route_count > 0:
            self.api_routes += route_count
            self.detected_backend = True
            
            # Detect backend framework
            if 'express' in content and not self.backend_tech:
                self.backend_tech = 'Express'
            elif 'fastapi' in content and not self.backend_tech:
                self.backend_tech = 'FastAPI'
            elif 'flask' in content and not self.backend_tech:
                self.backend_tech = 'Flask'
        
        # Models (be more specific)
        if any(kw in name for kw in self.MODEL_KEYWORDS):
            # Check if it actually defines models
            if 'schema' in content or 'model' in content or 'class' in content:
                self.models += 1
        
        # Services
        if any(kw in name for kw in self.SERVICE_KEYWORDS):
            # Check if it actually contains service logic
            if 'class' in content or 'function' in content or 'export' in content:
                self.services += 1
        
        # Database detection
        db_matches = sum(1 for kw in self.DB_KEYWORDS if kw in content)
        if db_matches > 0:
            self.detected_db = True
            
            # Detect specific database
            if 'mongoose' in content or 'mongodb' in content:
                self.db_tech = 'MongoDB'
            elif 'sequelize' in content or 'pg' in content:
                self.db_tech = 'PostgreSQL'
            elif 'sqlalchemy' in content:
                self.db_tech = 'SQL Database'
        
        # Import detection for dependencies
        for dep in self.COMMON_DEPENDENCIES:
            patterns = [
                f"import {dep}",
                f"from '{dep}'",
                f'from "{dep}"',
                f"import {{ }} from '{dep}'",
                f"require('{dep}')",
                f'require("{dep}")',
                f"import {dep} from",
            ]
            if any(p in content for p in patterns):
                self.detected_dependencies.add(dep)
        
        # Entry points
        if name in {'index.tsx', 'main.tsx', 'app.tsx', 'index.jsx', 'main.jsx'}:
            if 'reactdom' in content or 'render' in content:
                self.frontend_entry = str(file.relative_to(self.repo))
        
        if name in {'index.ts', 'server.ts', 'app.ts', 'main.ts', 'index.js', 'server.js'}:
            if any(kw in content for kw in ['express', 'fastapi', 'flask', 'app.listen']):
                self.backend_entry = str(file.relative_to(self.repo))
    
    def scan_repository(self) -> None:
        """Scan all files in the repository"""
        # First, analyze dependency files
        self.analyze_package_json()
        self.analyze_requirements_txt()
        
        # Then scan source files
        for file in self.repo.rglob("*"):
            if file.is_file() and not self.should_skip(file):
                self.analyze_file(file)
    
    def build_data_flow(self) -> List[Dict[str, str]]:
        """Build data flow diagram"""
        data_flow = []
        
        if self.detected_frontend:
            tech = self.frontend_tech or "React/Vue"
            data_flow.append({"name": "Frontend", "tech": tech})
        
        if self.detected_backend:
            tech = self.backend_tech or "Express/FastAPI"
            data_flow.append({"name": "API Layer", "tech": tech})
        
        if self.services > 0:
            data_flow.append({"name": "Business Logic", "tech": f"{self.services} Services"})
        
        if self.models > 0:
            data_flow.append({"name": "Data Models", "tech": f"{self.models} Models"})
        
        if self.detected_db:
            tech = self.db_tech or "Database"
            data_flow.append({"name": "Database", "tech": tech})
        
        return data_flow
    
    def get_results(self) -> Dict:
        """Get analysis results"""
        entry_points = []
        if self.frontend_entry:
            entry_points.append({"file": self.frontend_entry, "type": "frontend"})
        if self.backend_entry:
            entry_points.append({"file": self.backend_entry, "type": "backend"})
        
        return {
            "stats": {
                "components": self.components,
                "api_routes": self.api_routes,
                "models": self.models,
                "services": self.services,
            },
            "architecture": {
                "frontend": self.frontend_tech if self.detected_frontend else None,
                "backend": self.backend_tech if self.detected_backend else None,
                "database": self.db_tech if self.detected_db else None,
            },
            "data_flow": self.build_data_flow(),
            "entry_points": entry_points,
            "key_dependencies": sorted(self.detected_dependencies),
        }


def analyze_repo_architecture(repo_path: str) -> dict:
    """
    Analyze repository architecture and return comprehensive insights.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        Dictionary containing stats, architecture info, data flow, and dependencies
    """
    analyzer = RepoArchitectureAnalyzer(repo_path)
    analyzer.scan_repository()
    return analyzer.get_results()


