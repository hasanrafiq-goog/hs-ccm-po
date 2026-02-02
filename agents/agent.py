from google.agent_development_kit import LlmAgent, Tool, ToolContext

# --- TOOL IMPLEMENTATIONS FOR PORTFOLIO COORDINATOR ---

def validate_full_proposal(tool_context: ToolContext, proposal_data: dict):
    """
    TASK: Implement 'Full Validation' for Save Logic.
    
    DEVS: 
    1. Call the 'ORC Validation API (Save)' endpoint.
    2. Ensure ALL mandatory banking fields from the 'ORC Save API' schema are present.
    3. If valid, set tool_context.state['full_validation_passed'] = True to unlock the Advisor's Save tool.
    4. Reference the 'JSON payload structure' prerequisite for field naming conventions.
    """
    # TODO: Perform HTTP POST to ORC Validation API
    return {"status": "validated", "proposal_id_context": "ready_for_save"}

def fetch_session_context(tool_context: ToolContext):
    """
    TASK: Check Context Handling.
    
    DEVS:
    1. Retrieve the current 'active' deal parameters from tool_context.state.
    2. This ensures continuity (e.g., if RM says 'change only the margin', 
       we keep the Amount and Tenor from the previous turn).
    """
    return tool_context.state.get('current_deal_params', {})

def search_proposal_records(tool_context: ToolContext, query: str):
    """
    TASK: Historical Deal Query.
    
    DEVS:
    1. Query the ORC backend for existing Proposal IDs or historical client deals.
    2. Use this to pre-populate one of the '2 JSON variations' for the base deal.
    """
    # TODO: Backend search logic
    return {"historical_deals": []}


# --- TOOL IMPLEMENTATIONS FOR SIMULATOR ---

def validate_simulation_inputs(tool_context: ToolContext, parameters: dict):
    """
    TASK: 'Lite' Validation for Calculation.
    
    DEVS:
    1. Call 'ORC Validation API (Calculation)'.
    2. Only check 'math' fields: Margin, Fees, Tenor. 
    3. Skip 'Full Save' fields like Sector or Legal Entity to save latency.
    """
    return {"status": "valid"}

def run_orc_calculation(tool_context: ToolContext, parameters: dict):
    """
    TASK: Integrate ORC Calculation API.
    
    DEVS:
    1. Base Deal: Pass the single JSON object to the Calculation API.
    2. Advanced: If parameters contain a list, execute parallel/batch calls.
    3. Return RoRWA, Profit, and RWA values back to the agent for the RM.
    """
    # TODO: HTTP POST to ORC Calculation API
    return {"rorwa": 0.0, "profit": 0.0, "rwa": 0.0}

def generate_variation_parameters(tool_context: ToolContext, base_params: dict):
    """
    TASK: Configure Simulator for 3-Parameter Matrix.
    
    DEVS:
    1. Refer to 'Parameter Priority List' prerequisite (e.g., Margin, Fee, Tenor).
    2. Use 'Variation Logic Rules' (e.g., Margin ± 5bps) to create the matrix.
    3. MAX 3 parameters allowed; if more are provided, error out or prioritize top 3.
    """
    # TODO: Loop through the 3 parameters and generate the JSON variation list
    return {"variations_list": []}


# --- AGENT SETUP (ADK LLM AGENTS) ---

# Simulator: The math specialist
simulator_agent = LlmAgent(
    name="Simulator",
    instructions="""
    You are the ORC Simulation Specialist. 
    Focus: Calculating RoRWA and generating 'What-If' scenarios.
    Constraint: You only vary a maximum of 3 parameters at a time.
    Logic: Always run 'validate_simulation_inputs' before calling 'run_orc_calculation'.
    """,
    tools=[validate_simulation_inputs, run_orc_calculation, generate_variation_parameters]
)

# Coordinator: The RM's entry point and gatekeeper
portfolio_coordinator = LlmAgent(
    name="Portfolio Coordinator",
    instructions="""
    You are the lead orchestrator for the Pricing AI Assist.
    Goal: Manage Base Deal creation and Advanced Structuring.
    1. Use 'search_proposal_records' to find existing data.
    2. Extract parameters from the RM's message to populate the 2 JSON variations.
    3. If the user wants to SAVE, you MUST run 'validate_full_proposal'.
    4. If the user wants to COMPARE or OPTIMIZE, delegate to the Simulator.
    """,
    tools=[validate_full_proposal, fetch_session_context, search_proposal_records],
    sub_agents=[simulator_agent] # Goal Seeker/Advisor added in later phases
)
