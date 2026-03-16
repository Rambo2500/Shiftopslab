import pandas as pd
from typing import List
from platform_core.ontology.schema import ConstraintSpec

class SpreadsheetBridge:
    """
    Connects the world of rows-and-columns to the Cybernetic Kernel.
    """
    
    @staticmethod
    def csv_to_constraints(file_path: str) -> List[ConstraintSpec]:
        """
        Converts an Excel/CSV export into formal Kernel Constraints.
        Expected columns: ID, Expression, Severity, Message
        """
        df = pd.read_csv(file_path)
        constraints = []
        
        for _, row in df.iterrows():
            constraints.append(ConstraintSpec(
                id=str(row['ID']),
                expression=str(row['Expression']),
                severity=str(row.get('Severity', 'SAFETY')),
                error_message=str(row.get('Message', 'Constraint Violated'))
            ))
            
        return constraints

    @staticmethod
    def export_audit_log(audit_data: List[dict], output_path: str):
        """
        Exports the 'Forensic Ledger' back to a Spreadsheet for human review.
        """
        df = pd.DataFrame(audit_data)
        df.to_csv(output_path, index=False)
        print(f"Audit log exported to {output_path}")
