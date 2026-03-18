from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI(title="ShiftOpsPro API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DELTA_PATH = "outputs/delta_summary.csv"

@app.get("/api/deltas")
def get_deltas():
    if not os.path.exists(DELTA_PATH):
        return {"error": "Delta summary not found. Run the engine first."}
    
    df = pd.read_csv(DELTA_PATH)
    # Convert date to string for JSON serialization
    if 'date' in df.columns:
        df['date'] = df['date'].astype(str)
        
    return df.to_dict(orient="records")

@app.get("/api/summary")
def get_summary():
    if not os.path.exists(DELTA_PATH):
        return {"error": "Delta summary not found. Run the engine first."}
    
    df = pd.read_csv(DELTA_PATH)
    
    summary = {
        "total_ordered": int(df["ordered_units"].sum()),
        "total_booked": int(df["booked_units"].sum()),
        "total_received": int(df["received_units"].sum()),
        "service_delta": int(df["service_delta"].sum()),
        "production_delta": int(df["production_delta"].sum()),
        "planning_delta": int(df["planning_delta"].sum()),
        "risk_skus": int((df["service_delta"] < 0).sum()),
        "total_skus": int(df["sku"].nunique())
    }
    
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
