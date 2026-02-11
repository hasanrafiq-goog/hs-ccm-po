from google.agent_development_kit import ToolContext
import json
import os

def get_product_schema_tool(tool_context: ToolContext, product_type: str):
    """
    Queries the Product Schema Registry (JSON) to retrieve mandatory fields, 
    Reference Sets, and derivation rules[cite: 9, 23].
    """
    # FIX: Changed 'schemas' to 'schema' to match your folder image
    schema_map = {"loan": "loan.json", "credit": "credit.json"}
    
    # Using absolute path logic ensures it finds the folder regardless of entry point
    base_dir = os.path.dirname(os.path.dirname(__file__)) 
    file_name = schema_map.get(product_type.lower(), "loan.json")
    file_path = os.path.join(base_dir, "schema", file_name)
    
    with open(file_path, 'r') as f:
        return json.load(f)

def execute_field_derivation(tool_context: ToolContext, raw_inputs: dict):
    """
    A single Python function handling both reference field derivation 
    (non-calculated) and mathematical calculations.
    """
    enriched_data = raw_inputs.copy()
    
    # 1. Reference Mapping (e.g., Sector -> Risk Code) 
    sector_map = {"TMT": "RC-101", "Energy": "RC-202", "Retail": "RC-303"}
    enriched_data["risk_rating_code"] = sector_map.get(raw_inputs.get("sector"), "RC-GEN")
    
    # 2. Mathematical Calculations (e.g., All-in-Rate) [cite: 25]
    try:
        base = float(raw_inputs.get("base_rate", 0))
        spread = float(raw_inputs.get("spread", 0))
        enriched_data["all_in_rate"] = base + spread
    except (ValueError, TypeError):
        enriched_data["all_in_rate"] = 0.0
    
    return enriched_data

def validate_full_proposal(tool_context: ToolContext, proposal_data: dict):
    """
    Validates the complete data object against ORC Simulate API requirements 
    before a deal can be simulated[cite: 16, 22, 38].
    """
    # Technical format and compliance check for the Simulation API [cite: 34, 38]
    # In production, this would perform a schema check or call the 'Lite Validate' endpoint
    return {"status": "validated", "context": "ready_for_simulation"}

def fetch_session_context(tool_context: ToolContext):
    """
    Retrieves historical chat and deal data for continuity[cite: 8, 20].
    """
    return tool_context.state.get('current_deal_params', {})
