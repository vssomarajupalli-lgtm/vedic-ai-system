"""
Deterministic scoring constants for astrology engines.
Centralizing these prevents magic numbers in the calculation engines
and ensures absolute explainability for the final outputs.
"""

# ---------------------------------------------------------------------------
# Calibration note (v1.1):
#   Additive formula: dignity + house + state + aspects → clamped [0, 100]
#   Target ranges:
#     Best case  (exalted + trikona + retrograde): 50+35+5 = 90
#     Strong     (exalted + kendra, clean):        50+30   = 80  (≥ 70 axiom)
#     Own+kendra (clean):                          35+30   = 65  (> 50 axiom)
#     Worst case (debilitated + dusthana):          0-15   = 0   (≤ 25 axiom)
# ---------------------------------------------------------------------------
PLANET_SCORING_MATRIX = {
    "dignity": {
        "exalted":     50,   # Maximum dignity — exaltation sign (uccha)
        "own_sign":    35,   # Own sign (swakshetra) — strong functional strength
        "friendly":    20,   # Friendly sign — moderate support
        "neutral":     10,   # Neutral sign — baseline
        "enemy":        5,   # Enemy sign — weakened
        "debilitated":  0    # Debilitation (neecha) — minimum dignity
    },
    "house_placement": {
        "trikona":  35,   # 5, 9 — highest house type in Parashari
        "kendra":   30,   # 1, 4, 7, 10 — angular strength
        "upachaya": 20,   # 3, 6, 10, 11 — growth houses
        "neutral":  10,   # 2, 11, etc — functional
        "dusthana": -15   # 6, 8, 12 — houses of challenge
    },
    "state_modifiers": {
        "combust":    -20,  # Combustion loses planetary agency (within Sun's orb)
        "retrograde":   5   # Cheshta Bala: retrograde motion adds strength
    },
    "aspects": {
        "benefic_aspect":  10,
        "malefic_aspect": -10
    }
}

HOUSE_SCORING_MATRIX = {
    "house_type": {
        "kendra": 20,    # 1, 4, 7, 10
        "trikona": 25,   # 1, 5, 9
        "upachaya": 15,  # 3, 6, 10, 11 (growth)
        "dusthana": -15, # 6, 8, 12 (challenges)
        "neutral": 10    # 2, 12, etc.
    },
    "lord_weight": 0.25, # House lord's strength contributes 25% to the house's total capacity
    "occupants": {
        "benefic": 10,
        "malefic": -10
    },
    "aspects": {
        "benefic": 10,
        "malefic": -10
    },
    # SAV (Sarvashtakavarga) weight for house scoring.
    # Applied as: (sav_normalized_score - 50) × sav_weight → contribution in range [-10, +10]
    # Neutral average (28 bindus) → sav_score=50 → contribution=0 (no change)
    # Max (40+ bindus) → sav_score=100 → contribution=+10
    # Zero bindus      → sav_score=0   → contribution=-10
    # Source: VEDIC_AI_MASTER_ARCHITECTURE.md — Bhava Bala = primary factor
    "sav_weight": 0.20
}

NATURAL_BENEFICS = ["jupiter", "venus", "moon", "mercury"]
NATURAL_MALEFICS = ["saturn", "mars", "sun", "rahu", "ketu"]

# --- Varga Constants ---

D9_SCORES = {
    "exalted": 15.0,
    "moolatrikona": 10.0,
    "own_house": 10.0,
    "friendly": 5.0,
    "neutral": 0.0,
    "enemy": -5.0,
    "debilitated": -10.0
}

D10_SCORES = {
    "exalted": 10.0,
    "moolatrikona": 5.0,
    "own_house": 5.0,
    "friendly": 2.5,
    "neutral": 0.0,
    "enemy": -2.5,
    "debilitated": -5.0
}

VARGOTTAMA_BONUS = 15.0

# --- Dasha Constants (Phase 6) ---

DASHA_SCORING_MATRIX = {
    "relationship_scalars": {
        "1_1": 1.00,   # Same planet
        "2_12": 0.75,  # Loss / Dissolution
        "3_11": 1.15,  # Growth / Gain
        "4_10": 1.20,  # Kendra / Action
        "5_9": 1.25,   # Trikona / Dharma
        "6_8": 0.80,   # Dusthana / Challenge
        "1_7": 1.10    # Direct aspect / Partnership
    }
}

# ---------------------------------------------------------------------------
# Rasi (Sign) Strength Constants
# ---------------------------------------------------------------------------

# Parashari sign lordship — each sign's ruling planet (system key names)
SIGN_LORD_MAP = {
    "aries":       "mars",
    "taurus":      "venus",
    "gemini":      "mercury",
    "cancer":      "moon",
    "leo":         "sun",
    "virgo":       "mercury",
    "libra":       "venus",
    "scorpio":     "mars",
    "sagittarius": "jupiter",
    "capricorn":   "saturn",
    "aquarius":    "saturn",
    "pisces":      "jupiter"
}

# Canonical sign order — index 0 = Aries, index 11 = Pisces
# Used to derive house number from sign given an ascendant sign
SIGNS_IN_ORDER = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

# SAV Bindu → Score mapping (piecewise linear anchors)
# Source: VEDIC_AI_MASTER_ARCHITECTURE.md §Rasi Strength Engine
# Interpolated between anchor points; 56 is the theoretical maximum
SAV_BINDU_SCALE = [
    (0,  0),
    (20, 30),
    (25, 50),
    (30, 70),
    (35, 85),
    (40, 100),
    (56, 100)
]

RASI_SCORING_MATRIX = {
    # Composite formula weights (must sum to 1.0)
    "weights": {
        "sav":      0.40,
        "lord":     0.30,
        "occupant": 0.20,
        "dignity":  0.10
    },
    # Occupant quality modifiers (applied per planet)
    "occupant_modifiers": {
        "benefic":        +15,
        "malefic":        -15,
        "benefic_aspect":  +5,
        "malefic_aspect":  -5,
        "aspect_cap":      10   # max ± from aspects per planet
    },
    # Dignity modifiers (applied per occupant planet)
    "dignity_modifiers": {
        "exalted":        +30,
        "own sign":       +20,
        "moolatrikona":   +20,
        "friendly":       +10,
        "neutral":          0,
        "enemy":          -10,
        "debilitated":    -20,
        "lord_own_bonus": +10  # extra bonus if sign lord occupies own sign
    },
    # Neutral baseline for empty-sign components (not 0 — empty ≠ afflicted)
    "empty_sign_baseline": 50,
    # Default lord score when lord is missing from dependency_scores
    "default_lord_score": 50
}

# Probability grading — shared by all engines
# Source: VEDIC_AI_PROBABILITY_ENGINE_ARCHITECTURE.md
PROBABILITY_GRADES = [
    (80, "EXCELLENT"),
    (65, "VERY GOOD"),
    (50, "GOOD"),
    (35, "WEAK"),
    (0,  "TOO WEAK")
]

# ---------------------------------------------------------------------------
# Ashtakavarga Constants
# ---------------------------------------------------------------------------

# BAV bindu → grade (classical Parashari thresholds, 0-8 scale)
BAV_GRADE_THRESHOLDS = [
    (7, "EXCELLENT"),
    (6, "STRONG"),
    (5, "GOOD"),
    (4, "AVERAGE"),
    (3, "BELOW_AVG"),
    (2, "WEAK"),
    (0, "CRITICAL")
]

# Planet BAV support modifier applied to PlanetStrengthEngine final_score
# Source: design specification
BAV_PLANET_MODIFIER = {
    "high":    +5,   # bindus >= 5 (above average → strengthen planet)
    "neutral":  0,   # bindus == 4 (average)
    "low":     -5    # bindus <= 3 (below average → weaken planet)
}

# SAV bindu thresholds for favorable/unfavorable classification
# Classical average = 28 bindus (336 total / 12 houses)
SAV_FAVORABLE_THRESHOLD = 28
SAV_STRONG_THRESHOLD    = 30
SAV_WEAK_THRESHOLD      = 22

# Dasha BAV timing confidence multipliers
DASHA_BAV_CONFIDENCE = {
    "high":     1.10,   # dasha lord has 5+ bindus in natal house
    "moderate": 1.05,   # dasha lord has 4 bindus
    "low":      0.95    # dasha lord has <= 3 bindus
}

# Planets excluded from BAV (classical Parashari — Rahu/Ketu have no BAV)
BAV_EXCLUDED_PLANETS = {"rahu", "ketu"}

# Canonical 7-planet BAV set
BAV_PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]

# ---------------------------------------------------------------------------
# Natal Promise Engine Constants
# ---------------------------------------------------------------------------

# 4-tier promise classification (score → label)
NATAL_PROMISE_GRADES = [
    (70, "STRONG"),    # Clear natal promise — event strongly indicated
    (50, "MODERATE"),  # Good promise — needs dasha/transit to manifest
    (30, "WEAK"),      # Challenged promise — possible but uncertain
    (0,  "PRESENT"),   # Barely indicated — exceptional support needed
]

# Natural significator (karaka) planet per domain
DOMAIN_KARAKA = {
    "marriage":    {"primary": "venus",   "secondary": "jupiter"},
    "career":      {"primary": "saturn",  "secondary": "sun"},
    "wealth":      {"primary": "jupiter", "secondary": "venus"},
    "education":   {"primary": "mercury", "secondary": "jupiter"},
    "children":    {"primary": "jupiter", "secondary": "moon"},
    "property":    {"primary": "mars",    "secondary": "moon"},
    "health":      {"primary": "sun",     "secondary": "moon"},
    "spirituality":{"primary": "jupiter", "secondary": "ketu"},
}

# Per-domain 6-factor weight specification
# Weights: primary_house + support_houses + karaka + lord + varga + sav = 1.0
DOMAIN_CONFIG = {
    "marriage": {
        "primary_house":   "7",
        "support_houses":  ["2", "11"],
        "varga":           "D9",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1: reduced from 0.07 (SAV is primary timing indicator)
            "sav":            0.05,   # Calibrated v1.1: raised from 0.03 (SAV bindus are major classical indicator)
        }
    },
    "career": {
        "primary_house":   "10",
        "support_houses":  ["6", "11"],
        "varga":           "D10",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
    "wealth": {
        "primary_house":   ["2", "11"],     # averaged
        "support_houses":  ["5", "9"],
        "varga":           "D2",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
    "education": {
        "primary_house":   "5",
        "support_houses":  ["4", "9"],
        "varga":           "D24",
        "weights": {
            "primary_house":  0.25,
            "support_houses": 0.25,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
    "children": {
        "primary_house":   "5",
        "support_houses":  ["9", "11"],
        "varga":           "D7",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
    "property": {
        "primary_house":   "4",
        "support_houses":  ["2", "11"],
        "varga":           "D4",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
    "health": {
        "primary_house":   "1",
        "support_houses":  ["6", "8", "12"],    # INVERTED — strong = bad
        "inverted_support": True,
        "varga":           "D6",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
    "spirituality": {
        "primary_house":   ["9", "12"],     # averaged
        "support_houses":  ["5"],
        "varga":           "D20",
        "weights": {
            "primary_house":  0.30,
            "support_houses": 0.20,
            "karaka":         0.25,
            "lord":           0.15,
            "varga":          0.05,   # Calibrated v1.1
            "sav":            0.05,   # Calibrated v1.1
        }
    },
}

# Affliction penalties — discrete signed values applied after weighted sum
# Key: affliction flag name (detected from house occupants / planet flags)
# Value: dict of {domain: penalty} — only listed domains are affected
# Penalties are capped per domain (see AFFLICTION_CAP below)
AFFLICTION_PENALTIES = {
    # Marriage afflictions
    "rahu_in_7":       {"marriage": -10},
    "ketu_in_7":       {"marriage": -10},
    "saturn_in_7":     {"marriage": -15},
    "mars_in_7":       {"marriage": -10},
    "venus_combust":   {"marriage": -10, "wealth": -5},
    # Career afflictions
    "rahu_in_10":      {"career": -10},
    "saturn_retro_in_10": {"career": -8},
    "lord10_in_dusthana": {"career": -12},
    # Wealth afflictions
    "saturn_in_2":     {"wealth": -8},
    "rahu_in_11":      {"wealth": -8},
    # Education afflictions
    "mercury_combust": {"education": -10},
    "rahu_in_5":       {"education": -8, "children": -8},
    "saturn_in_5":     {"education": -10, "children": -15},
    "lord5_in_dusthana": {"education": -10, "children": -10},
    # Children afflictions
    "ketu_in_5":       {"children": -12},
    "lord5_debilitated": {"children": -10},
    # Property afflictions
    "saturn_in_4":     {"property": -10},
    "rahu_in_4":       {"property": -8},
    "lord4_in_dusthana": {"property": -12},
    "mars_debilitated": {"property": -8},
    # Health afflictions
    "saturn_aspects_lagna": {"health": -10},
    "rahu_in_1":       {"health": -8},
    "sun_combust":     {"health": -5},
    # Spirituality afflictions
    "jupiter_debilitated": {"spirituality": -15},
    "lord9_combust":   {"spirituality": -10},
}

# Maximum total affliction penalty per domain (prevents over-penalisation)
AFFLICTION_CAP = {
    "marriage":    -25,
    "career":      -25,
    "wealth":      -20,
    "education":   -25,
    "children":    -30,
    "property":    -20,
    "health":      -25,
    "spirituality":-20,
}

# Bonus additions (classical yogas) — applied after weighted sum, before cap
DOMAIN_BONUSES = {
    # Wealth — Dhana Yogas
    "same_2_11_lords":       {"wealth": +8},    # 2nd lord + 11th lord conjoined/same sign
    "jupiter_in_2_or_11":    {"wealth": +5},
    "jupiter_in_9":          {"wealth": +5, "spirituality": +8},
    "jupiter_in_5":          {"wealth": +5, "spirituality": +5},
    "venus_in_2":            {"wealth": +5},
    # Spirituality — Ketu amplifier
    "ketu_strong_in_moksha": {"spirituality": +10},  # Ketu (score>50) in H9/H12/H5
    # Marriage — Benefic protection
    "jupiter_aspects_7":     {"marriage": +8},
    "venus_exalted":         {"marriage": +5},
}

# Dusthana house numbers (for lord-in-dusthana checks)
DUSTHANA_HOUSES = {"6", "8", "12"}

# ---------------------------------------------------------------------------
# Transit Engine Constants
# ---------------------------------------------------------------------------

# Classical Parashari Gochara transit quality per planet per house.
# Key: planet system name → dict of {house_number: quality_score}
# Positive score (+12): planet transiting this house is classically auspicious.
# Negative score (-8):  planet transiting this house is classically inauspicious.
# 0 (absent from dict):  neutral — house not listed for this planet.
#
# Source: Brihat Parasara Hora Sastra, Gochara Phala chapter.
TRANSIT_HOUSE_QUALITY = {
    "sun": {
        3: +12, 6: +12, 10: +12, 11: +12,
        1: -8,  2: -8,  4: -8,  5: -8,  7: -8,  8: -8,  9: -8,  12: -8
    },
    "moon": {
        1: +12, 3: +12, 6: +12, 7: +12, 10: +12, 11: +12,
        2: -8,  4: -8,  5: -8,  8: -8,  9: -8,  12: -8
    },
    "mars": {
        3: +12, 6: +12, 11: +12,
        1: -8,  2: -8,  4: -8,  5: -8,  7: -8,  8: -8,  9: -8, 10: -8, 12: -8
    },
    "mercury": {
        2: +12, 4: +12, 6: +12, 8: +12, 10: +12, 11: +12,
        1: -8,  3: -8,  5: -8,  7: -8,  9: -8,  12: -8
    },
    "jupiter": {
        2: +12, 5: +12, 7: +12, 9: +12, 11: +12,
        1: -8,  3: -8,  4: -8,  6: -8,  8: -8,  10: -8, 12: -8
    },
    "venus": {
        1: +12, 2: +12, 3: +12, 4: +12, 5: +12, 8: +12, 9: +12, 11: +12, 12: +12,
        6: -8,  7: -8,  10: -8
    },
    "saturn": {
        3: +12, 6: +12, 11: +12,
        1: -8,  2: -8,  4: -8,  5: -8,  7: -8,  8: -8,  9: -8, 10: -8, 12: -8
    },
    "rahu": {
        3: +12, 6: +12, 10: +12, 11: +12,
        1: -8,  2: -8,  4: -8,  5: -8,  7: -8,  8: -8,  9: -8, 12: -8
    },
    "ketu": {
        3: +12, 6: +12, 11: +12,
        1: -8,  2: -8,  4: -8,  5: -8,  7: -8,  8: -8,  9: -8, 10: -8, 12: -8
    },
}

# Classical Vedha (obstruction) house pairs.
# If a benefic transits house H and a natural malefic simultaneously transits
# VEDHA_PAIRS[H], the benefic transit's positive effect is cancelled.
# Source: Parashari Gochara — Vedha Sthanas.
VEDHA_PAIRS = {
    1: 8,   2: 12,  3: 6,   4: 5,
    5: 4,   6: 3,   7: 2,   8: 1,
    9: 12,  10: 3,  11: 6,  12: 9,
}

# Transit planet conjuncting natal planet — conjunction score table.
# Key: (transit_planet, natal_planet_nature) → signed score.
# "benefic" = jupiter, venus, moon, mercury (natural benefics).
# "malefic" = saturn, mars, sun, rahu, ketu (natural malefics).
#
# Benefic transits amplify benefic natal planets and moderate malefics.
# Malefic transits suppress benefic natals and compound malefic ones.
TRANSIT_CONJUNCTION_MATRIX = {
    ("jupiter", "benefic"): +12,  ("jupiter", "malefic"): +3,
    ("venus",   "benefic"): +8,   ("venus",   "malefic"): +2,
    ("moon",    "benefic"): +6,   ("moon",    "malefic"):  0,
    ("mercury", "benefic"): +5,   ("mercury", "malefic"):  0,
    ("sun",     "benefic"): +4,   ("sun",     "malefic"): -2,
    ("mars",    "benefic"): -8,   ("mars",    "malefic"): -4,
    ("saturn",  "benefic"): -10,  ("saturn",  "malefic"): -5,
    ("rahu",    "benefic"): -6,   ("rahu",    "malefic"): -6,
    ("ketu",    "benefic"): -6,   ("ketu",    "malefic"): -6,
}

# Transit aspect weights for 7th-house (universal) aspect.
# Format: (transit_nature, natal_nature) → score
# Applied when transit planet aspects (7th from its position) a natal planet's house.
TRANSIT_ASPECT_WEIGHTS = {
    ("benefic", "benefic"): +6,
    ("malefic", "benefic"): -5,
    ("benefic", "malefic"): +2,
    ("malefic", "malefic"): -3,
}

# Special aspects for Saturn (3rd, 10th), Jupiter (5th, 9th), Mars (4th, 8th).
# Applied at TRANSIT_SPECIAL_ASPECT_WEIGHT fraction of the 7th-aspect weight.
TRANSIT_SPECIAL_ASPECTS = {
    "saturn":  [3, 7, 10],   # 3rd, 7th, 10th aspect
    "jupiter": [5, 7, 9],    # 5th, 7th, 9th aspect
    "mars":    [4, 7, 8],    # 4th, 7th, 8th aspect
}

# Non-7th special aspects are 60% as strong as the universal 7th aspect.
TRANSIT_SPECIAL_ASPECT_WEIGHT = 0.6

# TransitEngine sub-system weights — must sum to 1.0.
TRANSIT_WEIGHTS = {
    "house_activation":  0.30,
    "bav_support":       0.20,
    "planet_activation": 0.20,
    "dasha_sync":        0.20,
    "vedha_layer":       0.10,
}

# Maximum Vedha penalty per evaluation run (capped to prevent over-penalisation).
TRANSIT_VEDHA_CAP = -15

# Dasha-Transit sync bonus scores (added to the 50 neutral baseline).
TRANSIT_DASHA_SYNC_BONUSES = {
    "transit_is_md_lord":         20,   # transit planet == active Mahadasha lord
    "transit_is_ad_lord":         12,   # transit planet == active Antardasha lord
    "transit_aspects_md_natal":    8,   # transit planet 7th-aspects MD lord natal house
    "transit_aspects_ad_natal":    5,   # transit planet 7th-aspects AD lord natal house
    "transit_same_sign_as_md":     6,   # transit planet in same house as MD lord natal
    "md_transit_bav_high":         8,   # MD lord's BAV in its transit house >= 5 bindus
}
