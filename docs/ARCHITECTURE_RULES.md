# ARCHITECTURE RULES
# Vedic Astrology Intelligence System

These rules are absolute and must not be violated by any future implementation.

## 1. The Immutable D1 Rule
*   The D1 chart is the foundation of all karma.
*   Future engines (Varga, Transit, Dasha) **must never** overwrite or recalculate the D1 `final_score` or `breakdown` outputs.
*   All refinements must be safely injected into the `modifiers` or `temporal_activation` objects.

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

## 5. Standardized JSON Contract
*   Every engine must return the universally accepted output schema:
    *   `metadata` (entity_id, entity_type)
    *   `final_score` (immutable D1 promise)
    *   `breakdown` (explainable components)
    *   `modifiers` (additive structural points)
    *   `temporal_activation` (multiplicative timing scalars)
    *   `confidence_flags` (context strings)

## 6. Forbidden Patterns (DO NOT DO THIS)
*   **NO** AI black-box logic or LLM usage for astrological math/evaluations.
*   **NO** complex Object-Oriented inheritances (stick to simple Python dicts).
*   **NO** databases (system must run entirely in local memory/files).