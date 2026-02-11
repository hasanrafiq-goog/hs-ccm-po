from google.agent_development_kit import LlmAgent, Tool, ToolContext
import json
import os

# --- TOOL IMPLEMENTATIONS FOR PORTFOLIO COORDINATOR ---

def get_product_schema(tool_context: ToolContext, product_type: str):
    """
    TASK: Dynamic Schema Retrieval.
    
    DEVS: 
    1. Query the './schemas/' directory for the corresponding JSON file. [cite: 112]
    2. Provide mandatory fields and reference value sets to the agent for gap analysis. [cite: 98, 99]
    """
    # In production, this would load from the local 'schemas' folder [cite: 112]
    return {
        "mandatory_fields": ["client_id", "notional", "currency", "sector", "base_rate", "spread"],
        "reference_data": {
            "currency": ["USD", "GBP", "EUR"],
            "sector": ["TMT", "Energy", "Retail"]
        }
    }

def execute_field_derivation(tool_context: ToolContext, raw_inputs: dict):
    """
    TASK: Unified Truth Engine (Calc + Ref).
    
    DEVS:
    1. This is the single Python function handling all non-input data. 
    2. Perform Reference Mapping (e.g., Sector -> Risk Code). [cite: 114]
    3. Perform Mathematical Calculations (e.g., All-in-Rate). 
    """
    enriched_data = raw_inputs.copy()
    
    # 1. Reference Derivation (Non-calculated) [cite: 114]
    sector_map = {"TMT": "RC-101", "Energy": "RC-202", "Retail": "RC-303"}
    enriched_data["risk_rating_code"] = sector_map.get(raw_inputs.get("sector"), "RC-GEN")
    
    # 2. Mathematical Derivation (Calculated) [cite: 114]
    base = float(raw_inputs.get("base_rate", 0))
    spread = float(raw_inputs.get("spread", 0))
    enriched_data["all_in_rate"] = base + spread
    
    return enriched_data

def validate_full_proposal(tool_context: ToolContext, proposal_data: dict):
    """
    TASK: Pre-Simulation Validation Gate.
    
    DEVS: 
    1. Call the 'ORC Validation API (Simulation)' endpoint. 
    2. Check mandatory fields and reference value formats after derivation. [cite: 105, 111]
    3. Ensure data typing (floats, strings) is strictly aligned with the ORC Simulate API. 
    """
    # HTTP POST to ORC Simulate Validation endpoint 
    return {"status": "validated", "context": "ready_for_simulation"}

def fetch_session_context(tool_context: ToolContext):
    """
    TASK: Maintain continuity of deal parameters. [cite: 97, 109]
    """
    return tool_context.state.get('current_deal_params', {})


# --- TOOL IMPLEMENTATIONS FOR SIMULATOR ---

def validate_simulation_inputs(tool_context: ToolContext, parameters: dict):
    """
    TASK: 'Lite' Validation for Calculation. [cite: 123, 127]
    """
    return {"status": "valid"}

def run_orc_calculation(tool_context: ToolContext, parameters: dict):
    """
    TASK: Integrate ORC Calculation API. [cite: 128]
    """
    return {"rorwa": 0.125, "profit": 50000.0, "rwa": 400000.0}

def generate_variation_parameters(tool_context: ToolContext, base_params: dict):
    """
    TASK: Configure Simulator for Type 1 Sweep (±3 levels). [cite: 124, 129]
    """
    return {"variations_list": []}


# --- AGENT SETUP (ADK LLM AGENTS) ---

# Simulator: The math specialist [cite: 115, 116]
simulator_agent = LlmAgent(
    name="Simulator",
    instructions="""
    You are the ORC Simulation Specialist. 
    Focus: Calculating RoRWA and generating 'What-If' scenarios. [cite: 124, 125]
    Constraint: You only vary a maximum of 3 parameters at a time. [cite: 129]
    Logic: Always run 'validate_simulation_inputs' before calling 'run_orc_calculation'. [cite: 123, 128]
    """,
    tools=[validate_simulation_inputs, run_orc_calculation, generate_variation_parameters]
)

# Portfolio Coordinator: The Orchestrator [cite: 92, 93]
portfolio_coordinator = LlmAgent(
    name="Portfolio Coordinator",
    instructions="""
    You are the lead orchestrator for the Pricing AI Assist. [cite: 93]
    Goal: Manage the data journey from RM input to Simulation. [cite: 105]

    Step 1: Identify product_type and use 'get_product_schema' to retrieve requirements. 
    Step 2: Compare RM inputs to the schema. If fields are missing or reference values (Sector/Currency) 
            are invalid, interactively ask the RM to correct them. [cite: 99]
    Step 3: Once inputs are complete, call 'execute_field_derivation' to perform all Calc/Ref math. 
    Step 4: Run 'validate_full_proposal' to ensure the enriched JSON is ready for Simulation. [cite: 105, 111]
    Step 5: Delegate to the Simulator for the Type 1 Parametric Sweep. [cite: 95]
    """,
    tools=[get_product_schema, execute_field_derivation, validate_full_proposal, fetch_session_context],
    sub_agents=[simulator_agent] 
)
