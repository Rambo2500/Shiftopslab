from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from workforce_engine.database import Base, engine
from workforce_engine.routes import employee_routes, site_routes
from workforce_engine.routes import schedule_routes
from workforce_engine.routes import assignment_routes
from workforce_engine.routes import shift_routes
from workforce_engine.routes import experience_routes

import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("workforce_engine")

app = FastAPI(
    title="ShiftOpsPro Workforce Engine",
    version="0.1"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
# Base.metadata.create_all(bind=engine) (Handled by Alembic)

# Include routers
app.include_router(site_routes.router)
app.include_router(employee_routes.router)
app.include_router(schedule_routes.router)
app.include_router(assignment_routes.router)
app.include_router(shift_routes.router)
app.include_router(experience_routes.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error Catch: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"status": "engine online"}
