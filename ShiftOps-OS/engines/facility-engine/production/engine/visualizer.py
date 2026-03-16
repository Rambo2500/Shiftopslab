import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def generate_management_visuals(truth_df):
    """
    Orchestrates management-by-exception visualization.
    Only generates detailed charts for risk areas.
    """
    os.makedirs("outputs/charts/exceptions", exist_ok=True)
    os.makedirs("outputs/charts/overview", exist_ok=True)
    
    # 1. Overview: Service Risk Timeline (Always Generated)
    generate_timing_chart(truth_df, "outputs/charts/overview/executive_service_timeline.png")
    
    # 2. Exceptions: Individual Risk Charts
    risk_df = truth_df[truth_df["service_risk"].str.contains("RED|YELLOW", na=False)]
    for _, row in risk_df.iterrows():
        run_id = row["run_id"]
        # Simple specific visual for this run
        plt.figure(figsize=(8, 2))
        plt.axvline(x=18, color="red", linestyle="--", label="System Cutoff")
        finish_hour = pd.to_datetime(row["scheduled_end"]).hour
        plt.barh([run_id], [finish_hour], color="#f1c40f")
        plt.xlim(0, 24)
        plt.title(f"Risk Detail: {run_id}")
        plt.tight_layout()
        plt.savefig(f"outputs/charts/exceptions/risk_{run_id}.png")
        plt.close()

    # 3. Exceptions: Labor Gaps
    gap_df = truth_df[truth_df["labor_status"].str.contains("PACKING|SHIPPING", na=False)]
    if not gap_df.empty:
        generate_labor_chart(gap_df, "outputs/charts/exceptions/labor_gap_details.png")

def generate_timing_chart(truth_df, output_path):
    """
    Generates a visual timeline comparing Production Finish vs Lane Deadlines.
    """
    df = truth_df[truth_df["scheduled_end"].notna()].copy()
    if df.empty:
        return
    
    # Convert to datetime
    df["scheduled_end"] = pd.to_datetime(df["scheduled_end"])
    
    # Sort for cleaner visual
    df = df.sort_values("scheduled_end")
    
    # Prepare Labels
    df["label"] = df["sku"].astype(str) + " (" + df["line"].astype(str) + ")"
    
    plt.figure(figsize=(12, 6))
    
    # Plot bars for production finish time (hour of day)
    finish_hours = df["scheduled_end"].dt.hour + df["scheduled_end"].dt.minute / 60
    
    colors = []
    for risk in df["service_risk"]:
        if "RED" in str(risk): colors.append("#e74c3c") # Red
        elif "YELLOW" in str(risk): colors.append("#f1c40f") # Yellow
        elif "BLUE" in str(risk): colors.append("#3498db") # Blue
        else: colors.append("#2ecc71") # Green
        
    bars = plt.barh(df["label"], finish_hours, color=colors, alpha=0.8)
    
    # Add System Deadline Line (18:00)
    plt.axvline(x=18, color="#c0392b", linestyle="--", label="System Cutoff (18:00)")
    
    plt.title(f"Production Timing & Service Risk Control Tower - {datetime.now().strftime('%Y-%m-%d')}")
    plt.xlabel("Hour of Day (24hr)")
    plt.ylabel("SKU / Line")
    plt.xlim(0, 24)
    plt.xticks(range(0, 25))
    plt.grid(axis='x', linestyle=':', alpha=0.6)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Generated Service Risk Visualization: {output_path}")

def generate_labor_chart(truth_df, output_path="outputs/labor_gap_chart.png"):
    """
    Generates a chart showing Packing Actual vs Target.
    """
    df = truth_df[truth_df["packing_target"] > 0].copy()
    if df.empty:
        return
        
    plt.figure(figsize=(10, 6))
    
    labels = df["sku"].astype(str)
    x = range(len(labels))
    
    plt.bar(x, df["packing_target"], width=0.4, label="Target Staff", color="#bdc3c7", alpha=0.7)
    plt.bar(x, df["packing_actual"], width=0.4, label="Actual Staff", color="#2980b9", alpha=0.9)
    
    plt.title("Labor Capacity vs. Requirements (Packing)")
    plt.xlabel("Production SKU")
    plt.ylabel("Headcount")
    plt.xticks(x, labels, rotation=45)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Generated Labor Gap Visualization: {output_path}")
