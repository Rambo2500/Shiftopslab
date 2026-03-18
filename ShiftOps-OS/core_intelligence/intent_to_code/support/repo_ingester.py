import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from intent_to_code.support.system_graph import SystemGraph, SystemNode

class RepoIngester:
    """
    The 'Eyes' of ShiftOps-OS.
    Scans an existing repository and transpiles it into a SystemGraph.
    This allows the engine to 'Consult' on existing codebases.
    """

    def ingest(self, repo_path: str, goal: str = None) -> SystemGraph:
        path = Path(repo_path)
        if not path.exists():
            raise Exception(f"Repo path does not exist: {repo_path}")

        # 1. Extract Intent from README if available
        intent_summary = self._extract_readme_intent(path)
        graph_goal = goal or intent_summary or path.name
        
        graph = SystemGraph(goal=graph_goal)

        # 2. Map Services/Components
        # Heuristic: Folders in 'services/' or top-level folders with 'main.py' or 'Dockerfile'
        potential_services = []
        
        # Check 'services' folder
        services_dir = path / "services"
        if services_dir.exists():
            for d in services_dir.iterdir():
                if d.is_dir():
                    potential_services.append(d)
        
        # Check top-level
        for d in path.iterdir():
            if d.is_dir() and d.name not in ["venv", ".git", "__pycache__", "services"]:
                if (d / "main.py").exists() or (d / "Dockerfile").exists() or (d / "requirements.txt").exists():
                    potential_services.append(d)

        # 3. Create Nodes
        for s_path in potential_services:
            node = self._parse_service_node(s_path)
            graph.add_node(node)

        # 4. Infer Dependencies (Very basic heuristic for now)
        # Look for service names in requirements.txt or main.py (e.g. requests to other services)
        self._infer_dependencies(graph, potential_services)

        return graph

    def _extract_readme_intent(self, path: Path) -> Optional[str]:
        readme = path / "README.md"
        if readme.exists():
            content = readme.read_text()
            # Get the first line or first paragraph
            lines = content.split("\n")
            for line in lines:
                clean = line.strip("# ")
                if clean:
                    return clean
        return None

    def _parse_service_node(self, service_path: Path) -> SystemNode:
        name = service_path.name
        
        # Try to find description in a local README or artifact.json
        description = f"Existing service found at {service_path.name}"
        artifact_json = service_path / "artifact.json"
        if artifact_json.exists():
            try:
                data = json.loads(artifact_json.read_text())
                description = data.get("description", description)
            except:
                pass

        # Determine type
        s_type = "fastapi_service"
        if (service_path / "package.json").exists():
            s_type = "dashboard"
        elif "worker" in name.lower():
            s_type = "worker_service"

        return SystemNode(
            name=name,
            type=s_type,
            description=description,
            depends_on=[]
        )

    def _infer_dependencies(self, graph: SystemGraph, service_paths: List[Path]):
        service_names = {p.name for p in service_paths}
        
        for p in service_paths:
            node = graph.nodes.get(p.name)
            if not node: continue
            
            # Scan main.py for service name mentions
            main_py = p / "main.py"
            if main_py.exists():
                content = main_py.read_text().lower()
                for other in service_names:
                    if other != p.name and other.lower() in content:
                        node.depends_on.append(other)
            
            # Scan docker-compose if at root
            root_compose = p.parent / "docker-compose.yml"
            if root_compose.exists():
                content = root_compose.read_text().lower()
                # (Simple substring check for now)
                if p.name.lower() in content:
                    # This is complex to parse accurately without a yaml lib, 
                    # but we can look for 'depends_on' blocks
                    pass
