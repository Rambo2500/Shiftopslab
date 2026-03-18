import argparse
import os
import pandas as pd
from datetime import datetime

from ingestion.load_orders import load_orders
from ingestion.load_production import load_production
from ingestion.load_receipts import load_receipts
from ingestion.load_schedule import load_schedule
from engine.load_dimension import load_product_dimension

from engine.normalize_orders import normalize_orders
from engine.normalize_production import normalize_production

from engine.reconciliation_engine import build_truth_table
from engine.runtime_engine import build_runtime_summary

from ingestion.load_detailed_orders import load_detailed_orders

from engine.shift_summary import generate_shift_summary
from engine.facility_summary import generate_facility_summary

from ingestion.load_shipments import load_shipments

def run_pipeline():
    print("--- Bakery Ops Engine: Starting Run ---")
    
    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)
    
    # 1. Load Reference Data
    print("[1] Loading reference data...")
    dimension = load_product_dimension()

    # 2. Load Daily Operational Data
    print("[2] Loading daily operational datasets...")
    orders = load_orders()
    production = load_production()
    recon = load_receipts()
    schedule = load_schedule()
    detailed_orders = load_detailed_orders()
    shipments = load_shipments()

    # 3. Normalize (Dough to SKU expansion etc)
    print("[3] Normalizing datasets...")
    # Normalize orders (Legacy -> Oracle)
    orders = normalize_orders(orders, dimension)
    production = normalize_production(production, dimension)
    
    # 4. Build Reconciliation Truth Table
    print("[4] Building Reconciliation Truth Table (Ordered vs Planned vs Received vs Shipped)...")
    truth = build_truth_table(orders, production, recon, schedule=schedule, dimension=dimension, detailed_orders=detailed_orders, shipments=shipments)
    
    # 5. Build Runtime Analytics & Merge into Truth
    print("[5] Building Runtime Analytics...")
    from analytics.runtime_model import calculate_runtime
    truth = calculate_runtime(truth)

    # 6. Run Labor Model (Reconcile against Roster)
    print("[6] Reconciling Labor Requirements vs Actual Roster...")
    from analytics.labor_model import calculate_labor_requirements
    truth = calculate_labor_requirements(truth)

    # 7. Generate Management Summary
    print("[7] Generating Management Shift Summary...")
    management_summary = generate_shift_summary(truth)

    # 8. Generate Control Tower Report
    print("[8] Generating Control Tower Dashboard (Production vs Shipped)...")
    from engine.control_tower import generate_control_tower
    control_tower = generate_control_tower(truth)

    # 9. Generate Facility Level Insights
    print("[9] Generating Facility Level Summary...")
    facility_summary = generate_facility_summary(truth, detailed_orders)

    # 10. Generate Weekly Historical Report
    print("[10] Generating Weekly Historical Review...")
    from engine.weekly_report import generate_weekly_report
    roster = pd.read_csv("data_raw/roster.csv")
    weekly_report = generate_weekly_report(truth, roster)

    # 11. Generate Visualizations
    print("[11] Generating Management Visualizations (by Exception)...")
    from engine.visualizer import generate_management_visuals
    generate_management_visuals(truth)

    # 12. Save Artifacts (Categorized for Toggles)
    print("[12] Saving outputs for dashboard...")
    os.makedirs("outputs/data", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)
    
    truth.to_csv("outputs/data/truth_table.csv", index=False)
    management_summary.to_csv("outputs/reports/management_summary.csv", index=False)
    control_tower.to_csv("outputs/reports/control_tower.csv", index=False)
    facility_summary.to_csv("outputs/reports/facility_summary.csv", index=False)
    weekly_report.to_csv("outputs/reports/weekly_historical_report.csv", index=False)
    
    # Pipeline Runtime Log
    log_df = pd.DataFrame([{
        "run_timestamp": datetime.now(),
        "skus_processed": len(truth),
        "alerts_found": len(management_summary[management_summary['management_priority'] != 'NORMAL']),
        "status": "SUCCESS"
    }])
    log_path = "outputs/pipeline_log.csv"
    log_df.to_csv(log_path, mode='a', header=not os.path.exists(log_path), index=False)

    # 13. Print Summary
    print("\n--- Pipeline Run Complete ---")
    print(f"  SKUs Reconciled: {len(truth)}")
    print(f"  Management Alerts: {len(management_summary[management_summary['management_priority'] != 'NORMAL'])}")
    print(f"  Weekly Performance: {weekly_report.iloc[0]['fill_rate_%']}% Fill Rate")
    print(f"  Outputs saved in: outputs/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bakery Operations Intelligence Engine")
    parser.add_argument("command", choices=["run"], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "run":
        try:
            run_pipeline()
        except Exception as e:
            print(f"\n[Error] Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
