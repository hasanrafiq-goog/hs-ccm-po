# README: Pricing AI Assist - Multi-Agent CCM ORC

## Project Overview
The Pricing AI Assist is a multi-agent system designed for Relationship Managers (RMs) to streamline deal structuring, validation, and optimization within the Credit Capacity Management (CCM) and ORC frameworks [cite: 1.1, 5.1]. The system uses a hierarchical agent architecture to separate conversational flow from rigorous financial validation [cite: 1.2, 3.4].

---

## Core Architecture
The application follows an Orchestrator-Specialist pattern, ensuring high-stakes banking decisions remain auditable and grounded in backend reality [cite: image_7fee5d.png, 1.2].

### 1. Portfolio Coordinator (The Orchestrator)
* Role: The lead agent managing the user journey and high-level logic [cite: 1.2].
* Responsibilities:
    * Intent Classification: Detects if a request is for a base deal "Save/Create" or a "What-If" simulation [cite: 1.2, 4.2].
    * Full Validation: Acts as the gatekeeper for deal persistence, ensuring all mandatory system fields are valid before a save occurs [cite: 3.3, 5.3].
    * Context Management: Maintains session state to ensure parameters are carried forward across multiple turns [cite: 1.1, 4.4].
* Key Tools: validate_full_proposal, fetch_session_context, search_proposal_records [cite: image_7fee5d.png, 3.2].

### 2. Simulator (The Calculation Specialist)
* Role: The exclusive technical hub for mathematical modeling and API interaction [cite: 1.4, 5.2].
* Responsibilities:
    * Lite Validation: Performs rapid mathematical boundary checks on levers (Margin, Fees, Tenor) prior to calling calculation services [cite: image_7fee5d.png, 5.3].
    * Type 1 Sweep: Generates a matrix of variations based on a maximum of 3 parameters [cite: image_1146fb.png, 1.2].
    * Parallel Execution: Manages batch requests to the calculation engine to return multiple results simultaneously [cite: 5.2].
* Key Tools: validate_simulation_inputs, run_orc_calculation, generate_variation_parameters [cite: image_7fee5d.png, 3.2].

---

## Current Development Scope
The current roadmap is prioritized into two core Epics with restricted scope for maximum delivery velocity [cite: image_1146fb.png]:

### Epic 1: Base Deal Scenario Creation & Management
* Goal: Enable RMs to input parameters for a simple scenario using 2 JSON variations [cite: image_1146fb.png].
* Output: Successfully calculate initial returns and save the base deal parameters to generate a unique tracking ID [cite: image_1146fb.png, 5.2].

### Epic 2: Advanced Deal Structuring
* Goal: Optimize for financial metrics (RoRWA, Profit, RWA) [cite: image_1146fb.png, 1.4].
* Constraint: The AI is strictly limited to varying a maximum of 3 parameters per request [cite: image_1146fb.png].

---

## Evaluation & Grounding (The "Source of Truth")
To prevent hallucinations and ensure math accuracy, the agents follow these principles [cite: image_1146fb.png]:
* Ground Truth Check: LLM parameter extraction is benchmarked against a verified dataset of RM queries [cite: image_1146fb.png].
* Math Fidelity: The Simulator's output must match "Golden Scenarios" verified by manual calculation [cite: image_1146fb.png, 5.3].
* Hallucination Monitoring: Periodic audits ensure no deal parameters are "invented" by the LLM during the JSON generation process [cite: image_1146fb.png].

---

## Session State & Shared Logic
* Shared Whiteboard: All agents read from/write to session.state to ensure the "What-If" scenarios are based on the latest validated data [cite: 1.1, 4.4].
* Two-Layer Validation: Full deal validation happens in the Coordinator (Save Logic); lightweight calculation validation happens in the Simulator (Calculation Logic) [cite: image_7feaf8.jpg, 5.3].

---

## Technical Prerequisites Checklist
* [ ] ORC Save API: Endpoints for deal persistence [cite: image_1146fb.png].
* [ ] ORC Calculation API: Endpoints for RoRWA and Profit math [cite: image_1146fb.png].
* [ ] ORC Validation APIs: For both "Save" (Full) and "Calculation" (Lite) checks [cite: image_1146fb.png].
* [ ] JSON Schema: Detailed payload structures for the 2 variations [cite: image_1146fb.png].
