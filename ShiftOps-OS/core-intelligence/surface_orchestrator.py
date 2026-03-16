import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from intent_to_code.support.architecture_engine import ArchitectureEngine

app = FastAPI()
engine = ArchitectureEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SurfaceRequest(BaseModel):
    prompt: str
    image_path: str = None

@app.post("/project")
async def project_surface(request: SurfaceRequest):
    """
    The Deep Surface Projector.
    Uses the full ArchitectureEngine to synthesize domain-aware surfaces.
    """
    try:
        # Generate a full architectural snapshot including surface manifest
        snapshot = engine.generate_snapshot(
            goal="Projected_Surface",
            user_request=request.prompt,
            image_path=request.image_path
        )
        
        # The UI expects the manifest part of the snapshot
        manifest = snapshot.get("surface_manifest", {})
        
        # Inject domain data into the manifest for the UI to use in clamping
        manifest["domain_data"] = {
            "archetype": snapshot.get("domain_archetype"),
            "kpis": snapshot.get("diagnostics", {}).get("kpis", []),
            "incidents": snapshot.get("diagnostics", {}).get("incidents", []) # DomainScout research
        }
        
        return manifest
    except Exception as e:
        print(f"Deep Projection Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
