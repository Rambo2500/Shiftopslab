"""
Compiler execution path (deterministic).

Selects and runs artifact compilers from a registry.
Uses Jinja2 templates for code generation.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from intent_to_code.support.build_manager import prepare_project
from intent_to_code.support.bootstrap import bootstrap_project

# Path to templates relative to this file
TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def compile_intent(intent: dict, base_dir: Path = Path("build")) -> dict:
    """
    Execute deterministic code generation when requested.
    """
    payload = intent.get("payload") or {}
    goal = intent.get("goal") or payload.get("goal") or "unnamed_project"
    inputs = intent.get("inputs") or payload.get("inputs") or []
    constraints = intent.get("constraints") or payload.get("constraints") or []
    system_context = intent.get("system_context") or {}
    outputs = intent.get("outputs", {})
    code_request = outputs.get("code", {})

    result = {
        "canonical": {
            "goal": goal,
            "inputs": inputs,
            "constraints": constraints,
            "system_context": system_context
        },
        "issues": []
    }

    if code_request.get("enabled") is True:
        code_type = code_request.get("type", "function")
        
        # Dispatch to registry
        if code_type in COMPILER_REGISTRY:
            artifact_result = COMPILER_REGISTRY[code_type](goal, inputs, base_dir, system_context)
            result["artifact"] = artifact_result
            
            # Bootstrap Phase 3 Toolchain
            if code_request.get("bootstrap_env") is True:
                bootstrap_project(Path(artifact_result["path"]))
                artifact_result["bootstrapped"] = True
                
        elif code_type == "function":
            result["python"] = _generate_function(inputs)
        else:
            result["issues"].append(f"Unsupported code type: {code_type}")

    return result


def _generate_function(inputs: list) -> str:
    return f"""
def generated_function({", ".join(inputs)}):
    # Mirrors intent exactly.
    # No assumptions were made.
    pass
""".strip()


from intent_to_code.models.gemini_adapter import GeminiAdapter
gemini = GeminiAdapter()

def generate_fastapi_service(goal: str, inputs: list, base_dir: Path = Path("build"), system_context: dict = None) -> dict:
    project_dir = prepare_project(goal, base_dir)

    # INFERENCE BRANCH: Use LLM to write the service logic
    prompt = f"""
    Write a production-ready FastAPI main.py for a service named '{goal}'.
    System Context: {json.dumps(system_context)}
    
    Requirements:
    1. Implement endpoints relevant to '{goal}'.
    2. Mock the behavior of connecting to its dependencies: {", ".join(system_context.get("depends_on", [])) if system_context else "None"}.
    3. Include Pydantic models for data structures.
    
    Return ONLY the python code.
    """
    try:
        main_code = gemini.generate_text(prompt)
        # Cleanup markdown
        main_code = main_code.replace("```python", "").replace("```", "").strip()
    except Exception:
        template = env.get_template("fastapi/main.py.jinja")
        main_code = template.render(goal=goal, inputs=inputs, system_context=system_context)

    (project_dir / "main.py").write_text(main_code)
    requirements_content = "fastapi\nuvicorn\nrequests\npydantic\n"
    (project_dir / "requirements.txt").write_text(requirements_content)

    # 3. Metadata
    metadata = {
        "artifact_type": "fastapi_service",
        "goal": goal,
        "template_version": "2.1",
        "system_context": system_context,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    metadata_json = json.dumps(metadata, indent=2)
    (project_dir / "artifact.json").write_text(metadata_json)

    repo = {
        "main.py": main_code,
        "requirements.txt": requirements_content,
        "artifact.json": metadata_json
    }

    # 4. Dockerfile (Optional but professional)
    dockerfile_content = "FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
    (project_dir / "Dockerfile").write_text(dockerfile_content)
    repo["Dockerfile"] = dockerfile_content

    return {
        "type": "fastapi_service",
        "path": str(project_dir),
        "files": list(repo.keys()),
        "repo": repo
    }

def generate_react_dashboard(goal: str, inputs: list, base_dir: Path = Path("build"), system_context: dict = None) -> dict:
    """
    Generates a top-of-the-line React + Tailwind dashboard project.
    """
    project_dir = prepare_project(goal, base_dir)
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    repo = {}

    # 1. Configuration Files
    package_json = env.get_template("dashboard/package.json.jinja").render()
    (project_dir / "package.json").write_text(package_json)
    repo["package.json"] = package_json

    index_html = env.get_template("dashboard/index.html.jinja").render(goal=goal)
    (project_dir / "index.html").write_text(index_html)
    repo["index.html"] = index_html

    vite_config = env.get_template("dashboard/vite.config.js.jinja").render()
    (project_dir / "vite.config.js").write_text(vite_config)
    repo["vite.config.js"] = vite_config

    tailwind_config = env.get_template("dashboard/tailwind.config.js.jinja").render()
    (project_dir / "tailwind.config.js").write_text(tailwind_config)
    repo["tailwind.config.js"] = tailwind_config

    postcss_config = env.get_template("dashboard/postcss.config.js.jinja").render()
    (project_dir / "postcss.config.js").write_text(postcss_config)
    repo["postcss.config.js"] = postcss_config

    # 2. Source Files
    main_jsx = env.get_template("dashboard/main.jsx.jinja").render()
    (src_dir / "main.jsx").write_text(main_jsx)
    repo["src/main.jsx"] = main_jsx

    index_css = env.get_template("dashboard/index.css.jinja").render()
    (src_dir / "index.css").write_text(index_css)
    repo["src/index.css"] = index_css

    app_jsx = env.get_template("dashboard/App.jsx.jinja").render(goal=goal, inputs=inputs, system_context=system_context)
    (src_dir / "App.jsx").write_text(app_jsx)
    repo["src/App.jsx"] = app_jsx

    # 3. Metadata
    metadata = {
        "artifact_type": "react_dashboard",
        "goal": goal,
        "template_version": "2.0",
        "system_context": system_context,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    metadata_json = json.dumps(metadata, indent=2)
    (project_dir / "artifact.json").write_text(metadata_json)
    repo["artifact.json"] = metadata_json

    return {
        "type": "react_dashboard",
        "path": str(project_dir),
        "files": list(repo.keys()),
        "repo": repo
    }



def orchestrate_full_system(system_intent: dict, base_dir: Path = Path("build")) -> dict:
    """
    Orchestrates the build of a multi-service system into a single project structure.
    """
    goal = system_intent.get("goal", "full_system")
    project_root = base_dir / goal.replace(" ", "_")
    project_root.mkdir(parents=True, exist_ok=True)

    system_outputs = system_intent.get("outputs", {}).get("system", {})
    components = system_outputs.get("components", [])

    build_results = []

    # 1. Compile individual components
    for component in components:
        comp_dir = project_root / "services" / component["name"]
        component_intent = {
            "goal": component["name"],
            "outputs": {"code": {"enabled": True, "type": component["type"]}},
            "system_context": {"parent_system": goal, "component": component}
        }
        res = compile_intent(component_intent, base_dir=comp_dir)
        build_results.append({
            "name": component["name"],
            "type": component["type"],
            "result": res
        })

    # 2. Generate Docker Compose for orchestration
    docker_compose = {
        "version": "3.8",
        "services": {}
    }
    for res in build_results:
        if "artifact" in res["result"]:
            service_name = res["name"].lower().replace(" ", "_").replace("-", "_")
            docker_compose["services"][service_name] = {
                "build": f"./services/{res['name']}",
                "ports": ["8000:8000"] if "fastapi" in res["type"] else []
            }

    (project_root / "docker-compose.yml").write_text(json.dumps(docker_compose, indent=2))

    return {
        "goal": goal,
        "path": str(project_root),
        "components": build_results,
        "orchestration": "docker-compose.yml"
    }


def generate_generic_artifact(goal: str, inputs: list, artifact_type: str, base_dir: Path = Path("build"), system_context: dict = None) -> dict:
    project_dir = prepare_project(f"{goal}_{artifact_type}", base_dir)

    # INFERENCE BRANCH: Use LLM to write the service logic
    prompt = f"""
    Write a production-ready Python main.py for a service named '{goal}' of type '{artifact_type}'.
    System Context: {json.dumps(system_context)}
    
    Requirements:
    1. Implement logic relevant to '{goal}' and '{artifact_type}'.
    2. Mock the behavior of interacting with its dependencies: {", ".join(system_context.get("depends_on", [])) if system_context else "None"}.
    
    Return ONLY the python code.
    """
    try:
        main_py_content = gemini.generate_text(prompt)
        main_py_content = main_py_content.replace("```python", "").replace("```", "").strip()
    except Exception:
        main_py_content = f"# {artifact_type} for {goal}\n# System Context: {system_context}\nimport os\n\ndef main():\n    print('Running {goal}...')\n\nif __name__ == '__main__':\n    main()\n"

    (project_dir / "main.py").write_text(main_py_content)
    
    requirements_content = "requests\npydantic\n"
    (project_dir / "requirements.txt").write_text(requirements_content)

    # Phase 3: Artifact metadata
    metadata = {
        "artifact_type": artifact_type,
        "goal": goal,
        "template_version": "1.0",
        "system_context": system_context,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    metadata_json = json.dumps(metadata, indent=2)
    (project_dir / "artifact.json").write_text(metadata_json)

    repo = {
        "main.py": main_py_content,
        "requirements.txt": requirements_content,
        "artifact.json": metadata_json
    }

    return {
        "type": artifact_type,
        "path": str(project_dir),
        "files": list(repo.keys()),
        "repo": repo
    }



# Compiler Registry
COMPILER_REGISTRY = {
    "web_api_generator": generate_fastapi_service,
    "ui_generator": generate_react_dashboard,
    "compute_generator": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "compute_service", b, s),
    "transport_generator": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "transport_service", b, s),
    "storage_generator": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "storage_service", b, s),
    "reasoning_generator": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "reasoning_service", b, s),
    "control_generator": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "control_service", b, s),
    "presentation_generator": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "presentation_service", b, s),
    # Maintain old aliases for backward compatibility if needed
    "fastapi_service": generate_fastapi_service,
    "dashboard": generate_react_dashboard,
    "worker_service": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "worker_service", b, s),
    "analytics_service": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "analytics_service", b, s),
    "ai_reasoning_service": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "ai_reasoning_service", b, s),
    "report_service": lambda g, i, b=Path("build"), s=None: generate_generic_artifact(g, i, "report_service", b, s),
}