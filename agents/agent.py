from google.agent_development_kit import LlmAgent
from tools.tools_coordinator import (
    get_product_schema_tool, 
    execute_field_derivation, 
    validate_full_proposal, 
    fetch_session_context
)
from tools.tools_simulator import (
    validate_simulation_inputs, 
    generate_variation_parameters, 
    run_orc_calculation
)

# --- SIMULATOR AGENT ---
simulator_agent = LlmAgent(
    name="Simulator",
    instructions="""
    You are the Technical Specialist for the ORC Simulation API.
    
    Role & Workflow:
    1. Receive a validated deal object from the Portfolio Coordinator.
    2. Run 'validate_simulation_inputs' to check mathematical levers (Margin, Fees)[cite: 34, 38].
    3. Call 'generate_variation_parameters' to create the ±3 level matrix for a Type 1 Sweep[cite: 35, 40].
    4. Execute 'run_orc_calculation' to fetch results from the ORC API[cite: 37, 39].
    5. Present the simulation results (RoRWA, Profit, RWA) back to the Coordinator[cite: 37, 39].
    """,
    tools=[validate_simulation_inputs, generate_variation_parameters, run_orc_calculation]
)

# --- PORTFOLIO COORDINATOR AGENT ---
portfolio_coordinator = LlmAgent(
    name="Portfolio Coordinator",
    instructions="""
    You are the Lead Orchestrator. Your goal is to guide the Relationship Manager (RM) from a query to a validated simulation[cite: 3, 4, 6].

    Strict Procedural Workflow:
    Step 1: Context Retrieval - Call 'fetch_session_context' to see if there's an ongoing deal.
    Step 2: Schema Discovery - Once a product (Loan/Credit) is identified, call 'get_product_schema_tool' to get the mandatory fields and allowed values[cite: 9, 23].
    Step 3: Gap Analysis & HITL - Compare RM inputs against the schema. If fields are missing or reference values are invalid, ask the RM to provide them[cite: 10, 14].
    Step 4: Unified Derivation - Once inputs are complete, call 'execute_field_derivation' to generate all Calc and Ref fields (Risk Codes, All-in-Rate, etc.).
    Step 5: Quality Gate - Run 'validate_full_proposal' using the derived data and schema. If it returns 'rejected' with errors, report those errors to the RM for correction.
    Step 6: Delegation - Only after 'validated' status is received, delegate to the 'Simulator' for the Type 1 Sweep[cite: 21, 26].
    """,
    tools=[
        get_product_schema_tool, 
        execute_field_derivation, 
        validate_full_proposal, 
        fetch_session_context
    ],
    sub_agents=[simulator_agent]
)
