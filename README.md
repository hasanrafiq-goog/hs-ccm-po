# README: Pricing AI Assist - Multi-Agent CCM ORC

## Project Overview
The Pricing AI Assist is a multi-agent system designed for Relationship Managers (RMs) to streamline deal structuring, validation, and optimization within the Credit Capacity Management (CCM) and ORC frameworks. The system uses a hierarchical agent architecture to separate conversational flow from rigorous financial validation, leveraging Google's Agent Development Kit (ADK).

---

## Core Architecture
The application follows an Orchestrator-Specialist pattern, ensuring high-stakes banking decisions remain auditable and grounded in backend reality.

### Architecture Innovation: Schema-Driven Payload Mapping
This system implements a novel **Schema-in-JSON** architecture where:
1. **Product schemas contain both validation rules AND API payload templates** in a single JSON file
2. **The LLM performs intelligent payload mapping** by reading templates with placeholders like `{{field_name}}`, `{{spread * 100}}`, or `{{field == 'Yes' ? true : false}}`
3. **No hard-coded field-by-field transformation logic** - the model reasons through complex nested structures
4. **Product-agnostic tools** - adding new products only requires new JSON schemas, not code changes

### 1. Portfolio Coordinator (The Orchestrator)
**Role**: The lead agent managing the user journey and high-level logic.

**Responsibilities**:
* **Intent Classification**: Detects if a request is for a base deal "Save/Create" or a "What-If" simulation
* **Schema Discovery**: Retrieves product-specific schemas containing:
  - `schema_details`: Validation rules, mandatory fields, reference data, derivation targets
  - `target_api_payload`: API payload template with placeholders for intelligent mapping
* **Dynamic Validation**: Real-time gap analysis against schema, prompting RM for missing/invalid fields
* **Field Derivation**: Orchestrates transformation of raw inputs into complete deal objects (reference mappings + calculations)
* **HITL Gatekeeping**: Presents variation lists to RM for approval before execution
* **State Management**: Maintains `tool_context.state` for progressive parameter collection across conversation turns
* **Full Validation**: Acts as the gatekeeper, ensuring all mandatory fields are valid before simulation

**Key Tools**:
* `get_product_schema_tool` - Retrieves product configuration (schema + API template)
* `execute_field_derivation` - Derives calculated and reference-mapped fields
* `validate_full_proposal` - Validates against schema_details rules
* `fetch_session_context` - Retrieves ongoing deal state

### 2. Simulator (The Calculation Specialist)
**Role**: The exclusive technical hub for mathematical modeling and API interaction.

**Responsibilities**:
* **Lite Validation**: Rapid checks on mathematical levers (Margin, Fees, Notional) required for simulation
* **Type 1 Parametric Sweep**: Generates ±3 level variation matrix (max 30 variations per batch)
* **Intelligent Payload Mapping**:
  - Reads `target_api_payload` template from schema
  - Substitutes placeholders with actual deal data
  - Handles calculations: `{{spread * 100}}` → converts 0.025 to 2.5
  - Handles conditionals: `{{syndication_flag == 'Yes' ? true : false}}` → true/false
  - Generates complete, nested JSON payloads without hard-coded logic
* **Parallel Execution**: Manages batch requests to ORC Simulation API
* **Hallucination Prevention**: Only uses fields that exist in deal data or template logic

**Key Tools**:
* `validate_simulation_inputs` - Validates simulation-specific parameters
* `generate_variation_parameters` - Creates Type 1 Sweep variation matrix
* `run_orc_calculation` - Accepts fully-mapped payload and calls ORC API

---

## Product Schemas (Schema-in-JSON Architecture)

### Schema Structure
Each product JSON (`loan.json`, `cocredit.json`) contains:

```json
{
  "product_type": "Term Loan",
  "schema_details": {
    "fields_definition": {
      "field_name": {
        "type": "currency|percentage|date|reference|...",
        "format": "float|string|YYYY-MM-DD|...",
        "mandatory": true|false,
        "min": <optional_min_value>
      }
    },
    "reference_data": {
      "field_name": ["allowed", "values", "list"]
    },
    "derivation_targets": {
      "reference_mapped": ["field1", "field2"],
      "calculated": ["field3", "field4"]
    }
  },
  "target_api_payload": {
    "field_name": "{{placeholder}}",
    "calculated_field": "{{field * 100}}",
    "conditional_field": "{{flag == 'Yes' ? true : false}}",
    "facility_limits": [
      {
        "limit": "{{notional}}",
        "rate": "{{spread * 100}}"
      }
    ]
  }
}
```

### Currently Supported Products
1. **Term Loan** (`loan.json`)
2. **Revolving Credit / CoCredit** (`cocredit.json`)

---

## Current Development Scope

### Epic 1: Base Deal Scenario Creation & Management
**Goal**: Enable RMs to input parameters for a deal through conversational interface

**Features**:
- Progressive parameter collection across multiple conversation turns
- Real-time validation against product-specific schemas
- Automatic field derivation (reference mappings + calculations)
- State persistence in `tool_context.state`
- Dynamic payload generation from templates

**Output**: Validated deal object ready for simulation

### Epic 2: Advanced Deal Structuring
**Goal**: Optimize for financial metrics (RoRWA, Profit, RWA)

**Type 1 - Parametric Sweep**:
- Fixed ±3 level variations on up to 3 parameters
- Max 30 variations per batch
- Parallel execution for simultaneous results

**Type 2 - Smart Goal Seek** (Future):
- Iterative optimization to hit target metrics
- Intelligent parameter adjustment based on results

**Constraint**: Maximum 3 parameters varied per request

---

## Evaluation & Grounding (The "Source of Truth")
To prevent hallucinations and ensure accuracy, the system implements:

**Schema-Driven Validation**:
- All validations are driven by `schema_details` in product JSONs
- Reference data ensures only allowed values are accepted
- Mandatory field checks prevent incomplete deals

**Payload Validation**:
- `run_orc_calculation` tool validates no `{{placeholders}}` remain unfilled
- LLM instructions explicitly prohibit hallucinating field names
- Only fields from deal data or template logic are used

**Two-Layer Validation**:
- **Full Validation** (Portfolio Coordinator): Pre-simulation check of all banking fields
- **Lite Validation** (Simulator): Rapid check of calculation-specific parameters

**Math Fidelity**:
- Derivation logic is deterministic (Python functions)
- Template expressions clearly define transformations
- Simulator output benchmarked against verified scenarios

---

## Session State & Shared Logic

**State Management**:
- `tool_context.state` acts as shared whiteboard between agents
- `current_deal_params` stores progressive parameter collection
- Portfolio Coordinator updates state as RM provides inputs
- Simulator reads state to perform payload mapping

**Agent Communication**:
- Portfolio Coordinator passes validated deal data + schema to Simulator
- Simulator performs intelligent mapping and returns results
- State persists across conversation turns for incremental deal building

**Workflow Benefits**:
- RM can provide parameters across multiple messages
- Missing fields are identified and requested dynamically
- "What-If" scenarios build on validated base deal

---

## Implementation Status

### ✅ Completed
- [x] Schema-in-JSON architecture (schema_details + target_api_payload)
- [x] Product schemas for Loan and CoCredit
- [x] Portfolio Coordinator agent with 7-step workflow
- [x] Simulator agent with intelligent payload mapping
- [x] Schema retrieval tool (`get_product_schema_tool`)
- [x] Field derivation tool (`execute_field_derivation`)
- [x] Full validation tool (`validate_full_proposal`)
- [x] Session context tool (`fetch_session_context`)
- [x] Simulation tools (validate, generate variations, run calculation)
- [x] Payload placeholder validation (prevents unfilled templates)

### 🚧 In Progress / Future
- [ ] Goal Seeker agent (Type 2 optimization)
- [ ] Advisor agent (strategic narrative and synthesis)
- [ ] ORC Simulation API integration (currently mocked)
- [ ] ORC Save API integration
- [ ] ADK runner and test scripts
- [ ] Multi-facility deal support
- [ ] HITL approval flow implementation

## Technical Prerequisites
* **ORC Simulation API**: Endpoint for RoRWA, Profit, and RWA calculations
* **ORC Save API**: Endpoint for deal persistence (future)
* **Product Schemas**: JSON files defining validation rules and API payload templates
* **Google ADK**: Agent Development Kit for multi-agent orchestration

## File Structure
```
hs-ccm-po/
├── agents/
│   └── agent.py                 # Portfolio Coordinator & Simulator agents
├── tools/
│   ├── tools_coordinator.py     # Schema, validation, derivation tools
│   └── simulator_tools.py       # Simulation-specific tools
├── schema/
│   ├── loan.json               # Term Loan product schema
│   └── cocredit.json           # Revolving Credit product schema
└── README.md                   # This file
```
