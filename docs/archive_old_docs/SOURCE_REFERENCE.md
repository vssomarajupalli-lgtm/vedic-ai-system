# SOURCE REFERENCE
# Horoscope PDF Structure Reference

---

# 1. PURPOSE

This document explains the structure of the source horoscope PDF reports used in the system.

The reports are approximately:
- 80–100 pages
- astrology tables
- Vargas
- strengths
- phalita sections

The software should extract structured data from these reports.

---

# 2. IMPORTANT NOTE

Page numbers may vary slightly between reports.

The extraction engine should rely on:
- headings
- keywords
- table patterns
- section identification

NOT only page numbers.

---

# 3. MAIN PDF SECTIONS

---

## SECTION 1
# BASIC BIRTH DETAILS

Contains:
- name
- birth date
- birth time
- place
- ayanamsa
- nakshatra
- lagna

Purpose:
basic chart initialization.

---

## SECTION 2
# D1 RASHI CHART

Contains:
- 9 planets
- signs
- houses
- degrees
- nakshatras

Purpose:
main foundational chart.

Important:
D1 is the primary chart.

---

## SECTION 3
# SHODASHA VARGAS

Contains:
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

Purpose:
manifestation refinement.

Important:
Vargas should support D1 interpretation.

---

## SECTION 4
# GRAHA BALAS

Contains:
- planetary strengths
- positional strengths
- directional strengths
- motion strengths

Purpose:
planet strength engine input.

---

## SECTION 5
# SHADBALA

Contains:
- Sthana Bala
- Dig Bala
- Kala Bala
- Cheshta Bala
- Naisargika Bala
- Drik Bala

Purpose:
planet strength scoring.

---

## SECTION 6
# BHAVA BALA

Contains:
- house strengths
- bhava support values

Purpose:
house strength engine input.

---

## SECTION 7
# ASHTAKAVARGA

Contains:
- Bhinna Ashtakavarga
- Sarvashtakavarga
- house-wise points
- sign-wise points

Purpose:
house support scoring.

---

## SECTION 8
# DASHA TABLES

Contains:
- Mahadasha
- Antardasha
- Antarantar Dasha

Purpose:
activation timing engine.

---

## SECTION 9
# TRANSIT TABLES

Contains:
- current transits
- planetary movements
- transit effects

Purpose:
transit triggering analysis.

---

## SECTION 10
# PHALITA BHAGAM

Contains:
classical prediction text.

Purpose:
base prediction layer.

Important:
Software should preserve this text and enhance it intelligently.

---

# 4. PHALITA ENHANCEMENT PHILOSOPHY

The software should NOT replace original phalita.

The software should:
- append intelligence analysis
- append probability layer
- append severity modulation
- append strength interpretation

---

# 5. SAMPLE FINAL OUTPUT STRUCTURE

Original Phalita
↓
Planet Strength Analysis
↓
House Strength Analysis
↓
Dasha Probability
↓
Transit Modification
↓
Final Intelligent Conclusion

---

# 6. EXTRACTION TARGETS

The parser should eventually identify:

- headings
- tables
- planet names
- house values
- percentages
- dasha periods
- phalita paragraphs

---

# 7. JSON EXTRACTION GOAL

Final extracted structure should become:

{
  "birth_details": {},
  "d1_chart": {},
  "vargas": {},
  "planet_strengths": {},
  "house_strengths": {},
  "ashtakavarga": {},
  "dashas": {},
  "transits": {},
  "phalita": {}
}

---

# 8. IMPORTANT DEVELOPMENT PRINCIPLE

Extraction should happen in stages:

Stage 1:
Raw text extraction

Stage 2:
Table extraction

Stage 3:
Heading identification

Stage 4:
Structured JSON conversion

Stage 5:
Validation and normalization

---

# 9. CURRENT DEVELOPMENT PRIORITY

Current focus:
- stable PDF extraction
- stable JSON generation

Not prediction generation yet.

---

# 10. LONG TERM GOAL

Create a reusable extraction system capable of:
- reading astrology PDFs
- structuring astrology intelligence
- feeding deterministic astrology engines
- supporting future intelligent prediction layers