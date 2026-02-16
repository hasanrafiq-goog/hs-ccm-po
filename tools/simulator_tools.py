from google.adk.tools import ToolContext
import requests # Assuming standard REST calls for ORC API

# --- TOOL IMPLEMENTATIONS FOR SIMULATOR ---

def validate_simulation_inputs(tool_context: ToolContext, parameters: dict):
    """
    TASK: 'Lite' Validation for Calculation[cite: 34, 87].
    
    DEVS:
    1. Focused strictly on the subset of fields required for the ORC Simulation API[cite: 38, 90].
    2. Rapid check of mathematical 'levers' (Margin, Fees, Tenor) to ensure the API won't error out[cite: 34].
    """
    required_levers = ["notional", "base_rate", "spread"]
    for lever in required_levers:
        if lever not in parameters:
            return {"status": "invalid", "error": f"Missing simulation lever: {lever}"}
    
    return {"status": "valid"}

def generate_variation_parameters(tool_context: ToolContext, base_params: dict):
    """
    TASK: Configure Simulator for Type 1 Sweep (±3 levels).
    
    DEVS:
    1. Generates a 'brute-force' matrix of parameter combinations[cite: 35].
    2. Typically varies Margin, Fees, or Tenor regardless of the output result[cite: 35].
    3. MAX 30 variations allowed per batch for the ORC Simulation API.
    """
    # Example logic for ±3 levels on spread/margin
    base_spread = base_params.get("spread", 0)
    variations = []
    
    # Simple logic: create 7 variations (Base, -3, -2, -1, +1, +2, +3)
    for i in range(-3, 4):
        new_variant = base_params.copy()
        new_variant["spread"] = base_spread + (i * 0.05) # 5bps steps
        new_variant["variation_id"] = f"var_{i}"
        variations.append(new_variant)
        
    return {"variations_list": variations}

def run_orc_calculation(tool_context: ToolContext, api_payload: dict):
    """
    TASK: Integrate ORC Calculation API.

    DEVS:
    1. Accepts the fully-mapped API payload (already transformed from deal data via LLM reasoning).
    2. Validates the payload structure (optional: add JSON schema validation here).
    3. Executes the ORC Simulation API call with the provided payload.
    4. Returns RoRWA, Profit, and RWA results.

    INPUT: api_payload should be the complete JSON matching ORC API specification,
           with all placeholders already substituted by the Simulator agent.
    """
    import json

    # Log the received payload for debugging
    print("\n" + "="*70)
    print("🔍 API PAYLOAD RECEIVED BY run_orc_calculation")
    print("="*70)
    print(json.dumps(api_payload, indent=2))
    print("="*70 + "\n")

    # TODO: Add validation to ensure no {{placeholders}} remain unfilled
    payload_str = str(api_payload)
    if "{{" in payload_str or "}}" in payload_str:
        print("❌ ERROR: Payload contains unfilled placeholders!")
        return {
            "status": "error",
            "message": "Payload contains unfilled placeholders. Please ensure all template variables are substituted."
        }

    # MOCK RESPONSE: In production, this calls the ORC Simulation API
    # Example: response = requests.post(ORC_API_ENDPOINT, json=api_payload, headers=headers)

    # Mock calculation based on payload structure
    results = {
        "status": "success",
        "simulation_results": {
            "rorwa": 0.125,  # Mock value
            "profit": 50000.0,
            "rwa": 400000.0,
            "payload_received": api_payload  # For debugging
        }
    }

    print("✅ Simulation executed successfully")
    print(f"   RoRWA: {results['simulation_results']['rorwa']}")
    print(f"   Profit: ${results['simulation_results']['profit']:,.2f}")
    print(f"   RWA: ${results['simulation_results']['rwa']:,.2f}\n")

    return results
