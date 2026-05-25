# PROJECT CONTEXT
# Vedic Astrology Intelligence Framework

## 1. Project Purpose
A deterministic, probability-based Vedic astrology framework. It operates on normalized JSON payloads (optionally extracted from classical horoscope PDFs), calculates explainable strengths, maps these to Event Domains, and layers timing modifiers to determine manifestation probabilities. **It does NOT use AI to "guess" or "invent" astrological predictions.**

## 2. Current Architecture Flow
Data flows unidirectionally through stateless modules:
1. **PDF Extractor (Optional)** -> Scrapes tables and text into raw dicts.
2. **JSON Normalizer (Contract Enforcer)** -> Cleans data, normalizes terminology, injects safe defaults.
3. **Planet Engine (D1)** -> Calculates base 0-100 planetary strength.
4. **House Engine (D1)** -> Calculates base 0-100 life-domain strength.
5. **Varga Engine (Phase 5)** -> Calculates D9/D10 structural refinements.
6. **Pipeline Runner** -> Orchestrates data hand-offs sequentially utilizing `MappingProxyType` to enforce immutable read-only dependency injection.
7. **Staged JSON State Object** -> The explainable, standardized global pipeline payload.

## 3. Current Completed Modules
*   `config/astrology_constants.py` (Central deterministic brain)
*   `parsers/json_normalizer.py` (Schema firewall)
*   `engines/planet_strength_engine.py`
*   `engines/house_strength_engine.py`
*   `engines/varga_engine.py` (V1: D9, D10)
*   `pipeline_runner.py` (Lightweight sequential executor)
*   `tests/` (Deterministic regression test suite)

## 4. Modifier Philosophy
*   **Structural Modifiers (Capacity):** Vargas, Yogas, and SAV modify the *quality* of the chart. They are mathematically **additive** (e.g., +15 points) and live in the `modifiers` output object.
*   **Temporal Modifiers (Activation):** Dashas and Transits determine *when* an event triggers. They are mathematically **multiplicative** (e.g., 1.2x) and live in the `temporal_activation` output object.
*   **Ashtakavarga Matrix:** Ashtakavarga serves as a dynamic reinforcement/lookup matrix rather than a simple flat score modifier.
*   **Confidence Flags:** Engines append string context (e.g., `"varga_contradicted"`) to explain mathematical scores to future AI text layers.

## 5. Predictive Philosophy
**Manifestation Probability = (Natal Promise + Structural Modifiers) × Temporal Multipliers**
*   D1 = Foundation Karma
*   Vargas = Manifestation Refinement
*   Dashas = Activation Timing
*   Transits = Event Triggering
*   Event Domains = Abstracted configuration mappings (e.g. Career, Marriage) avoiding coupled if-else synthesis chaos.

## 6. Future Roadmap
*   **Phase 6:** Dasha Engine (Timing Multipliers)
*   **Phase 7:** Transit Engine (Trigger Modifiers)
*   **Phase 8:** Probability & Consolidation Engine (Master Synthesis)
*   **Phase 9:** AI Interpretation Wrapper (Translating math to readable classical text)