import pandas as pd
from pathlib import Path
from typing import List
from platform_core.schemas import ProductionMetric

# This service wraps the legacy bakery-engine logic into the new ShiftOps-OS schema
class ProductionService:
    def __init__(self, data_path: str = "engines/facility_intelligence/production/outputs/data/truth_table.csv"):
        self.data_path = Path(data_path)

    def get_current_metrics(self) -> List[ProductionMetric]:
        """
        Reads the latest deterministic truth table and maps it to 
        standardized ProductionMetrics.
        """
        if not self.data_path.exists():
            # Return empty metrics if no data yet
            return []

        df = pd.read_csv(self.data_path)
        
        metrics = []
        # Group by 'line' (or node)
        for line, group in df.groupby('line'):
            planned = group['ordered_units'].sum()
            actual = group['received_units'].sum()
            
            # Simple status logic
            status = "NORMAL"
            if actual < (planned * 0.9):
                status = "DELAY"
            if actual < (planned * 0.7):
                status = "CRITICAL"

            metrics.append(ProductionMetric(
                node_id=str(line),
                planned_units=float(planned),
                actual_units=float(actual),
                uph_target=group['target_uph'].mean() if 'target_uph' in group else 0.0,
                uph_actual=group['actual_uph'].mean() if 'actual_uph' in group else 0.0,
                status=status
            ))
        
        return metrics
