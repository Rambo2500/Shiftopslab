import pandas as pd
import json
import time
import os
import glob
from datetime import datetime, timedelta

# CONFIGURATION
INPUT_FOLDER = "data_inputs"
HISTORY_FOLDER = "data_history"
REFERENCE_FILE = "sku_reference.csv"
OUTPUT_FILE = "dashboard_data.json"

# SITE METADATA
SITE_METADATA = {
    'FAC': {'name': 'North Aurora', 'travel': 5, 'priority': 250},
    'FSB': {'name': 'South Bend', 'travel': 1, 'priority': 290},
    'FCR': {'name': 'Cedar Rapids', 'travel': 7, 'priority': 230},
    'FRI': {'name': 'Riverside', 'travel': 12, 'priority': 225},
    'FAK': {'name': 'Kansas City DC', 'travel': 12, 'priority': 220},
    'FJA': {'name': 'Janesville', 'travel': 5, 'priority': 240},
    'PCB': {'name': 'Fort Worth', 'travel': 26, 'priority': 200},
    'GB3968970': {'name': 'Christina Foods', 'travel': 4, 'priority': 215},
    'GB4027603': {'name': 'Sun Valley', 'travel': 4, 'priority': 210},
}

CALENDAR_OFFSETS = {
    'Monday': 3, 'Tuesday': 3, 'Thursday': 2, 'Friday': 2, 'Saturday': 2, 'Wednesday': 2, 'Sunday': 2
}

# --- CLEAN PARSER UTILITIES ---

def clean_value(v):
    if pd.isna(v): return ""
    v = str(v).strip()
    if v.startswith('="') and v.endswith('"'): v = v[2:-1] # remove Excel ="value"
    if v.endswith(".0"): v = v[:-2] # remove trailing .0 Excel artifacts
    return v.strip()

def clean_numeric(v):
    try:
        v = str(v).replace(",", "").replace('"', "").strip()
        if v == "" or v.lower() == "nan": return 0
        return float(v)
    except: return 0

def normalize_facility(v):
    return str(v).strip().upper()

def load_csv(path):
    try:
        df = pd.read_csv(path, encoding="iso-8859-1", dtype=str, on_bad_lines="skip")
        df.columns = df.columns.str.strip()
        for c in df.columns:
            df[c] = df[c].apply(clean_value)
        return df
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return pd.DataFrame()

def detect_file_type(file_path):
    try:
        df = pd.read_csv(file_path, nrows=5, encoding='iso-8859-1')
        cols = [str(c).lower().strip() for c in df.columns]
        if any("load nbr" in c for c in cols) and any("order nbr" in c for c in cols) and any("lpn status" in c for c in cols):
            return "oblpns"
        if any("load nbr" in c for c in cols) and "status" in cols and any("dock nbr" in c for c in cols):
            return "obloads"
        if any("order nbr" in c for c in cols) and any("item code" in c for c in cols):
            return "orders"
        if any("lpn" in c for c in cols) and any("current qty" in c for c in cols) and "location" in cols:
            return "iblpns"
        return "unknown"
    except:
        return "unknown"

def process_data():
    try:
        files = glob.glob(f"{INPUT_FOLDER}/*.csv")
        file_map = {}
        for f in files:
            f_type = detect_file_type(f)
            if f_type != "unknown": file_map[f_type] = f

        # Load SKU Factors
        sku_factors = {}
        if os.path.exists(REFERENCE_FILE):
            ref_df = load_csv(REFERENCE_FILE)
            for _, row in ref_df.iterrows():
                try:
                    sku = str(row['FG Oracle Ref']).strip()
                    u_per_c = clean_numeric(row.get('Units per Container', 10))
                    c_per_r = clean_numeric(row.get('Containers per Rack', 17))
                    sku_factors[sku] = u_per_c * c_per_r
                except: continue

        # Load Dataframes
        data = {}
        for t, f in file_map.items():
            data[t] = load_csv(f)

        dashboard_loads = []
        available_dates = []
        
        # --- GET SALES DATES FROM ORDER DETAILS ---
        if "orders" in data:
            orders_df = data["orders"]
            date_col = next((c for c in orders_df.columns if 'Sales Date' in c), None)
            if date_col:
                available_dates = sorted(list(set(orders_df[date_col].dropna())))

        if "oblpns" in data:
            oblpn_df = data["oblpns"]
            if not available_dates and 'Sales Date*' in oblpn_df.columns:
                available_dates = sorted(oblpn_df['Sales Date*'].dropna().unique().tolist())

            # Group by Load Nbr and Sales Date
            load_agg = oblpn_df.groupby(["Load Nbr", "Sales Date*"]).agg({
                "Allocated Qty": "first", # Will re-sum manually to be safe
                "LPN Status": "first",
                "Destination Facility*": "first",
                "Item Code": "first"
            }).reset_index()
            
            # Recalculate sums using robust numeric cleaner
            load_sums = oblpn_df.groupby(["Load Nbr", "Sales Date*"]).apply(lambda x: pd.Series({
                "Total Allocated": x["Allocated Qty"].apply(clean_numeric).sum(),
                "Total Current": x["Current Qty"].apply(clean_numeric).sum()
            })).reset_index()
            
            load_agg = load_agg.merge(load_sums, on=["Load Nbr", "Sales Date*"])

            # Dock Assignments from OBLoads
            dock_assignments = {}
            if "obloads" in data:
                ob_df = data["obloads"]
                d_col = next((c for c in ob_df.columns if 'Dock' in c), None)
                if d_col:
                    for _, row in ob_df.iterrows():
                        l_id = str(row.get("Load Nbr", ""))
                        d_val = str(row.get(d_col, "--"))
                        clean_d = "".join(filter(str.isdigit, d_val))
                        if clean_d: clean_d = str(int(clean_d))
                        if l_id and clean_d: dock_assignments[l_id] = clean_d

            for _, row in load_agg.iterrows():
                l_id = str(row["Load Nbr"])
                s_date_raw = str(row["Sales Date*"])
                dest_code = normalize_facility(row.get("Destination Facility*", "Unknown"))
                meta = SITE_METADATA.get(dest_code, {'name': dest_code, 'travel': 0, 'priority': 999})
                
                status = str(row["LPN Status"])
                ordered = int(row["Total Allocated"]) 
                allocated = int(row["Total Current"])
                needed = max(0, ordered - allocated)
                
                # Deadline logic
                try:
                    s_dt = pd.to_datetime(s_date_raw)
                    if pd.isna(s_dt): s_dt = datetime.now()
                except:
                    s_dt = datetime.now()
                
                days_prior = CALENDAR_OFFSETS.get(s_dt.strftime("%A"), 2)
                ship_dt = s_dt - timedelta(days=days_prior)
                deadline = ship_dt + timedelta(hours=meta['travel'])
                
                production_eta_hrs = (needed / 4132.0)
                hours_remaining = (deadline - datetime.now()).total_seconds() / 3600.0
                
                health = "GREEN"
                if needed == 0: health = "GREEN"
                elif production_eta_hrs > hours_remaining: health = "RED"
                elif status in ["Loading Started", "Shipped"]: health = "YELLOW"
                
                item_code = str(row.get("Item Code", ""))
                stack_cap = sku_factors.get(item_code, 170.0)

                dashboard_loads.append({
                    "id": l_id, 
                    "sales_date": s_date_raw, 
                    "dest": meta['name'], 
                    "dest_code": dest_code,
                    "dock": dock_assignments.get(l_id, "--"), 
                    "status": status,
                    "ordered": ordered, 
                    "allocated": allocated, 
                    "needed": needed,
                    "priority": meta['priority'],
                    "window": deadline.strftime("%I:%M %p"),
                    "deadline": deadline.strftime("%I:%M %p"),
                    "travel_hours": meta["travel"],
                    "eta_mins": int(production_eta_hrs * 60),
                    "health": health,
                    "stacks": round(ordered / stack_cap, 1)
                })

        # Sort by Priority
        dashboard_loads.sort(key=lambda x: x['priority'])

        # Recon Totals per day
        recon_summary = {}
        for d in available_dates:
            day_loads = [l for l in dashboard_loads if l["sales_date"] == d]
            alc = sum(l["ordered"] for l in day_loads) 
            shp = sum(l["allocated"] for l in day_loads if l["status"] in ["Shipped", "Delivered"])
            recon_summary[d] = {"produced": int(alc), "shipped": int(shp), "variance": int(alc - shp)}

        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "loads": dashboard_loads,
            "available_dates": available_dates,
            "recon_summary": recon_summary,
            "velocity": 24.3 
        }

        with open(OUTPUT_FILE, "w") as f: json.dump(output, f, indent=4)
        print(f"✅ Digital Twin Rebuilt: {output['last_update']}")

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if not os.path.exists(INPUT_FOLDER): os.makedirs(INPUT_FOLDER)
    while True:
        process_data()
        time.sleep(10)
