import operator
from typing import Dict, Any, List, Optional
from platform_core.ontology.schema import ConstraintSpec, IndustryPack

class ConstraintParser:
    """The Judge: Evaluates boolean math with spreadsheet precision."""
    OPERATORS = {
        "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
        "==": operator.eq, "!=": operator.ne, "+": operator.add, "-": operator.sub,
        "*": operator.mul, "/": operator.truediv
    }

    @staticmethod
    def evaluate(expression: str, values: Dict[str, float]) -> bool:
        parts = expression.split()
        if len(parts) != 3: return True 
        left_key, op_str, right_val_str = parts
        
        left_val = values.get(left_key, 0.0)
        try:
            right_val = float(right_val_str)
        except ValueError:
            right_val = values.get(right_val_str, 0.0)
            
        op_func = ConstraintParser.OPERATORS.get(op_str)
        return op_func(left_val, right_val) if op_func else True

class StateResolver:
    """The Librarian: Maps any symbol to any number, blind to the industry."""
    
    @staticmethod
    def resolve_variables(pack: IndustryPack, raw_telemetry: Dict[str, Any]) -> Dict[str, float]:
        """
        Symbolic mapping. 
        If the ontology expects 'temp' and raw_telemetry provides 'temp', it maps.
        If it expects 'count(entities)', it performs the aggregation.
        """
        resolved = {}
        
        # 1. Direct Telemetry Mapping (Cell Values)
        for key, value in raw_telemetry.items():
            if isinstance(value, (int, float)):
                resolved[key] = float(value)
        
        # 2. Aggregation Logic (The 'Spreadsheet Formulas')
        # In a full build, this uses regex to find COUNT/SUM in expressions
        if "entities" in raw_telemetry:
            entities = raw_telemetry["entities"]
            # Example: count(patient) -> generic count by type
            types = set([e.get("type") for e in entities])
            for t in types:
                resolved[f"count_{t}"] = float(len([e for e in entities if e.get("type") == t]))
        
        # 3. Industry-Specific Variable Logic (from the LOM metadata)
        # This allows the LOM to define its own derived variables
        for var_name, formula in pack.metadata.get("derived_variables", {}).items():
            # For now, simple direct mapping. In full build, this runs the Parser recursively.
            resolved[var_name] = resolved.get(formula, 0.0)

        return resolved
