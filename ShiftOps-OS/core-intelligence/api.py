from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import datetime
import json
import asyncio
import zipfile
import io
import shutil
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from intent_to_code.support.architecture_engine import ArchitectureEngine
from intent_to_code.support.architecture_memory import ArchitectureMemory
from intent_to_code.support.architecture_simulator import ArchitectureSimulator
from intent_to_code.validators.blueprint_validator import BlueprintValidator
from intent_to_code.support.architecture_diff import ArchitectureDiff
from intent_to_code.support.dsl_converter import DSLConverter
from intent_to_code.models.gemini_adapter import GeminiAdapter

app = FastAPI(title="ShiftOps-OS Core API")

# Ensure build directory exists
Path("build").mkdir(exist_ok=True)

# Mount build directory for previews
app.mount("/preview", StaticFiles(directory="build"), name="preview")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ArchitectureEngine()
memory = ArchitectureMemory()
validator = BlueprintValidator()
diff_engine = ArchitectureDiff()
gemini = GeminiAdapter()

class ChatRequest(BaseModel):
    message: str
    blueprint: Optional[Dict[str, Any]] = None

class SimulationRequest(BaseModel):
    blueprint: Dict[str, Any]
    scenario: str # failure, latency, throughput
    node_id: Optional[str] = None
    value: Optional[float] = 1.0

class ArchitectRequest(BaseModel):
    goal: str
    request: str
    base_dir: str = "build"
    image_path: Optional[str] = None

class EvolveRequest(BaseModel):
    snapshot: Dict[str, Any]
    request: str

class DiffRequest(BaseModel):
    baseline: Dict[str, Any]
    candidate: Dict[str, Any]

class ExportRequest(BaseModel):
    goal: str
    repo: Dict[str, str]

@app.get("/")
async def root():
    return {"status": "online", "message": "ShiftOps-OS Core API is active"}

@app.post("/ai/chat")
async def ai_chat(req: ChatRequest):
    try:
        context = ""
        if req.blueprint:
            dsl = DSLConverter.blueprint_to_dsl(req.blueprint)
            context = f"\nCurrent System Architecture (DSL):\n{dsl}\n"

        prompt = f"""
        Act as the ShiftOps-OS Senior Architect.
        Provide professional guidance on the following user request.
        {context}
        User Request: "{req.message}"
        
        If the user wants to change the architecture, suggest the specific components to add or remove.
        Keep it concise and engineering-focused.
        """
        
        response = gemini.generate_text(prompt)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Chat failed: {str(e)}")

@app.post("/diff")
async def diff(req: DiffRequest):
    try:
        diff_res = diff_engine.compare(req.baseline, req.candidate)
        return {
            "status": "success",
            "diff": diff_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Architecture diff failed: {str(e)}")

@app.post("/export")
async def export_project(req: ExportRequest):
    """
    Exports the virtual repo snapshot as a ZIP file.
    No disk writes required for the source files.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for path, content in req.repo.items():
            zip_file.writestr(path, content)
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={req.goal.replace(' ', '_')}.zip"}
    )

@app.get("/download")
async def download_project(goal: str):
    """
    Exporters the generated project as a ZIP file.
    """
    project_path = Path("build") / goal.replace(" ", "_")
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found. Build it first.")
    
    zip_path = Path("outputs") / f"{goal.replace(' ', '_')}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create zip
    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', project_path)
    
    return FileResponse(path=zip_path, filename=f"{goal}.zip", media_type='application/zip')

@app.get("/architect/stream")
async def stream_architect(goal: str, request: str):
    async def event_generator():
        for event in engine.run_search_cycle(goal, request):
            # Use default=str to handle non-serializable objects safely
            yield f"data: {json.dumps(event, default=str)}\n\n"
            await asyncio.sleep(0.1) 

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/architect")
async def architect(req: ArchitectRequest):
    try:
        base_path = Path(req.base_dir) / req.goal.replace(" ", "_")
        
        # Run the full cycle with safe handling
        try:
            result = engine.run_full_cycle(req.goal, req.request, base_dir=base_path)
        except Exception as e:
            # If full cycle fails (e.g. compilation), we still want to return the blueprint if it exists
            print(f"Full cycle warning: {str(e)}")
            result = []

        # Load the generated blueprint (it should exist even if compilation had issues)
        blueprint_path = base_path / "architecture_blueprint.json"
        blueprint = {}
        if blueprint_path.exists():
            with open(blueprint_path, "r") as f:
                blueprint = json.load(f)
            
            try:
                validator.validate_all(blueprint)
            except Exception as ve:
                print(f"Validation warning: {str(ve)}")
            
        # Find the dashboard_ui path in results to return to frontend
        preview_url = None
        for res in result:
            if isinstance(res, dict) and res.get("component") == "dashboard_ui":
                try:
                    # Extract the directory name from the absolute path
                    comp_path = Path(res["result"]["artifact"]["path"])
                    rel_path = comp_path.relative_to(Path("build"))
                    preview_url = f"http://localhost:8000/preview/{rel_path.as_posix()}/index.html"
                except Exception:
                    pass

        return {
            "status": "success",
            "blueprint": blueprint,
            "build_dir": str(base_path),
            "preview_url": preview_url,
            "compilation_status": "completed" if result else "failed_or_partial"
        }
    except Exception as e:
        print(f"Architecting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Architecting failed: {str(e)}")

@app.post("/architect/snapshot")
async def architect_snapshot(req: ArchitectRequest):
    try:
        snapshot = engine.generate_snapshot(req.goal, req.request, image_path=req.image_path)
        return {
            "status": "success",
            "snapshot": snapshot
        }
    except Exception as e:
        print(f"Snapshot generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Snapshot generation failed: {str(e)}")

@app.post("/architect/evolve")
async def architect_evolve(req: EvolveRequest):
    try:
        evolved_snapshot = engine.evolve_snapshot(req.snapshot, req.request)
        return {
            "status": "success",
            "snapshot": evolved_snapshot
        }
    except Exception as e:
        print(f"Evolution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evolution failed: {str(e)}")

@app.get("/patterns")
async def get_patterns():
    patterns = memory.load_patterns()
    return {"patterns": patterns}

@app.post("/simulate")
async def simulate(req: SimulationRequest):
    try:
        simulator = ArchitectureSimulator(req.blueprint)
        
        if req.scenario == "failure":
            if not req.node_id:
                raise HTTPException(status_code=400, detail="node_id required for failure scenario")
            res = simulator.simulate_node_failure(req.node_id)
        elif req.scenario == "latency":
            if not req.node_id:
                raise HTTPException(status_code=400, detail="node_id required for latency scenario")
            res = simulator.simulate_latency_spike(req.node_id, int(req.value or 100))
        elif req.scenario == "throughput":
            res = simulator.simulate_throughput_test(req.value or 1.5)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown scenario: {req.scenario}")
            
        return {
            "status": "success",
            "results": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
