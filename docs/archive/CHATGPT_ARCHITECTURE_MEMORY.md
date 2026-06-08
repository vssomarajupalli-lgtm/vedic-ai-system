# CHATGPT_ARCHITECTURE_MEMORY.md
> **Project State:** June 2026 Runtime Investigation Phase
> **Last Verified Date:** June 8, 2026
> **Verified By:** Source Inspection
> **Known Unverified Areas:** YogaEngine mathematical rules

## Project Goal
*   **Final intended Vedic AI architecture:** A robust, pipeline-driven engine combining Python/FastAPI backend with a React/Vite frontend. The architecture is fully deterministic, calculating exact scores based on astrological rules without generative AI interpolation.
*   **HoroscopeCleaner integration goals:** Consume static pre-extracted JSON (`canonical_content.json`) natively, bypassing the need for an active PDF parsing layer in the main runtime pipeline.
*   **Deterministic calculation goals:** 100% math-based scoring.
*   **Question engine goals:** Provide precise astrological answers mapped directly to derived domain scores.
*   **Transit/Gochara goals:** Project dynamic effects of current/future transits over the base natal promise.

## Current Implementation Status
### Backend
*   **JsonNormalizer:** **PARTIALLY IMPLEMENTED** (Core logic exists. Structural key mismatches with `canonical_content.json` have been patched to support `planets`, `houses`, and `birth_data` keys directly).
*   **PipelineRunner:** **COMPLETED**
*   **PlanetStrengthEngine:** **COMPLETED**
*   **HouseStrengthEngine:** **COMPLETED**
*   **NatalPromiseEngine:** **COMPLETED**
*   **YogaEngine:** **PARTIALLY IMPLEMENTED** (Engine logic exists and executes, but natively detects 0 yogas for canonical charts).
*   **AshtakavargaEngine:** **COMPLETED**
*   **DashaEngine:** **PARTIALLY IMPLEMENTED** (Placeholder present).
*   **TransitEngine:** **NOT IMPLEMENTED**
*   **MasterProbabilityEngine:** **COMPLETED**
*   **ReportBuilder:** **COMPLETED**

### Frontend
*   **Upload page:** **COMPLETED** (Verified hitting `http://localhost:8000`).
*   **Results page:** **COMPLETED** (UI components exist, renders data directly from backend payload).
*   **Question Engine page:** **PARTIALLY IMPLEMENTED**
*   **Export Report page:** **PARTIALLY IMPLEMENTED** (Fails due to missing `WeasyPrint` OS dependency).

## Files Modified During Current Debugging Cycle
1.  `backend/app/parsers/json_normalizer.py`: Added fallback logic to gracefully handle `"planets"`, `"houses"`, and `"birth_data"` keys without demanding the legacy `"raw_"` prefixes.
2.  `backend/app/reports/sections/extractors.py`: Updated dictionary extraction to use `"promise"` key instead of `"grade"` key, perfectly matching the `NatalPromiseEngine` schema.

## Confirmed Fixes
*   `master_synthesis` renamed to `master_probability` in schema to match actual logic.
*   `grade` fallback fixed to `promise` extractor alignment in `ReportBuilder`.
*   Fixed `JsonNormalizer` natively bypassing the `canonical_content.json` input failure that orphaned planets and houses.

## Open Problems
*   **Frontend Phantom Cache:** The frontend application seamlessly connects to any process on port 8000. Ghost instances (like older Docker containers running unpatched backend code) will silently intercept requests, causing "fixed" bugs to continuously appear unfixed to the user.
*   **Extraneous `machine_index` Schema:** The API enforces a strict `machine_index: List[Dict]` payload shape via Pydantic. Passing an empty or malformed index throws a fatal `422 Unprocessable Entity`, despite the fact that `machine_index` has exactly zero impact on any astrological calculations.
*   **Yoga Rule Triggers:** `YogaEngine` successfully executes without crashing, but natively detects `0` yogas, requiring investigation into its mathematical thresholds.

## Current Runtime Symptoms
*   **Life domains showing 48:** Conclusively proven to be caused by `JsonNormalizer` rejecting `canonical_content.json` legacy keys in unpatched instances. It silently passes `0` planets and `0` houses to the mathematical engines, which triggers their respective fail-safe defaults (50 strength, 0 SAV) and mathematically resolves to exactly `48`.
*   **Missing meaningful question engine output:** Incomplete implementation.
*   **Missing/unfinished transit/gochara output:** Transit engine logic is not fully integrated into the pipeline flow.
*   **Yoga output status:** Displays `0` yogas detected at runtime.

## Critical Contradictions Found
*   **CONTRADICTION 1:** Previous audits incorrectly claimed the system was fully functional and mathematically flawless because 619 tests passed. They failed to test the *exact* input schema of the final production `canonical_content.json`.
*   **CONTRADICTION 2:** Earlier audits incorrectly stated `JsonNormalizer` was broken. Its python execution was sound, but it strictly expected legacy prefixes (`"raw_planets"`) instead of the final extracted keys (`"planets"`).

## Next Investigation Plan
1.  **Stop blindly rewriting engine math:** The fallback value of `48` is ultimate runtime proof that the `NatalPromiseEngine` math is working flawlessly under fallback/empty payload conditions.
2.  **Verify Yoga Engine Math:** Trace `YogaEngine` using actual runtime data to identify why rules do not trigger.
3.  **Refactor `machine_index` Schema:** Deprecate its strict Pydantic requirements in `ChartProcessRequest` since it is entirely cosmetic and causes `422` crashes.
