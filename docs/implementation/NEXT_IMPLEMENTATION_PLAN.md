# NEXT IMPLEMENTATION PLAN

This document organizes the remaining implementation work identified in the Gap Analysis and Boundary Validation reports into a structured execution order. 

**Smallest Safe Implementation**: Task 1 (Question Engine Boundary Fix) is the smallest safe implementation that can be completed immediately to secure the architecture before building new modules.

---

## 1. Quick Wins (Low Complexity, High Structural Value)

### Task 1: Fix `QuestionEngine` Boundary Violation (DR-007)
*   **File(s) Affected**: `backend/app/engines/question_engine.py`, `backend/app/pipeline_runner.py`
*   **Dependencies**: None.
*   **Estimated Complexity**: Low
*   **Risks**: Minor risk of breaking tests that assume `QuestionEngine` runs in isolation.
*   **Validation Requirements**: Ensure `QuestionEngine` no longer imports `MasterProbabilityEngine`. Verify that `PipelineRunner` successfully coordinates the question routing and probability re-evaluation without throwing dependency errors.

### Task 2: Implement Functional Nature (Ascendant Layer)
*   **File(s) Affected**: `backend/app/engines/planet_strength_engine.py` (or new `functional_nature_engine.py`), `backend/app/pipeline_runner.py`
*   **Dependencies**: Data Layer (`normalized_payload["metadata"]`).
*   **Estimated Complexity**: Low
*   **Risks**: Could alter downstream `final_score` distributions for planets.
*   **Validation Requirements**: Verify that planets acting as functional benefics/malefics based on Lagna (e.g., Mars for Cancer Lagna) receive correct modifiers.

---

## 2. Medium Complexity (Missing Logical Blocks)

### Task 3: Build & Integrate `DoshaEngine`
*   **File(s) Affected**: `backend/app/engines/dosha_engine.py` (NEW), `backend/app/pipeline_runner.py`
*   **Dependencies**: `PlanetStrengthEngine`, `HouseStrengthEngine`.
*   **Estimated Complexity**: Medium
*   **Risks**: Kuja Dosha (Manglik) logic has many classical exceptions. Implementing it without exceptions could lead to false positives. 
*   **Validation Requirements**: Unit tests for Kuja Dosha, Kala Sarpa Dosha, and Pitru Dosha. Verify that detecting a dosha correctly penalizes the associated domain probability (e.g., Marriage).

### Task 4: Refactor `DashaEngine` to Pure Extraction (DR-001)
*   **File(s) Affected**: `backend/app/engines/dasha_engine.py`
*   **Dependencies**: `canonical_content.json` schema updates.
*   **Estimated Complexity**: Medium
*   **Risks**: Modifying Dasha temporal multipliers could cause large shifts in final prediction probabilities.
*   **Validation Requirements**: Ensure engine performs zero mathematical prediction. Verify it strictly reads the active Mahadasha/Antardasha from canonical data and correctly outputs temporal confidence multipliers for downstream engines.

---

## 3. Major Modules (Heavy Data / Core Subsystems)

### Task 5: Implement Transit Engine (Gochara System)
*   **File(s) Affected**: `backend/app/engines/transit_engine.py`
*   **Dependencies**: `canonical_content.json` (for extracted Phalithalu), `ephemeris_service.py`, `AshtakavargaEngine`, `NatalPromiseEngine`.
*   **Estimated Complexity**: High
*   **Risks**: Largest remaining subsystem. High risk of over-engineering or violating DR-003 if we calculate too much Ephemeris math instead of extracting pre-existing source data.
*   **Validation Requirements**: Validate that Transit activation correctly influences the Master Probability score without overwriting the Natal Promise. Verify fallback mechanisms if `canonical_content.json` is missing transit data.

### Task 6: Implement Remedy Engine
*   **File(s) Affected**: `backend/app/engines/remedy_engine.py` (NEW), `backend/app/pipeline_runner.py`
*   **Dependencies**: `DoshaEngine`, `NatalPromiseEngine`, `MasterProbabilityEngine`.
*   **Estimated Complexity**: High
*   **Risks**: Mapping specific astrological afflictions to correct classical remedies requires high domain accuracy.
*   **Validation Requirements**: Verify that severe chart afflictions (e.g., low Health domain promise) successfully trigger the generation of appropriate remedy suggestions in the final output.
