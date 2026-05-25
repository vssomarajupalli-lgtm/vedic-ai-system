# SYSTEM ARCHITECTURE
# Vedic Astrology Intelligence Framework

---

# 1. SYSTEM OVERVIEW

The software is a local desktop-based deterministic Vedic astrology intelligence framework.

Purpose:
- extract horoscope PDF data
- calculate strengths
- reconcile astrology layers via Event Domains
- generate probability-based outputs

---

# 2. MAIN ARCHITECTURE FLOW

(Optional Workflow)
PDF
↓
PDF Extraction Engine
↓
(Primary Workflow)
Structured JSON
↓
Planet Engine
↓
House Engine
↓
Varga Engine
↓
Dasha Engine
↓
Transit Engine
↓
Probability Engine
↓
Interpretation Engine
↓
Final Report

---

# 3. MAIN PROJECT STRUCTURE

vedic-ai-system/
│
├── backend/
├── docs/
├── sample_reports/
├── extracted_json/
├── outputs/
└── temp/

---

# 4. BACKEND STRUCTURE

backend/
│
├── app/
├── requirements.txt
└── run.py

---

# 5. APP STRUCTURE

app/
│
├── database/
├── engines/
├── interpretations/
├── models/
├── parsers/
├── utils/
└── config/

---

# 6. PARSERS MODULE

Purpose:
extract and structure PDF data.

Files:

- pdf_extractor.py
- table_parser.py
- json_builder.py

Responsibilities:
- extract text
- extract tables
- identify headings
- create structured JSON

---

# 7. ENGINES MODULE

Purpose:
astrology intelligence calculations.

Files:

- planet_engine.py
- house_engine.py
- varga_engine.py
- dasha_engine.py
- transit_engine.py
- probability_engine.py
- consolidation_engine.py

---

# 8. PLANET ENGINE

Purpose:
calculate 9-planet strength percentages.

Inputs:
- Graha Bala
- Shadbala
- Ishta/Kashta
- D1 dignity
- aspects
- conjunctions
- BAV
- D9 validation

Output:
0–100 score.

---

# 9. HOUSE ENGINE

Purpose:
calculate 12-house strength percentages.

Inputs:
- Bhava Bala
- SAV
- house lord strength
- karaka strength
- aspects
- occupants

Output:
0–100 score.

---

# 10. VARGA ENGINE

Purpose:
refine manifestation potential.

Important:
Vargas should support D1.
They should not override D1 completely.

Main Vargas:
- D2
- D3
- D4
- D7
- D9
- D10
- D12
- D16
- D20
- D24
- D27
- D30
- D40
- D45
- D60

---

# 11. DASHA ENGINE

Purpose:
calculate activation probability.

Inputs:
- Mahadasha
- Antardasha
- related planets
- related houses
- Vargas support

Output:
manifestation probability.

---

# 12. TRANSIT ENGINE

Purpose:
calculate event triggering intensity.

Inputs:
- transit planets
- natal interaction
- SAV/BAV support
- Sade Sati logic

Output:
transit severity and support score.

---

# 13. PROBABILITY ENGINE

Purpose:
combine all engines deterministically via Event Domain configuration mappings.

Responsibilities:
- weighted reconciliation
- severity calculation
- manifestation probability
- final confidence score

---

# 14. INTERPRETATION ENGINE

Purpose:
translate math scores into classical text explanations.

Important:
Do NOT generate random astrology.

The engine should:
- preserve existing phalita
- append intelligence layer
- append probability layer
- append final conclusion

---

# 15. JSON FLOW

PDF
↓
Raw Extraction JSON
↓
Cleaned JSON
↓
Normalized JSON
↓
Engine Inputs
↓
Calculated Scores
↓
Final Output JSON

---

# 16. OUTPUT TYPES

Outputs include:

- planet strength report
- house strength report
- dasha report
- transit report
- intelligent prediction report

---

# 17. IMPORTANT DEVELOPMENT PRINCIPLES

Rule 1:
Keep modules independent.

Rule 2:
One engine at a time.

Rule 3:
Avoid overengineering.

Rule 4:
Keep astrology logic deterministic.

Rule 5:
Keep interpretation separated from calculations.

---

# 18. INITIAL DEVELOPMENT ORDER

Phase 1:
PDF extraction

Phase 2:
JSON structuring

Phase 3:
Planet engine

Phase 4:
House engine

Phase 5:
Varga engine

Phase 6:
Dasha engine

Phase 7:
Transit engine

Phase 8:
Probability consolidation

Phase 9:
Final report generation

---

# 19. CURRENT TECHNOLOGY STACK

- Python
- VS Code
- Local desktop environment
- JSON data flow

No web application initially.
No cloud dependency initially.

---

# 20. FUTURE POSSIBILITY

Future optional upgrades:
- Electron desktop UI
- AI interpretation layer
- Telugu narration
- multilingual reports
- conversational assistant

Core astrology engine should remain deterministic.