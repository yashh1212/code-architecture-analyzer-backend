"""
Repository Dependency Analyzer
Analyzes file dependencies and creates a dependency graph similar to the image
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict


class DependencyNode:
    """Represents a file/module with its dependencies"""
    
    def __init__(self, name: str, file_path: str, node_type: str):
        self.name = name
        self.file_path = file_path
        self.node_type = node_type  
        self.depends_on: Set[str] = set()
        self.used_by: Set[str] = set()
        self.imports: List[str] = []
    
    def to_dict(self, camel_case: bool = False) -> Dict:
        if camel_case:
            return {
                "name": self.name,
                "type": self.node_type,
                "dependsOn": sorted(list(self.depends_on)),
                "dependedBy": sorted(list(self.used_by)),
            }
        else:
            return {
                "name": self.name,
                "type": self.node_type,
                "file_path": self.file_path,
                "depends_on": sorted(list(self.depends_on)),
                "used_by": sorted(list(self.used_by)),
                "depends_on_count": len(self.depends_on),
                "used_by_count": len(self.used_by)
            }


class RepoDependencyAnalyzer:
    """Analyzes repository dependencies and creates a dependency graph"""
    
    # File type patterns
    TYPE_PATTERNS = {
        'service': ['service.ts', 'service.js', 'service.py'],
        'model': ['model.ts', 'model.js', 'model.py', 'schema.ts', 'schema.js'],
        'controller': ['controller.ts', 'controller.js', 'controller.py'],
        'component': ['.tsx', '.jsx', '.vue', '.svelte'],
        'middleware': ['middleware.ts', 'middleware.js', 'middleware.py'],
        'util': ['util.ts', 'util.js', 'utils.ts', 'utils.js', 'helper.ts', 'helper.js'],
        'config': ['config.ts', 'config.js', 'config.py'],
        'route': ['route.ts', 'routes.ts', 'router.ts'],
    }
    
    # Directories to skip
    SKIP_DIRS = {
        'node_modules', 'venv', 'env', '.git', 'dist', 'build',
        '__pycache__', '.next', '.nuxt', 'coverage', 'out', 'target'
    }
    
    # Import patterns for different languages
    IMPORT_PATTERNS = {
        'typescript': [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\([\'"]([^\'"]+)[\'"]\)',
        ],
        'javascript': [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
        ],
        'python': [
            r'from\s+([^\s]+)\s+import',
            r'import\s+([^\s]+)',
        ]
    }
    
    def __init__(self, repo_path: str):
        self.repo = Path(repo_path)
        if not self.repo.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        self.nodes: Dict[str, DependencyNode] = {}
        self.file_map: Dict[str, str] = {}  # file_path -> node_name
    
    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        parts = path.parts
        return any(skip_dir in parts for skip_dir in self.SKIP_DIRS)
    
    def determine_type(self, file_path: Path) -> str:
        """Determine the type of file based on patterns"""
        file_name = file_path.name.lower()
        
        for node_type, patterns in self.TYPE_PATTERNS.items():
            for pattern in patterns:
                if file_name.endswith(pattern):
                    return node_type
        
        return 'file'
    
    def extract_class_or_export_name(self, content: str, file_path: Path) -> Optional[str]:
        """Extract the main class or export name from file content"""
        
        # Try to find class name
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match:
            return class_match.group(1)
        
        # Try to find export default name
        export_match = re.search(r'export\s+default\s+(\w+)', content)
        if export_match:
            return export_match.group(1)
        
        # Try to find named export
        export_match = re.search(r'export\s+(?:class|function|const)\s+(\w+)', content)
        if export_match:
            return export_match.group(1)
        
        # Fallback to file name
        return file_path.stem
    
    def extract_imports(self, content: str, file_path: Path) -> List[str]:
        """Extract all import statements from file content"""
        imports = []
        
        # Determine language
        ext = file_path.suffix.lower()
        if ext in {'.ts', '.tsx', '.js', '.jsx'}:
            patterns = self.IMPORT_PATTERNS['typescript']
        elif ext == '.py':
            patterns = self.IMPORT_PATTERNS['python']
        else:
            return imports
        
        # Extract imports
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                import_path = match.group(1)
                
                # Skip external packages (without relative paths)
                if import_path.startswith('.') or import_path.startswith('/'):
                    imports.append(import_path)
        
        return imports
    
    def resolve_import_path(self, import_path: str, from_file: Path) -> Optional[Path]:
        """Resolve relative import path to actual file path"""
        
        # Handle relative imports
        if import_path.startswith('.'):
            base_dir = from_file.parent
            resolved = (base_dir / import_path).resolve()
            
            # Try different extensions
            extensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '']
            for ext in extensions:
                test_path = resolved.with_suffix(ext)
                if test_path.exists() and test_path.is_file():
                    return test_path
                
                # Try index files
                if resolved.is_dir():
                    for index_name in ['index.ts', 'index.tsx', 'index.js', 'index.jsx', '__init__.py']:
                        index_path = resolved / index_name
                        if index_path.exists():
                            return index_path
        
        return None
    
    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single file and extract its dependencies"""
        
        if self.should_skip(file_path):
            return
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return
        
        # Extract node name
        node_name = self.extract_class_or_export_name(content, file_path)
        if not node_name:
            return
        
        # Determine type
        node_type = self.determine_type(file_path)
        
        # Create or get node
        if node_name not in self.nodes:
            self.nodes[node_name] = DependencyNode(
                name=node_name,
                file_path=str(file_path.relative_to(self.repo)),
                node_type=node_type
            )
        
        node = self.nodes[node_name]
        self.file_map[str(file_path)] = node_name
        
        # Extract imports
        imports = self.extract_imports(content, file_path)
        node.imports = imports
    
    def build_dependency_graph(self) -> None:
        """Build the dependency graph by resolving imports"""
        
        for node_name, node in self.nodes.items():
            file_path = self.repo / node.file_path
            
            for import_path in node.imports:
                # Resolve import to actual file
                resolved_path = self.resolve_import_path(import_path, file_path)
                
                if resolved_path and str(resolved_path) in self.file_map:
                    dependency_name = self.file_map[str(resolved_path)]
                    
                    # Add dependency relationship
                    node.depends_on.add(dependency_name)
                    
                    # Add reverse relationship
                    if dependency_name in self.nodes:
                        self.nodes[dependency_name].used_by.add(node_name)
    
    def scan_repository(self) -> None:
        """Scan all files in the repository"""
        
        # Supported extensions
        extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.vue', '.svelte'}
        
        for file_path in self.repo.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                if not self.should_skip(file_path):
                    self.analyze_file(file_path)
        
        # Build dependency graph
        self.build_dependency_graph()
    
    def get_results(self, camel_case: bool = False) -> Dict:
        """Get analysis results in the format similar to the image"""
        
        nodes_list = []
        
        for node_name, node in sorted(self.nodes.items()):
            nodes_list.append(node.to_dict(camel_case=camel_case))
        
        # Calculate statistics
        total_nodes = len(self.nodes)
        nodes_with_deps = sum(1 for n in self.nodes.values() if n.depends_on)
        nodes_used = sum(1 for n in self.nodes.values() if n.used_by)
        
        # Type distribution
        type_distribution = defaultdict(int)
        for node in self.nodes.values():
            type_distribution[node.node_type] += 1
        
        if camel_case:
            return nodes_list  # Just return the array for TypeScript
        
        return {
            "nodes": nodes_list,
            "statistics": {
                "total_nodes": total_nodes,
                "nodes_with_dependencies": nodes_with_deps,
                "nodes_being_used": nodes_used,
                "type_distribution": dict(type_distribution)
            },
            "graph_data": self._generate_graph_data()
        }
    
    def _generate_graph_data(self) -> Dict:
        """Generate graph data for visualization"""
        
        nodes = []
        edges = []
        
        for node_name, node in self.nodes.items():
            nodes.append({
                "id": node_name,
                "label": node_name,
                "type": node.node_type,
                "group": node.node_type
            })
            
            for dependency in node.depends_on:
                edges.append({
                    "from": node_name,
                    "to": dependency,
                    "label": "depends on"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_formatted_output(self) -> str:
        """Get formatted text output similar to the image"""
        
        output_lines = []
        
        for node_name, node in sorted(self.nodes.items()):
            output_lines.append(f"\n{node_name}")
            output_lines.append(f"  {node.node_type}")
            
            # Depends on
            if node.depends_on:
                output_lines.append(f"\n  → Depends on ({len(node.depends_on)})")
                deps = "  " + "  ".join(sorted(node.depends_on))
                output_lines.append(deps)
            else:
                output_lines.append(f"\n  → Depends on (0)")
                output_lines.append("  None")
            
            # Used by
            if node.used_by:
                output_lines.append(f"\n  ← Used by ({len(node.used_by)})")
                users = "  " + "  ".join(sorted(node.used_by))
                output_lines.append(users)
            else:
                output_lines.append(f"\n  ← Used by (0)")
                output_lines.append("  None")
            
            output_lines.append("\n" + "-" * 80)
        
        return "\n".join(output_lines)


def analyze_repo_dependencies(repo_path: str, camel_case: bool = False) -> Dict:
    """
    Analyze repository dependencies and return dependency graph
    
    Args:
        repo_path: Path to the repository root
        camel_case: If True, returns data with camelCase keys (dependsOn, dependedBy)
                   If False, returns snake_case keys (depends_on, used_by)
        
    Returns:
        Dictionary containing nodes with their dependencies and usage information
        If camel_case=True, returns just the array of dependencies
    """
    analyzer = RepoDependencyAnalyzer(repo_path)
    analyzer.scan_repository()
    return analyzer.get_results(camel_case=camel_case)
