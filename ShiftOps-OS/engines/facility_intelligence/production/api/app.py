from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import os
from datetime import datetime

# Import validators
from validators.validate_orders import validate_orders
from validators.validate_shipments import validate_shipments
from validators.validate_schedule import validate_schedule
from validators.validate_work_orders import validate_work_orders
from validators.validate_receipts import validate_receipts

app = FastAPI(title="Bakery Ops Engine API")

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data_raw")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

FILE_MAP = {
    "orders": ("oasis_orders.csv", validate_orders),
    "shipments": ("wms_shipments.csv", validate_shipments),
    "schedule": ("production_schedule.csv", validate_schedule),
    "work_orders": ("production_work_orders.csv", validate_work_orders),
    "receipts": ("work_order_reconciliation.csv", validate_receipts)
}

@app.get("/status")
def get_status():
    status = {}
    for key, (filename, _) in FILE_MAP.items():
        status[key] = (UPLOAD_DIR / filename).exists()
    return status

@app.post("/upload/{file_type}")
async def upload_file(file_type: str, file: UploadFile = File(...)):
    if file_type not in FILE_MAP:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    filename, validator = FILE_MAP[file_type]
    file_path = UPLOAD_DIR / filename
    
    # Read file to validate
    content = await file.read()
    try:
        df = pd.read_csv(pd.io.common.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    
    validation = validator(df)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["message"])
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
        
    return {
        "status": "success", 
        "message": f"{file_type} uploaded and validated",
        "rows": len(df),
        "warnings": validation.get("warnings", [])
    }

@app.post("/api/run")
def run_engine_api():
    import sys
    sys.path.append(os.getcwd())
    from main import run_pipeline
    try:
        run_pipeline()
        return {"status": "success", "message": "Engine run complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/truth")
def get_truth():
    truth_path = OUTPUT_DIR / "data" / "truth_table.csv"
    if not truth_path.exists():
        raise HTTPException(status_code=404, detail="Truth table not found. Run the engine first.")
    
    df = pd.read_csv(truth_path)
    # Convert dates/times to strings for JSON
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ["date", "time", "scheduled"]):
            df[col] = df[col].astype(str)
            
    return df.to_dict(orient="records")

@app.get("/api/summary")
def get_summary():
    truth_path = OUTPUT_DIR / "data" / "truth_table.csv"
    if not truth_path.exists():
        raise HTTPException(status_code=404, detail="Truth table not found.")
    
    df = pd.read_csv(truth_path)
    
    summary = {
        "total_ordered": int(df["ordered_units"].sum()),
        "total_planned": int(df["planned_units"].sum()),
        "total_received": int(df["received_units"].sum()),
        "service_delta": int(df["service_delta"].sum()),
        "understaffed_runs": int(df["labor_status"].str.contains("PACKING|SHIPPING", na=False).sum()),
        "total_skus": int(df["sku"].nunique()),
        "critical_risks": int(df["service_risk"].str.contains("RED", na=False).sum())
    }
    
    return summary

if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0 so it's accessible externally if needed
    uvicorn.run(app, host="0.0.0.0", port=8003)
