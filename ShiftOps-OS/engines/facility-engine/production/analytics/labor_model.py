import pandas as pd
import os

ROSTER_PATH = "data_raw/roster.csv"
TARGETS_PATH = "dimensions/labor_targets.csv"

def calculate_labor_requirements(truth_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simplified labor model: Compares departmental targets vs actual roster headcount.
    """
    df = truth_df.copy()
    if not os.path.exists(ROSTER_PATH) or "scheduled_start" not in df.columns:
        return df

    # Load actual roster data
    roster = pd.read_csv(ROSTER_PATH)
    roster["start_time"] = pd.to_datetime(roster["start_time"])
    roster["end_time"] = pd.to_datetime(roster["end_time"])
    
    # Load targets (Shipping: 18, Packing: 12/14)
    targets = pd.read_csv(TARGETS_PATH)
    
    actual_shippers = []
    actual_packers = []
    ship_targets = []
    pack_targets = []
    
    for _, run in df.iterrows():
        s, e = run["scheduled_start"], run["scheduled_end"]
        
        # 1. Get Targets for the specific day (based on when the work starts)
        work_dt = pd.to_datetime(s) if not pd.isna(s) else pd.to_datetime(run["date"])
        day_name = work_dt.strftime("%a").upper() # SUN, MON...
        day_map = {"TUE": "TUE", "THU": "THU", "WED": "WED", "MON": "MON", "SUN": "SUN", "FRI": "FRI", "SAT": "SAT"}
        day_col = day_map.get(day_name, day_name)
        
        s_target = targets[targets["Department"] == "Shipping"][day_col].values[0]
        p_target = targets[targets["Department"] == "Packing"][day_col].values[0]
        ship_targets.append(s_target)
        pack_targets.append(p_target)

        if pd.isna(s) or pd.isna(e):
            actual_shippers.append(0); actual_packers.append(0); continue
        
        # 2. Count Available personnel during this specific time window
        available = roster[(roster["start_time"] < e) & (roster["end_time"] > s)]
        actual_shippers.append(len(available[available["department"] == "Shipping"]))
        actual_packers.append(len(available[available["department"] == "Packing"]))
        
    # Attach clear columns for the dashboard
    df["shipping_target"] = ship_targets
    df["shipping_actual"] = actual_shippers
    df["packing_target"] = pack_targets
    df["packing_actual"] = actual_packers
    
    # Simple Status Flag
    def get_labor_status(row):
        issues = []
        if row["shipping_actual"] < row["shipping_target"]:
            issues.append(f"SHIPPING: -{row['shipping_target'] - row['shipping_actual']}")
        if row["packing_actual"] < row["packing_target"]:
            issues.append(f"PACKING: -{row['packing_target'] - row['packing_actual']}")
        return ", ".join(issues) if issues else "STAFFING OK"

    df["labor_status"] = df.apply(get_labor_status, axis=1)
    
    # 7. Add Risk Score Ranking
    df = calculate_risk_score(df)

    return df

def calculate_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a 0-100 Risk Score for each run.
    Ranking: (Minutes Late * 0.5) + (Staffing Gap * 5) + (Lane Priority Weight)
    """
    lanes = pd.read_csv("dimensions/shipping_lanes.csv")
    
    risk_scores = []
    for _, row in df.iterrows():
        score = 0
        
        # A. Lateness Penalty
        sr = str(row["service_risk"])
        if "LATE" in sr or "RISK" in sr:
            # Simple heuristic: if it's in the status, it gets a base 20 points
            score += 20
            if "SYSTEM LATE" in sr:
                score += 30 # Big jump for red
        
        # B. Staffing Penalty
        ls = str(row["labor_status"])
        if "-" in ls: # e.g. "PACKING: -2"
            try:
                gap = abs(int(ls.split("-")[1]))
                score += gap * 5
            except: pass
            
        # C. Lane Priority
        # (This is simplified - we could pull actual lane weight for the SKU)
        # If it's a risk, add 10 points for priority
        if score > 0:
            score += 10
            
        risk_scores.append(min(score, 100))
        
    df["risk_score"] = risk_scores
    return df
