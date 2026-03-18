import pandas as pd

from ingestion.load_orders import load_orders
from ingestion.load_shipments import load_shipments
from ingestion.load_work_orders import load_work_orders
from ingestion.load_receipts import load_receipts
from engine.load_dimension import load_product_dimension
from engine.normalize_orders import normalize_orders
from engine.normalize_production import normalize_production
from engine.normalize_shipments import normalize_shipments


def build_truth_table():
    """
    Builds the operational truth table by reconciling:
    1. Ordered (Sales Orders from WMS)
    2. Booked (Production Booking from MIPS)
    3. Received (Inventory Receipt from WMS Recon)
    """
    # 1. Load core datasets
    ordered = load_orders()
    received = load_receipts()
    shipments = load_shipments()
    dimension = load_product_dimension()
    
    # 2. Load Production Schedule (Dough-Level)
    schedule_raw = pd.read_csv("data_raw/production_schedule.csv")
    
    # --- Dough to SKU Expansion ---
    # Join schedule with dimension to get the SKUs for each Unit Ref
    booked = schedule_raw.merge(
        dimension[["unit_ref", "fg_oracle_ref", "allocation_ratio"]],
        left_on="Unit Ref",
        right_on="unit_ref",
        how="left"
    )
    
    # Calculate SKU-level booked units
    booked["booked_units"] = booked["Net Order (Piece)"] * booked["allocation_ratio"].fillna(1.0)
    booked = booked.rename(columns={
        "fg_oracle_ref": "sku",
        "Line": "line",
        "Sales Date": "date",
        "Production Date": "production_date",
        "Start Time": "scheduled_start",
        "Finish Time": "scheduled_end"
    })
    
    # Ensure date formats
    booked["date"] = pd.to_datetime(booked["date"])
    booked["scheduled_start"] = pd.to_datetime(booked["scheduled_start"])
    booked["scheduled_end"] = pd.to_datetime(booked["scheduled_end"])

    # ------------------------------------------------
    # SKU Normalization (Legacy -> Oracle)
    # ------------------------------------------------

    ordered = normalize_orders(ordered, dimension)
    booked = normalize_production(booked)
    shipments = normalize_shipments(shipments)

    # ------------------------------------------------
    # Aggregate each dataset by Date and SKU
    # ------------------------------------------------

    ordered_grouped = (
        ordered.groupby(["date", "sku"], as_index=False)
        .agg({"ordered_units": "sum"})
    )

    # Booked grouping includes optional 'line' and 'production_date' if they exist
    booked_cols = ["date", "sku"]
    for col in ["line", "production_date", "scheduled_start", "scheduled_end"]:
        if col in booked.columns:
            booked_cols.append(col)
        
    booked_grouped = (
        booked.groupby(booked_cols, as_index=False)
        .agg({"booked_units": "sum"})
    )

    received_grouped = (
        received.groupby(["date", "sku"], as_index=False)
        .agg({"received_units": "sum"})
    )

    shipments_grouped = (
        shipments.groupby(["date", "sku"], as_index=False)
        .agg({"shipped_units": "sum"})
    )

    # ------------------------------------------------
    # Final Reconciliation Merge
    # ------------------------------------------------

    # We start with the booked schedule as the center of gravity if we want line info
    truth = booked_grouped.merge(
        ordered_grouped,
        on=["date", "sku"],
        how="outer"
    )

    truth = truth.merge(
        received_grouped,
        on=["date", "sku"],
        how="outer"
    )

    truth = truth.merge(
        shipments_grouped,
        on=["date", "sku"],
        how="outer"
    )

    # Fill NaNs with 0
    truth = truth.fillna(0)

    # ------------------------------------------------
    # Core Delta Calculations
    # ------------------------------------------------

    # Planning Delta: Did we book enough production for the orders?
    truth["planning_delta"] = truth["booked_units"] - truth["ordered_units"]

    # Production Delta: Did production hit the booking target?
    truth["production_delta"] = truth["received_units"] - truth["booked_units"]

    # Service Delta: Did we receive enough to meet orders?
    truth["service_delta"] = truth["received_units"] - truth["ordered_units"]

    # ------------------------------------------------
    # Status / Variance Flags
    # ------------------------------------------------
    def get_variance_status(row):
        if row['service_delta'] < -1000:
            return "RED: Critical Shortage"
        elif row['service_delta'] < 0:
            return "YELLOW: Service Risk"
        elif row['planning_delta'] < 0:
            return "ORANGE: Under-booked"
        else:
            return "GREEN: OK"

    truth["variance_status"] = truth.apply(get_variance_status, axis=1)

    # ------------------------------------------------
    # Root Cause Classification
    # ------------------------------------------------
    def get_root_cause(row):
        if row['service_delta'] >= 0:
            return "NONE"
        
        # If we have a service gap, find out why
        if row['planning_delta'] < 0 and abs(row['planning_delta']) >= abs(row['service_delta']):
            return "PLANNING ISSUE"
        if row['production_delta'] < 0:
            return "PRODUCTION ISSUE"
        if row['ordered_units'] > (row['booked_units'] * 1.2): # 20% surge
            return "DEMAND SURGE"
        return "OTHER"

    truth["root_cause"] = truth.apply(get_root_cause, axis=1)

    # Sort for readability
    sort_cols = ["date", "sku"]
    if "line" in truth.columns:
        sort_cols = ["date", "line", "sku"]
    truth = truth.sort_values(sort_cols)

    return truth
