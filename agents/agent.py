from google.agent_development_kit import LlmAgent
from tools.orchestrator_tools import (
    fetch_session_context, get_product_schema, 
    execute_field_derivation, validate_full_proposal
)
from tools.simulator_tools import (
    validate_simulation_inputs, generate_variation_parameters, 
    run_orc_calculation
)

# Specialist Agent
simulator_agent = LlmAgent(
    name="Simulator",
    instructions="Focus on generating sweeps and calling the ORC Calculation API.",
    tools=[validate_simulation_inputs, generate_variation_parameters, run_orc_calculation]
)

# Orchestrator Agent
portfolio_coordinator = LlmAgent(
    name="Portfolio Coordinator",
    instructions="""
    Identify product, validate inputs against schema, derive all Calc/Ref fields, 
    and perform pre-simulation validation before delegating to the Simulator.
    """,
    tools=[fetch_session_context, get_product_schema, execute_field_derivation, validate_full_proposal],
    sub_agents=[simulator_agent]
)
