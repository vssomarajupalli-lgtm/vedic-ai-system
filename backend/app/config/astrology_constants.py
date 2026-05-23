"""
Deterministic scoring constants for astrology engines.
Centralizing these prevents magic numbers in the calculation engines
and ensures absolute explainability for the final outputs.
"""

PLANET_SCORING_MATRIX = {
    "dignity": {
        "exalted": 35,
        "own_sign": 25,
        "friendly": 15,
        "neutral": 10,
        "enemy": 5,
        "debilitated": 0
    },
    "house_placement": {
        "kendra": 20,    # 1, 4, 7, 10
        "trikona": 25,   # 5, 9
        "dusthana": -10, # 6, 8, 12
        "neutral": 10    # 2, 3, 11
    },
    "state_modifiers": {
        "combust": -15,
        "retrograde": 5  # Simplified V1: Retrogression generally adds Cheshta Bala (motion strength)
    },
    "aspects": {
        "benefic_aspect": 10,
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
    }
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