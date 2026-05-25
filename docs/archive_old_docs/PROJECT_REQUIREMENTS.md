# PROJECT REQUIREMENTS
# Vedic Astrology Intelligence Framework

---

# 1. PROJECT PURPOSE

Develop a deterministic Vedic astrology intelligence framework that:

- supports direct normalized JSON processing OR PDF-driven workflows
- extracts horoscope data from PDF reports
- calculates planetary and house strengths
- integrates Shodasha Vargas
- evaluates Mahadasha / Antardasha
- evaluates transit effects
- calculates manifestation probability
- enhances existing classical phalita text with intelligent analysis

The system should NOT generate random astrology predictions.

The system should:
- preserve classical astrology
- add quantified intelligence
- provide explainable probability-based outputs
- prevent tightly coupled spaghetti logic via strict Event Domain abstraction

---

# 2. CORE PHILOSOPHY

## Main Principle

D1 = Foundation Karma

Planets = Operational Strength

Houses = Life Domain Strength

Vargas = Manifestation Refinement

Dashas = Activation Timing

Transits = Event Triggering

---

# 3. SOFTWARE TYPE

This is NOT:
- a chatbot
- a random AI astrology generator
- a static astrology software

This IS:
- a deterministic astrology intelligence framework
- a probability-based prediction system
- a layered reconciliation engine

---

# 4. PRIMARY INPUT

Primary input sources (Dual Workflow):

A) Direct normalized JSON payloads (API/Backend workflow).
B) Optional PDF Extraction Workflow:

- horoscope PDF reports
- approximately 80–100 pages
- structured astrology tables
- existing phalita text included

---

# 5. PDF CONTENTS EXPECTED

The PDF may contain:

- D1 chart
- Shodasha Vargas
- Graha Bala
- Shadbala
- Bhava Bala
- Ashtakavarga
- Bhinna Ashtakavarga
- Sarvashtakavarga
- Dasha tables
- Transit tables
- Existing phalita sections

---

# 6. MAIN SOFTWARE MODULES

## 6.1 PDF Extraction Engine

Purpose:
- extract text
- extract tables
- identify headings
- convert data into structured JSON

---

## 6.2 Planet Strength Engine

Purpose:
calculate final planetary strength percentage.

Inputs include:
- Graha Bala
- Shadbala
- Ishta/Kashta
- D1 dignity
- House placement
- Aspects
- Conjunctions
- BAV points
- D9 validation

Output:
0–100 planetary strength score.

---

## 6.3 House Strength Engine

Purpose:
calculate life-domain strength.

Inputs include:
- Bhava Bala
- SAV
- House lord strength
- Occupants
- Aspects
- Karaka strength

Output:
0–100 house strength score.

---

## 6.4 Shodasha Varga Engine

Purpose:
calculate contextual manifestation refinement.

Important rule:
Vargas should refine house strength.
Vargas should NOT dominate D1.

Each Varga should have:
- separate scoring
- weighted contribution
- contextual interpretation

---

## 6.5 Dasha Engine

Purpose:
calculate activation probability.

Inputs:
- Mahadasha lord
- Antardasha lord
- related houses
- related Vargas
- planetary strengths

Output:
Dasha manifestation probability.

---

## 6.6 Transit Engine

Purpose:
calculate current triggering effects.

Inputs:
- current transit
- natal interaction
- Ashtakavarga reinforcement matrix
- Sade Sati framework

Output:
Transit intensity and event triggering probability.

---

## 6.7 Probability Engine

Purpose:
consolidate all engines deterministically via Event Domains.

Final output:
- manifestation probability
- severity
- quality
- timing strength

---

## 6.8 Interpretation Engine

Purpose:
enhance existing classical phalita and translate math to text.

Important:
The system should NOT replace classical predictions.
The AI MUST NOT generate mathematical probabilities or astrological scores.

The system should:
- append intelligent analysis
- attach probability scores
- attach strength analysis
- attach severity modulation

---

# 7. PREDICTION PHILOSOPHY

The software should:
- preserve original astrology phalita
- enhance it using calculated intelligence

Example:

Original phalita:
"Career growth may occur."

Software enhancement:
- Jupiter strength
- 10th house strength
- D10 support
- Transit support
- Final probability

Final output should become:
- explainable
- quantified
- deterministic

---

# 8. OUTPUT TYPES

The software should generate:

## 8.1 Planet Strength Report
- 9 planets
- final strength %

---

## 8.2 House Strength Report
- 12 houses
- final strength %

---

## 8.3 Dasha Report
- active Mahadasha
- Antardasha
- manifestation probability

---

## 8.4 Transit Report
- current transit effects
- severity

---

## 8.5 Final Intelligent Prediction Report

Should contain:
- original phalita
- software intelligence layer
- probability layer
- final conclusion

---

# 9. ARCHITECTURE PRINCIPLES

The project must remain:

- deterministic
- modular
- explainable
- scalable
- locally runnable
- AI-compatible
- not AI-dependent

---

# 10. IMPORTANT DEVELOPMENT RULES

## Rule 1
Do NOT overengineer.

---

## Rule 2
One engine at a time.

---

## Rule 3
Freeze architecture before scaling.

---

## Rule 4
Keep astrology logic separated from UI.

---

## Rule 5
Keep each engine independent.

---

# 11. DEVELOPMENT PHASES

## Phase 1
PDF Extraction

---

## Phase 2
JSON Structuring

---

## Phase 3
Planet Strength Engine

---

## Phase 4
House Strength Engine

---

## Phase 5
Shodasha Varga Engine

---

## Phase 6
Dasha Engine

---

## Phase 7
Transit Engine

---

## Phase 8
Probability Consolidation

---

## Phase 9
Final Report Generation

---

# 12. TECHNOLOGY STACK

Current stack:

- Python
- VS Code
- Local desktop environment
- JSON-based data flow

No cloud dependency initially.

No web application initially.

---

# 13. FINAL GOAL

Create a professional Vedic astrology intelligence framework that:
- preserves classical astrology
- adds quantified intelligence
- produces explainable prediction probabilities
- supports future AI interpretation layers
- remains deterministic at the core