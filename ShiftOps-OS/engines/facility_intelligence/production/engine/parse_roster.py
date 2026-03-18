import pandas as pd
import re
from datetime import datetime, timedelta

def parse_time(time_str, base_date):
    if not time_str or time_str.strip() == "":
        return None
    time_str = time_str.lower().strip()
    match = re.match(r"(\d+):(\d+)\s*([ap])", time_str)
    if not match: return None
    hours, minutes, ampm = int(match.group(1)), int(match.group(2)), match.group(3)
    if ampm == 'p' and hours < 12: hours += 12
    if ampm == 'a' and hours == 12: hours = 0
    return base_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)

def parse_labor_schedule(file_path, year=2026):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    records = []
    current_dates = []
    current_dept = "Unknown"
    
    # Skip role summaries and headers
    skip_keywords = ["TEAM", "NAME", "SUN", "MON", "TUES", "WED", "THUR", "FRI", "SAT", "", 
                     "Bread", "Bun", "Muffin Line", "Line lead", "SR dock", "Flloating postion", 
                     "De-Nester", "Dock", "Break Relief", "Supervisor", "logistics", "Department",
                     "schedule logic", "Shipping hours", "Packing hours"]
    
    for line in lines:
        parts = [p.strip() for p in line.split('\t')]
        if not any(parts): continue
        
        # Detect Department
        if "SHIPPER Schedule" in line:
            current_dept = "Shipping"
            continue
        elif "PACKER Schedule" in line:
            current_dept = "Packing"
            continue
            
        # Identify date header line
        if any(re.match(r"\d+/\d+", p) for p in parts):
            current_dates = []
            for p in parts:
                date_match = re.match(r"(\d+)/(\d+)", p)
                if date_match:
                    m, d = int(date_match.group(1)), int(date_match.group(2))
                    current_dates.append(datetime(year, m, d))
            continue
            
        if parts[0] in skip_keywords or any(kw in parts[0] for kw in ["Schedule", "hours", "logic"]):
            continue
            
        # Roster line
        team, name = parts[0], parts[1]
        
        # Override department based on Team if known
        if team in ["A", "B", "C", "D", "A / B"]:
            row_dept = "Shipping"
        elif team.startswith("P"):
            row_dept = "Packing"
        else:
            row_dept = current_dept

        for i, shift_str in enumerate(parts[2:]):
            if i >= len(current_dates): break
            if "-" in shift_str:
                date = current_dates[i]
                start_dt = parse_time(shift_str.split("-")[0], date)
                end_dt = parse_time(shift_str.split("-")[1], date)
                if start_dt and end_dt:
                    if end_dt <= start_dt: end_dt += timedelta(days=1)
                    records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "department": row_dept,
                        "team": team,
                        "name": name,
                        "start_time": start_dt,
                        "end_time": end_dt
                    })
                    
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = parse_labor_schedule("data_raw/labor_schedule_raw.txt")
    df.to_csv("data_raw/roster.csv", index=False)
    print(f"Parsed {len(df)} entries to data_raw/roster.csv")
