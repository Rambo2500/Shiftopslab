import re
from pathlib import Path

def prepare_project(project_name: str, base_dir: Path = Path("build")) -> Path:
    """
    Creates a clean, non-conflicting build directory for an artifact.
    """
    base_dir.mkdir(exist_ok=True, parents=True)

    clean_name = re.sub(r"[^a-zA-Z0-9_]", "", project_name.replace(" ", "_")).lower()
    if not clean_name:
        clean_name = "artifact"

    project_dir = base_dir / clean_name

    counter = 1
    while project_dir.exists():
        project_dir = base_dir / f"{clean_name}_{counter}"
        counter += 1

    project_dir.mkdir(parents=True)
    return project_dir
