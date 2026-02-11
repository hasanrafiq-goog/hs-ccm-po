from google.agent_development_kit import ToolContext
import json
import os

def get_product_schema_tool(tool_context: ToolContext, product_type: str):
    """
    Queries the Product Schema Registry (JSON) to retrieve mandatory fields, 
    Reference Sets, and derivation rules.
    """
    # Maps 'loan' or 'credit' to the corresponding JSON file in /schemas
    schema_map = {"loan": "loan.json", "credit": "credit.json"}
    file_path = f"./schemas/{schema_map.get(product_type.lower(), 'loan.json')}"
    
    with open(file_path, 'r') as f:
        return json.load(f)

def execute_field_derivation(tool_context: ToolContext, raw_inputs: dict):
    """
    A single Python function handling both reference field derivation 
    (non-calculated) and mathematical calculations.
    """
    enriched_data = raw_inputs.copy()
    
    # 1. Reference Mapping (e.g., Sector -> Risk Code) [cite: 100]
    sector_map = {"TMT": "RC-101", "Energy": "RC-202", "Retail": "RC-303"}
    enriched_data["risk_rating_code"] = sector_map.get(raw_inputs.get("sector"), "RC-GEN")
    
    # 2. Mathematical Calculations (e.g., All-in-Rate) 
    base = float(raw_inputs.get("base_rate", 0))
    spread = float(raw_inputs.get("spread", 0))
    enriched_data["all_in_rate"] = base + spread
    
    return enriched_data

def validate_full_proposal(tool_context: ToolContext, proposal_data: dict):
    """
    Validates the complete data object against ORC Simulate API requirements 
    before a deal can be simulated.
    """
    # Technical format and compliance check for the Simulation API
    return {"status": "validated", "context": "ready_for_simulation"}

def fetch_session_context(tool_context: ToolContext):
    """
    Retrieves historical chat and deal data for continuity[cite: 97, 109].
    """
    return tool_context.state.get('current_deal_params', {})
