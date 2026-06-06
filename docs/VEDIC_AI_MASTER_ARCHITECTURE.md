# VEDIC_AI_MASTER_ARCHITECTURE.md

## Project Vision

Vedic-AI is a deterministic Vedic Astrology Intelligence System.

It is NOT:

* A chatbot
* A generic horoscope generator
* A random prediction engine

It IS:

* A deterministic astrology calculation framework
* A probability-based prediction system
* A question-answering astrology intelligence platform

---

## Relationship Between Projects

Raw Horoscope PDF
↓
HoroscopeCleaner_Final
↓
Canonical PDF
Canonical JSON
Canonical Sections
Canonical Page Map
↓
Vedic AI System
↓
Prediction Intelligence

---

## Core Philosophy

The source horoscope PDF already contains:

* Shadbala
* Bhava Bala
* Ishta Phala
* Kashta Phala
* Ashtakavarga
* Sarvashtakavarga
* Shodasha Vargas
* Dasha Tables
* Predictions

Vedic-AI should EXTRACT these values.

Vedic-AI should NOT recalculate them unless absolutely necessary.

The primary role of Vedic-AI is:

Extract
→ Validate
→ Weight
→ Combine
→ Synthesize

---

## Core Engines

### Planet Strength Engine

Inputs:

* Shadbala
* Dignity
* House Placement
* Aspects
* Combustion
* Retrogression
* Varga Support

Weighting:

Shadbala = 40%
Dignity = 20%
Placement = 10%
Aspects = 10%
State Modifiers = 10%
Varga Support = 10%

Output:

Planet Strength %

---

### House Strength Engine

Inputs:

* Bhava Bala
* Lord Strength
* Occupants
* Aspects

Weighting:

Bhava Bala = 50%
Lord Strength = 30%
Occupants = 10%
Aspects = 10%

Output:

House Strength %

---

### Rasi Strength Engine

Inputs:

* Sarvashtakavarga Bindus
* Rasi Lord Strength

Formula:

Rasi Strength =
70% SAV Bindus
+
30% Rasi Lord Strength

Example Mapping:

20 Bindus = 30%
25 Bindus = 50%
30 Bindus = 70%
35 Bindus = 85%
40 Bindus = 100%

Output:

Rasi Strength %

---

### Varga Validation Engine

Marriage → D9
Career → D10
Children → D7
Property → D4
Spiritual → D20

Purpose:

Validate Natal Promise.

---

### Dasha Activation Engine

Inputs:

* Mahadasha
* Antardasha
* Pratyantardasha

Uses:

* Planet Strength
* Varga Support
* Ashtakavarga Support

Output:

Dasha Activation %

---

### Transit Engine

Phase 1:

Use Transit Information Available In PDF.

Phase 2:

Swiss Ephemeris Integration.

Purpose:

Future Date Calculations.

---

## Event Domain Engines

Marriage Engine
Career Engine
Finance Engine
Property Engine
Health Engine
Children Engine
Education Engine
Spiritual Engine

---

## Master Probability Engine

Natal Promise = 40%
Planet Strength = 15%
House Strength = 10%
Rasi Strength = 10%
Varga Validation = 10%
Dasha Activation = 10%
Transit Trigger = 5%

Output:

Manifestation Probability %

---

## Protection / Resistance Engine

Examples:

* Sade Sati
* Ashtama Shani
* Rahu Transit
* Ketu Transit

Formula:

## Damage Potential

# Protection Factors

Effective Impact

Protection Factors:

* Planet Strength
* House Strength
* Rasi Strength
* Ashtakavarga
* Vargas

---

## Question Engine

Question
↓
Event Domain
↓
Natal Promise
↓
Dasha Activation
↓
Transit Trigger
↓
Probability
↓
Timing Window
↓
Answer

---

## Swiss Ephemeris

Required Only For:

* Future Marriage Timing
* Future Career Timing
* Future Property Timing
* Future Transit Prediction

Not Required For:

* PDF Reading
* Existing Prediction Validation
* Current Dasha Analysis

---

## Development Priority

1. HoroscopeCleaner_Final
2. PDF Extraction Blueprint
3. Core Extraction Pipeline
4. Planet Strength
5. House Strength
6. Rasi Strength
7. Dasha Activation
8. Question Engine
9. Transit Engine
10. Swiss Ephemeris
11. Master Synthesis
