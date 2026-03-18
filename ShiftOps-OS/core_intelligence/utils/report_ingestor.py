import pandas as pd
import io
import re
from typing import Dict, Any, List

class IndustrialReportIngestor:
    """
    The 'Universal Translator' for messy legacy reports (AS400, WMS, etc.)
    """
    
    @staticmethod
    def identify_and_parse(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r') as f:
                head = f.read(1000)
            
            # Identify BP174 (AS400 Inventory Recon)
            if "BBRP174" in head or "Over/Short" in head:
                return IndustrialReportIngestor.parse_bp174(file_path)
            
            # Fallback for generic CSV
            if "," in head:
                df = pd.read_csv(file_path)
                return {"type": "GENERIC_CSV", "data": df.to_dict(orient='records')}
                
            return {"type": "UNKNOWN", "message": "Report format not recognized yet."}
        except Exception as e:
            return {"type": "ERROR", "message": str(e)}

    @staticmethod
    def parse_bp174(file_path: str) -> Dict[str, Any]:
        """
        Parses the AS400 RP174 Inventory Reconciliation Report.
        Handles the messy AS400 tab-separated format with shifted headers.
        """
        # AS400 RP174 headers often miss the 'Product ID' column in the header row
        true_headers = [
            'Report', 'Market Area', 'Ending Date', 'Period', 'Location', 'Name', 
            'Product ID', 'Product Description', 'Begin Inv', 
            'Rec/Ord', 'Rec/Chg', 'Rec/Claim', 'Net Rec',
            'Ship/Ord', 'Ship/Chg', 'Ship/Claim', 'Net Ship',
            'End Inv', 'Over/Short', 'Equiv Unit', 'Prod As'
        ]

        try:
            # Read skiping the first line (messy headers) and providing our own
            df = pd.read_csv(file_path, sep='\t', names=true_headers, skiprows=1, skipinitialspace=True)
            
            # Clean up Product ID (remove ="")
            df['Product ID'] = df['Product ID'].str.replace('="', '').str.replace('"', '')
            
            # Convert numeric columns
            numeric_cols = [
                'Begin Inv', 'Rec/Ord', 'Rec/Chg', 'Rec/Claim', 'Net Rec',
                'Ship/Ord', 'Ship/Chg', 'Ship/Claim', 'Net Ship',
                'End Inv', 'Over/Short'
            ]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # --- INTELLIGENCE: Flow Reconciliation ---
            # If Net Rec is 0 but Rec/Ord has value, calculate it
            df.loc[df['Net Rec'] == 0, 'Net Rec'] = df['Rec/Ord'] + df['Rec/Chg'] + df['Rec/Claim']
            # Same for Net Ship
            df.loc[df['Net Ship'] == 0, 'Net Ship'] = df['Ship/Ord'] + df['Ship/Chg'] + df['Ship/Claim']

            # Calculate Theoretical End
            df['Theoretical End'] = df['Begin Inv'] + df['Net Rec'] - df['Net Ship']
            
            # Variance Check (Actual End - Theoretical)
            # If End Inv is 0 but Over/Short has value, we can infer Actual End
            # Actual End = Theoretical End + Over/Short
            df['Derived End Inv'] = df['Theoretical End'] + df['Over/Short']

            # Filter out non-product rows (header repeats, empty rows)
            df = df[df['Product Description'].str.len() > 2]
            
            # Summarize
            shortages = df[df['Over/Short'] < 0].sort_values(by='Over/Short')
            
            return {
                "type": "BP174_AS400",
                "ontology_id": "inventory_recon_v1",
                "total_shortage_units": abs(df['Over/Short'].sum()),
                "top_losses": shortages[['Product Description', 'Over/Short']].head(5).to_dict(orient='records'),
                "flow_summary": {
                    "total_receipts": df['Net Rec'].sum(),
                    "total_shipments": df['Net Ship'].sum(),
                    "net_inventory_delta": df['Net Rec'].sum() - df['Net Ship'].sum(),
                    "integrity_status": "VALIDATED" if (df['Over/Short'] + df['Theoretical End'] - df['End Inv']).abs().sum() < 1 else "DISCREPANCY"
                },
                "raw_summary": f"Processed {len(df)} SKUs from BP174 using deterministic flow ontology."
            }
        except Exception as e:
            return {"type": "ERROR", "message": f"BP174 Parse Failed: {str(e)}"}
