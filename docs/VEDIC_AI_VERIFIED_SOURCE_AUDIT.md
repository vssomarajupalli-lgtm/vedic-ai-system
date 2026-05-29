# VERIFIED SOURCE CODE AUDIT (MANUALLY VERIFIED)

The following files were directly inspected and confirmed to contain real executable code.

## VERIFIED IMPLEMENTED FILES

### backend/app/pipeline_runner.py

Status: VERIFIED IMPLEMENTED

Purpose:

* orchestrates deterministic execution pipeline
* connects normalizer and engines
* manages dependency passing

Verified Components:

* JsonNormalizer integration
* PlanetStrengthEngine integration
* HouseStrengthEngine integration
* VargaEngine integration

---

### backend/app/parsers/json_normalizer.py

Status: VERIFIED IMPLEMENTED

Purpose:

* schema normalization
* alias mapping
* data cleaning
* deterministic defaults

Verified Features:

* metadata normalization
* planet normalization
* varga normalization
* dasha normalization
* Telugu/Sanskrit alias handling

---

### backend/app/parsers/table_parser.py

Status: VERIFIED IMPLEMENTED

Purpose:

* converts extracted table grids into structured dictionaries

Verified Features:

* malformed row rejection
* empty row handling
* deterministic parsing
* extraction metadata generation

---

### backend/app/engines/planet_strength_engine.py

Status: VERIFIED IMPLEMENTED

Verified Features:

* dignity scoring
* house placement scoring
* combustion modifiers
* retrograde modifiers
* benefic aspect scoring
* malefic aspect scoring
* confidence flags
* score clamping

Pending:

* Ashtakavarga integration
* advanced varga support

---

### backend/app/engines/house_strength_engine.py

Status: VERIFIED IMPLEMENTED

Verified Features:

* house type scoring
* lord contribution scoring
* occupant evaluation
* aspect evaluation
* confidence flags

Pending:

* SAV integration

---

### backend/app/engines/varga_engine.py

Status: VERIFIED IMPLEMENTED

Verified Features:

* D9 evaluation
* D10 evaluation
* Vargottama evaluation
* Neecha Bhanga detection
* contradiction detection
* immutable D1 preservation

---

### backend/app/engines/dasha_engine.py

Status: VERIFIED IMPLEMENTED

Verified Features:

* Mahadasha activation
* Antardasha activation
* planetary relationship analysis
* timing multipliers
* temporal activation payload generation

---

### backend/app/config/astrology_constants.py

Status: VERIFIED IMPLEMENTED

Verified Constants:

* PLANET_SCORING_MATRIX
* HOUSE_SCORING_MATRIX
* NATURAL_BENEFICS
* NATURAL_MALEFICS
* D9_SCORES
* D10_SCORES
* VARGOTTAMA_BONUS
* DASHA_SCORING_MATRIX

---

# VERIFIED TEST FILES

Confirmed Present:

* test_pipeline_runner.py
* test_json_normalizer.py
* test_pdf_text_extractor.py
* test_planet_strength_engine.py
* test_table_parser.py
* test_index_reader.py

---

# FILES PRESENT BUT NOT YET INSPECTED

Need source verification:

* pdf_text_extractor.py
* index_reader.py
* astrology_math.py
* run.py

---

# VERIFIED STUBS / PENDING IMPLEMENTATIONS

Ashtakavarga:

* BAV integration pending
* SAV integration pending

Advanced Prediction Layer:

* Transit Engine
* Master Synthesis Engine
* Prediction Runtime
* Narration Engine
* Question Engine

Not yet verified in source code.
