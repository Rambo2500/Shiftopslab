from datetime import datetime, timedelta
from typing import Dict, List, Any

class ConflictChecker:
    def check_for_conflicts(self, new_assignment: Dict[str, Any], existing_assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        conflicts = []
        n_start = new_assignment['start_time']
        n_end = new_assignment['end_time']
        for existing in existing_assignments:
            e_start = existing['start_time']
            e_end = existing['end_time']
            if n_start < e_end and n_end > e_start:
                conflicts.append({
                    "type": "overlap",
                    "message": f"Overlap with assignment {existing.get('id', 'unknown')}",
                    "offending_id": existing.get('id')
                })
        return conflicts
