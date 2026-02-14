from google.agent_development_kit import ToolContext
import json
import os
from datetime import datetime

def get_product_schema_tool(tool_context: ToolContext, product_type: str):
    """
    Retrieves the full product config, including validation rules 
    and API mapping blueprints.
    """
    schema_map = {"loan": "loan.json", "rcf": "rcf.json"}
    base_dir = os.path.dirname(os.path.dirname(__file__)) 
    file_name = schema_map.get(product_type.lower(), "loan.json")
    file_path = os.path.join(base_dir, "schema", file_name)
    
    with open(file_path, 'r') as f:
        return json.load(f)

def execute_field_derivation(tool_context: ToolContext, raw_inputs: dict, schema: dict):
    """
    Uses the 'derivation_targets' from the JSON to enrich deal data.
    """
    enriched_data = raw_inputs.copy()
    derivation_rules = schema.get("schema_details", {}).get("derivation_targets", {})
    
    # 1. Logic for Reference Mapping (e.g., Risk Ratings)
    if "risk_rating_code" in derivation_rules.get("reference_mapped", []):
        sector_map = {"TMT": "RC-101", "Energy": "RC-202", "Retail": "RC-303"}
        enriched_data["risk_rating_code"] = sector_map.get(raw_inputs.get("sector"), "RC-GEN")
    
    # 2. Logic for Mathematical Calculations (e.g., All-in-Rate)
    if "calculated" in derivation_rules:
        try:
            base = float(raw_inputs.get("base_rate", 0))
            spread = float(raw_inputs.get("spread", 0))
            enriched_data["all_in_rate"] = base + spread
        except (ValueError, TypeError):
            enriched_data["all_in_rate"] = 0.0
    
    return enriched_data

def validate_full_proposal(tool_context: ToolContext, proposal_data: dict, schema: dict):
    """
    Performs checks based on the 'schema_details' section of the config.
    """
    errors = []
    # Pointing to the new nested structure
    details = schema.get("schema_details", {})
    field_defs = details.get("fields_definition", {})
    ref_data = details.get("reference_data", {})

    for field, specs in field_defs.items():
        val = proposal_data.get(field)

        # 1. Mandatory Check
        if specs.get("mandatory") and (val is None or val == ""):
            errors.append(f"Missing mandatory field: {field}")
            continue

        if val is not None:
            f_type = specs.get("type")
            
            # 2. Numeric Validation
            if f_type in ["currency", "percentage", "basis_points"]:
                if not isinstance(val, (int, float)):
                    errors.append(f"Field {field} must be numeric.")
            
            # 3. Date Format Validation
            elif f_type == "date":
                expected_format = specs.get("format", "%Y-%m-%d")
                try:
                    # Converting YYYY-MM-DD to python-compatible format if necessary
                    py_format = expected_format.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
                    datetime.strptime(str(val), py_format)
                except (ValueError, TypeError):
                    errors.append(f"Field {field} must follow {expected_format} format.")

            # 4. Reference Set Validation
            if f_type == "reference" and field in ref_data:
                if val not in ref_data[field]:
                    errors.append(f"Invalid value for {field}. Allowed: {ref_data[field]}")

    if errors:
        return {"status": "rejected", "errors": errors}
    
    return {"status": "validated", "context": "ready_for_simulation"}
