from google.agent_development_kit import ToolContext
import json
import os
import re
from datetime import datetime

def get_product_schema_tool(tool_context: ToolContext, product_type: str):
    """
    Queries the Product Schema Registry (JSON) to retrieve mandatory fields, 
    Reference Sets, and derivation rules[cite: 9, 23].
    """
    schema_map = {"loan": "loan.json", "credit": "credit.json"}
    base_dir = os.path.dirname(os.path.dirname(__file__)) 
    file_name = schema_map.get(product_type.lower(), "loan.json")
    file_path = os.path.join(base_dir, "schema", file_name)
    
    with open(file_path, 'r') as f:
        return json.load(f)

def execute_field_derivation(tool_context: ToolContext, raw_inputs: dict):
    """
    Handles both reference field derivation (non-calculated) and 
    mathematical calculations in one pass[cite: 11, 25].
    """
    enriched_data = raw_inputs.copy()
    
    # 1. Reference Mapping (Non-calculated)
    sector_map = {"TMT": "RC-101", "Energy": "RC-202", "Retail": "RC-303"}
    enriched_data["risk_rating_code"] = sector_map.get(raw_inputs.get("sector"), "RC-GEN")
    
    # 2. Mathematical Calculations (Calculated) [cite: 25]
    try:
        base = float(raw_inputs.get("base_rate", 0))
        spread = float(raw_inputs.get("spread", 0))
        enriched_data["all_in_rate"] = base + spread
    except (ValueError, TypeError):
        enriched_data["all_in_rate"] = 0.0
    
    return enriched_data

def validate_full_proposal(tool_context: ToolContext, proposal_data: dict, schema: dict):
    """
    Performs rigorous check of formatting, mandatory presence, and 
    reference value alignment before simulation[cite: 16, 22, 38].
    """
    errors = []
    field_defs = schema.get("fields_definition", {})
    ref_data = schema.get("reference_data", {})

    for field, specs in field_defs.items():
        val = proposal_data.get(field)

        # 1. Mandatory Check [cite: 10, 16]
        if specs.get("mandatory") and (val is None or val == ""):
            errors.append(f"Missing mandatory field: {field}")
            continue

        if val is not None:
            # 2. Type & Format Validation [cite: 22, 34]
            f_type = specs.get("type")
            
            if f_type in ["currency", "percentage", "basis_points"]:
                if not isinstance(val, (int, float)):
                    errors.append(f"Field {field} must be numeric.")
            
            elif f_type == "date":
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                except (ValueError, TypeError):
                    errors.append(f"Field {field} must follow YYYY-MM-DD format.")

            # 3. Reference Set Validation [cite: 9, 10]
            if f_type == "reference" and field in ref_data:
                if val not in ref_data[field]:
                    errors.append(f"Invalid value for {field}. Allowed: {ref_data[field]}")

    if errors:
        return {"status": "rejected", "errors": errors}
    
    return {"status": "validated", "context": "ready_for_simulation"}

def fetch_session_context(tool_context: ToolContext):
    """
    Retrieves historical chat and deal data for continuity[cite: 8, 20].
    """
    return tool_context.state.get('current_deal_params', {})
