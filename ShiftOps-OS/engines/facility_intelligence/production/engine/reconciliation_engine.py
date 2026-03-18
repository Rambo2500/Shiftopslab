import pandas as pd

def build_truth_table(orders, production, recon, schedule=None, dimension=None, detailed_orders=None, shipments=None):
    """
    Builds the core reconciliation table (Ordered vs Planned vs Received vs Shipped).
    Also attaches Schedule timing and Service Risk analysis.
    """
    # 1. Volume Grouping
    orders_grouped = orders.groupby(["sku", "date"], as_index=False)["ordered_units"].sum()
    prod_grouped = production.groupby(["sku", "date"], as_index=False)["planned_units"].sum()
    recon_grouped = recon.groupby(["sku", "date"], as_index=False)["received_units"].sum()
    ship_grouped = pd.DataFrame()
    if shipments is not None:
        ship_grouped = shipments.groupby(["sku", "date"], as_index=False)["shipped_units"].sum()

    # 2. Main Reconciliation Merge
    truth = orders_grouped.merge(prod_grouped, on=["sku", "date"], how="outer")
    truth = truth.merge(recon_grouped, on=["sku", "date"], how="outer")
    if not ship_grouped.empty:
        truth = truth.merge(ship_grouped, on=["sku", "date"], how="outer")
    
    truth = truth.fillna(0)

    # 3. Attach Schedule & Service Risk (If provided)
    if schedule is not None and dimension is not None:
        # Expand schedule to SKU level for matching
        sched_skus = schedule.merge(
            dimension[["unit_ref", "fg_oracle_ref"]],
            on="unit_ref",
            how="left"
        ).rename(columns={"fg_oracle_ref": "sku"})
        
        # Merge timing and Line detail into truth
        sched_grouped = sched_skus.groupby(["sku"], as_index=False).agg({
            "line": "first",
            "scheduled_start": "min",
            "scheduled_end": "max"
        })
        truth = truth.merge(sched_grouped, on="sku", how="left")
        
        # --- Generate Run_ID (The 'Red Thread' for Audits) ---
        def generate_run_id(row):
            if pd.isna(row["scheduled_start"]): return "UNSCHEDULED"
            date_str = pd.to_datetime(row["date"]).strftime("%Y%m%d")
            line_str = str(row["line"]).replace(" ", "")
            return f"{date_str}_{line_str}_{row['sku']}"
        
        truth["run_id"] = truth.apply(generate_run_id, axis=1)

        # --- Service Risk & Root Cause Logic ---
        if detailed_orders is not None:
            lanes = pd.read_csv("dimensions/shipping_lanes.csv")
            risk_labels = []
            root_causes = []
            
            for _, row in truth.iterrows():
                s, e = row["scheduled_start"], row["scheduled_end"]
                if pd.isna(e):
                    risk_labels.append("NO SCHEDULE")
                    root_causes.append("PLANNING_MISS")
                    continue
                
                sku_orders = detailed_orders[
                    (detailed_orders["sku"] == row["sku"]) & 
                    (detailed_orders["sales_date"] == row["date"])
                ]
                
                if sku_orders.empty:
                    risk_labels.append("STAFFING OK")
                    root_causes.append("NONE")
                    continue
                
                locations = sku_orders["location"].unique()
                sku_lanes = lanes[lanes["location"].isin(locations)]
                
                system_late = False
                internal_risks = []
                all_early = True
                
                system_deadline = e.replace(hour=18, minute=0, second=0)
                if e > system_deadline: system_late = True

                for _, lane in sku_lanes.iterrows():
                    dd_str = str(int(lane["drop_dead_time"])).zfill(4)
                    dd_hour, dd_min = int(dd_str[:2]), int(dd_str[2:])
                    internal_deadline = e.replace(hour=dd_hour, minute=dd_min)
                    
                    if e > internal_deadline:
                        internal_risks.append(lane["location"])
                        all_early = False
                    elif (internal_deadline - e).total_seconds() < 7200:
                        all_early = False
                
                # Determine Root Cause
                cause = "NONE"
                if system_late or internal_risks:
                    # Check if labor was the cause (if we have labor_status in next step, 
                    # but for now we check order volume vs line rate)
                    if row["received_units"] < row["planned_units"]:
                        cause = "PRODUCTION_SHORTFALL"
                    else:
                        cause = "SCHEDULING_CONSTRAINT"

                if system_late:
                    risk_labels.append(f"RED: SYSTEM LATE ({e.strftime('%H:%M')})")
                elif internal_risks:
                    risk_labels.append(f"YELLOW: INTERNAL RISK ({', '.join(internal_risks)})")
                elif all_early and not sku_lanes.empty:
                    risk_labels.append("BLUE: EARLY (SLACK DETECTED)")
                else:
                    risk_labels.append("GREEN: ON TIME")
                
                root_causes.append(cause)
            
            truth["service_risk"] = risk_labels
            truth["root_cause"] = root_causes

    # 4. Core Metrics
    truth["planned_delta"] = truth["planned_units"] - truth["ordered_units"]
    truth["service_delta"] = truth["received_units"] - truth["ordered_units"]
    truth["production_drift"] = truth["received_units"] - truth["planned_units"]

    # 5. Throughput Validation (If times exist)
    if "scheduled_start" in truth.columns and "scheduled_end" in truth.columns:
        truth["scheduled_duration_hrs"] = (
            truth["scheduled_end"] - truth["scheduled_start"]
        ).dt.total_seconds() / 3600
        
    return truth
