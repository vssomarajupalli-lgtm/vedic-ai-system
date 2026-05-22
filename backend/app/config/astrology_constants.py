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