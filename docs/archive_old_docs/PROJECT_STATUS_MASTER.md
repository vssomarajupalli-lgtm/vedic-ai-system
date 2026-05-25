# PROJECT STATUS MASTER
# Vedic Astrology Intelligence Framework

**Purpose:** This document is the persistent, long-term implementation memory and governance layer for the framework. It serves as the primary stabilization reference for AI-assisted development to ensure deterministic architectural continuity.

---

## 1. Current Stable Project Tree
```text
vedic-ai-system/
├── docs/                                 # Centralized architecture rules and project context
├── sample_reports/                       # PDF inputs for dev/testing
├── source_pdfs/                          # Production PDF inputs
├── extracted_json/                       # Intermediate extraction outputs
├── outputs/                              # Final system deliverables
└── backend/
    ├── requirements.txt                  # Python dependencies (e.g., pyswisseph)
    ├── run.py                            # Main execution entry point
    ├── app/                              # Core application package
    │   ├── __init__.py
    │   ├── pipeline_runner.py            # Central orchestrator (Unidirectional DAG)
    │   ├── config/                       # Deterministic rules (astrology_constants.py)
    │   ├── engines/                      # Stateless calculation modules
    │   │   ├── house_strength_engine.py
    │   │   ├── planet_strength_engine.py
    │   │   └── varga_engine.py
    │   ├── parsers/                      # Extraction & JSON Normalization
    │   └── utils/                        # Shared math & Ephemeris services
    └── tests/                            # Global regression testing suite
```

## 2. Completed Implementation Phases
*   **Phase 1 & 2 (Foundation):** JSON Schema design and `JsonNormalizer` implemented to enforce data safety, defaults, and type correctness.
*   **Phase 3 & 4 (D1 Foundation):** `PlanetStrengthEngine` and `HouseStrengthEngine` implemented to evaluate immutable 0-100 base scores.
*   **Phase 5 (Structural Refinement):** `VargaEngine` implemented to calculate structural capacity modifiers (e.g., Vargottama) without overwriting D1.
*   **Orchestration:** `PipelineRunner` implemented to handle unidirectional data handoffs safely.
*   **Stabilization:** Project tree cleaned, package `__init__.py` files added, and math utilities centralized.

## 3. Stabilized Architecture Philosophy
*   **Dual Workflow Support:** The framework supports both PDF-driven extraction workflows and Direct Normalized JSON/API workflows. The extraction layer is purely optional.
*   **Stateless Engines:** No engine retains memory between requests. They accept a normalized dictionary, calculate, and return a dictionary.
*   **Unidirectional DAG:** Data flows strictly forward. Engines never call each other. All dependencies are passed via the `PipelineRunner`.
*   **The Immutable D1 Rule:** The D1 chart is the foundation of karma. Engines evaluating Vargas, Dashas, or Transits must *never* overwrite D1. 
*   **Immutability Enforcement:** The `PipelineRunner` must enforce this programmatically using Python `MappingProxyType` to create read-only dependency injections.
*   **Layered JSON Contracts:** Entities use strict, versioned contracts (Type A for static entities, Type B for temporal matrices, Type C for synthesis probabilities).

## 4. Deterministic Scoring Philosophy
*   **Zero Magic Numbers:** Every astrological weight (e.g., Exalted = +35) lives exclusively in `app/config/astrology_constants.py`.
*   **No AI in Math:** The mathematical calculations are strict, deterministic Python logic. AI is strictly forbidden from "guessing" scores.
*   **Safe Boundaries:** Every engine utilizes `clamp_score()` from `astrology_math.py` to ensure final percentages never exceed 0-100 limits.
*   **100% Explainability:** Every point added or subtracted is recorded in the `breakdown` dictionary. 
    * *Future Evolution:* To support advanced tracing without breaking simplicity, breakdowns will evolve into structured rule packets with trace metadata (engine version, rule category).
*   **Declarative Rules (Future-Proofing):** To avoid future if-else explosions, complex logic will evolve into Declarative Rule Packets evaluated by standardized registries.

## 5. Modifier Philosophy
*   **Structural Modifiers (Capacity):** Vargas evaluate the *quality* of the chart. These are mathematically **additive** (e.g., +15 points).
*   **Temporal Modifiers (Activation):** Dashas and Transits dictate *when* an event triggers. These are mathematically **multiplicative** (e.g., 1.25x).
*   **Confidence Flags:** Engines append string context (e.g., `"varga_contradicted"`) to translate raw math into context for future AI layers.

## 6. Ashtakavarga Architecture Position
*   **Independent Matrix Subsystem:** Ashtakavarga is NOT a flat structural modifier. It will be architected as an independent Matrix/Reinforcement Subsystem that acts as a lookup filter for Transits and House manifestation.

## 7. Dasha & Transit Philosophy (Upcoming)
*   **Dashas (The Window):** The broad baseline activation multiplier (e.g., "Jupiter period is active, applying 1.2x multiplier to 9th house matters").
*   **Transits (The Spark):** The short-term temporary trigger multiplier applied on top of the Dasha baseline. Evaluated dynamically via discrete Ephemeris snapshots.
*   **Independence:** The Transit engine does not need to know the Dasha engine's internal logic. Both independently write to `temporal_activation`.

## 8. Event Domain & Synthesis Philosophy (Upcoming Phase 8)
*   **Event Domain Abstraction:** To prevent tightly-coupled synthesis chaos, predictions are grouped into Event Domains (e.g., Career, Marriage). These domains sit strictly between Engine Outputs and Synthesis, acting as configuration mappings (e.g., Career = House 10 + Sun + D10).
*   **Probability Synthesis Engine:** The ultimate intelligence layer. It aggregates deterministic scores, applies temporal multipliers based on Event Domains, and calculates final manifestation probabilities. AI must NEVER alter these mathematical outputs.

## 9. Shared Utility Philosophy
*   **Centralized Logic:** Astrological math that is used across multiple engines (like calculating axis relationships `calculate_planetary_axis` or clamping scores `clamp_score`) lives in `app/utils/astrology_math.py`.
*   **Ephemeris Decoupling:** `ephemeris_service.py` handles pure astronomical math (Swiss Ephemeris wrapper). It outputs normalized snapshots and contains zero astrological reasoning.

## 10. Current Testing Workflow
*   The system uses the standard Python `unittest` framework.
*   Tests are fully isolated from production folders and live in `backend/tests/`.
*   Tests utilize strictly mocked, deterministic JSON payloads that bypass the PDF extraction layer to test pure engine logic.
*   Regression tests validate schema consistency, rule adherence (Immutable D1), and accurate scoring clamps.

## 11. Current Execution Commands
*   **Run Main Application:**
    ```bash
    cd backend
    python run.py
    ```
*   **Run All Tests:**
    ```bash
    cd backend
    python -m unittest discover tests
    ```

## 12. Pending Future Phases
*   **Phase 6 (Dasha Engine):** Implement Vimshottari period logic to output `timing_multipliers`.
*   **Phase 7 (Transit Engine):** Implement Ephemeris-driven Gochara logic to output short-term `transit_multipliers` and context flags (e.g., Sade Sati).
*   **Phase 8 (Probability Synthesis):** The master calculation engine that executes `(D1 Base + Modifiers) * Temporal Multipliers` to output a final event manifestation probability.
*   **Phase 9 (AI Interpretation Wrapper):** Translates the strict mathematical JSON output into readable classical text enhancements via LLM.

## 13. Known Architectural Constraints
*   **Local Execution Only:** The system is strictly designed for local desktop/environment execution.
*   **Memory-Bound / No DB:** There are no databases. The system relies entirely on passing the JSON state object in memory sequentially.
*   **Synchronous Flow:** The `PipelineRunner` acts as a synchronous, blocking DAG. Async logic is currently forbidden to maintain strict determinism.

## 14. Future Caution Areas (DO NOT DO THIS)
*   **DO NOT** add database hooks (e.g., SQL, Mongo) into the engines.
*   **DO NOT** write code that breaks the existing JSON schema (all top-level keys must remain stable).
*   **DO NOT** introduce complex OOP inheritance (e.g., `class TransitEngine(DashaEngine)`). Modules must remain flat and decoupled.
*   **DO NOT** use AI for calculations. Keep the engines mathematically rigid.

## 15. Governance, Import & Execution Rules
*   Absolute imports must be used from the `app.` root (e.g., `from app.engines.varga_engine import VargaEngine`).
*   `__init__.py` files are required in all subdirectories of `app/` and `tests/` to prevent `ModuleNotFoundError` issues.
*   All execution should happen with `backend/` as the current working directory.
*   **Contract Versioning:** The Master JSON Contract is strictly versioned. Schema drift is disallowed. Breaking changes require explicit version increments and backward-compatibility layers.