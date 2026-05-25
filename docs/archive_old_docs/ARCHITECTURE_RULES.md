# ARCHITECTURE RULES
# Vedic Astrology Intelligence Framework

These rules are absolute and must not be violated by any future implementation.

## 1. The Immutable D1 Rule
*   The D1 chart is the foundation of all karma.
*   Future engines (Varga, Transit, Dasha) **must never** overwrite or recalculate the D1 `final_score` or `breakdown` outputs.
*   All refinements must be safely injected into the `modifiers` or `temporal_activation` objects.
*   **Immutability Enforcement:** The `PipelineRunner` MUST use `types.MappingProxyType` when injecting dependencies to guarantee downstream engines receive read-only data.

## 2. Stateless Engine Rules
*   Engines must not retain memory or hidden states between requests.
*   Engines accept a normalized dictionary, perform calculations, and return a dictionary.
*   No cross-talk allowed: Engine A must never import or directly call Engine B.

## 3. Pipeline & Dependency Rules
*   The architecture executes strictly via the `PipelineRunner` (unidirectional DAG).
*   If an engine requires data from a previous calculation (e.g., House Engine needs the Lord's Planet Score), the `PipelineRunner` is responsible for safely extracting and injecting that dependency.

## 4. Deterministic Scoring Rules
*   All astrological logic and scoring weights must be mapped in `astrology_constants.py`.
*   No "magic numbers" hardcoded in engine files.
*   All mathematical adjustments must be 100% explainable via the output JSON breakdown.
*   Calculations must always clamp to safe boundaries (e.g., final scores clamp strictly between 0 and 100).
*   **Declarative Rules:** Future scaling MUST avoid "if-else explosions" by routing logic through declarative rule packets and registries.

## 5. Layered JSON Contracts & Governance
*   The system uses strict Layered Contracts:
    *   **Type A:** Static Entities (Planets, Houses, Vargas).
    *   **Type B:** Temporal Matrices (Dashas, Transits).
    *   **Type C:** Synthesis/Event Outputs.
*   **Schema Governance:** Schema drift is forbidden. Changing a core contract requires an explicit version increment in `JSON_CONTRACT_MASTER.md`.

## 6. Event Domain Abstraction
*   The Synthesis Engine MUST NOT hardcode raw astrological logic (e.g., `if sun > 50 and 10th_house > 50`). 
*   Prediction logic must be abstracted into Event Domains (e.g., "Career", "Marriage") representing configuration mappings that the Synthesis Engine consumes deterministically.

## 7. Forbidden Patterns (DO NOT DO THIS)
*   **NO** AI black-box logic or LLM usage for astrological math/evaluations.
*   **NO** complex Object-Oriented inheritances (stick to simple Python dicts).
*   **NO** databases (system must run entirely in local memory/files).