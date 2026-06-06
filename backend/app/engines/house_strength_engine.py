from app.config.astrology_constants import HOUSE_SCORING_MATRIX, NATURAL_BENEFICS, NATURAL_MALEFICS
from app.utils.astrology_math import clamp_score

class HouseStrengthEngine:
    """
    Deterministic scoring engine for calculating the strength of astrological houses (Bhavas).
    Calculates a 0-100 score based on foundational rules.
    No AI reasoning is used in these calculations.
    """

    def __init__(self):
        # Load scoring constants from central config
        self.scoring_matrix = HOUSE_SCORING_MATRIX
        self.benefics = NATURAL_BENEFICS
        self.malefics = NATURAL_MALEFICS

    def calculate_strength(self, house_data: dict) -> dict:
        """
        Calculates the overall strength of a single house.
        
        Args:
            house_data (dict): Normalized JSON data for a single house, including the lord's pre-calculated strength.
            
        Returns:
            dict: Explainable payload with final score and score breakdown.
        """
        breakdown = {}
        total_score = 0

        # 1. Evaluate House Type (Kendra, Trikona, Dusthana, etc.)
        type_score = self._evaluate_house_type(house_data.get("house_type", "neutral"))
        breakdown["house_type"] = type_score
        total_score += type_score

        # 2. Evaluate Lord Contribution (Assumes planet engine has already run for the lord)
        lord_score = self._evaluate_lord_contribution(house_data.get("lord_strength_score", 50))
        breakdown["lord_contribution"] = lord_score
        total_score += lord_score

        # 3. Evaluate Occupants
        occupant_score = self._evaluate_influences(house_data.get("occupants", []), "occupants")
        breakdown["occupants_impact"] = occupant_score
        total_score += occupant_score

        # 4. Evaluate Aspects Received
        aspect_score = self._evaluate_influences(house_data.get("aspected_by", []), "aspects")
        breakdown["aspects_impact"] = aspect_score
        total_score += aspect_score

        # 5. SAV (Sarvashtakavarga) Environment
        # Contribution is signed [-10, +10]: above-average SAV helps; below-average SAV hurts.
        # Houses with 28+ bindus (average) get a neutral or positive contribution.
        sav_score = self._evaluate_sav_support(house_data.get("sav_points", 0))
        breakdown["sav_support"] = sav_score
        total_score += sav_score


        # Clamp final score between 0 and 100
        final_score = clamp_score(total_score)

        return {
            "metadata": {
                "entity_id": str(house_data.get("house", "unknown")),
                "entity_type": "house"
            },
            "final_score": final_score,
            "raw_score": float(total_score),
            "breakdown": breakdown,
            "modifiers": {
                "varga_refinement": 0.0,
                "ashtakavarga_support": 0.0
            },
            "temporal_activation": {
                "timing_multiplier": 1.0,
                "transit_modifier": 0.0
            },
            "confidence_flags": self._generate_confidence_flags(total_score, final_score)
        }

    # --- Isolated Helper Methods ---

    def _evaluate_house_type(self, house_type: str) -> int:
        return self.scoring_matrix["house_type"].get(house_type.lower(), self.scoring_matrix["house_type"]["neutral"])

    def _evaluate_lord_contribution(self, lord_strength: int) -> float:
        # E.g., if lord strength is 80, it adds 20 points (80 * 0.25)
        return lord_strength * self.scoring_matrix["lord_weight"]

    def _evaluate_influences(self, planet_list: list, context: str) -> int:
        """Calculates benefic/malefic impact for either occupants or aspects."""
        score = 0
        for planet in planet_list:
            planet_lower = planet.lower()
            if planet_lower in self.benefics:
                score += self.scoring_matrix[context]["benefic"]
            elif planet_lower in self.malefics:
                score += self.scoring_matrix[context]["malefic"]
        return score

    def _evaluate_sav_support(self, sav_points: int) -> float:
        """
        Computes SAV (Sarvashtakavarga) contribution to house strength.

        Uses the official piecewise linear anchor table from the master architecture.
        Deviation from neutral (50 = 28 bindus) is scaled by sav_weight (0.20).

        Formula:
            sav_score    = piecewise_linear(sav_points, anchors)   → [0, 100]
            contribution = (sav_score - 50) × sav_weight           → [-10, +10]

        Reference points (Raju chart):
            H11: 40 bindus → score 100 → contribution +10
            H9:  25 bindus → score  50 → contribution   0
            H4:  30 bindus → score  70 → contribution  +4
            H12:  0 bindus → score   0 → contribution -10

        Returns:
            float: SAV contribution in the range [-10, +10].
        """
        anchors = [
            (0,  0.0),
            (20, 30.0),
            (25, 50.0),
            (30, 70.0),
            (35, 85.0),
            (40, 100.0),
            (56, 100.0)    # upper bound guard
        ]
        bindus = int(sav_points or 0)

        # Piecewise linear interpolation
        if bindus <= anchors[0][0]:
            sav_score = anchors[0][1]
        elif bindus >= anchors[-1][0]:
            sav_score = anchors[-1][1]
        else:
            sav_score = 50.0  # safe fallback
            for i in range(len(anchors) - 1):
                lo_b, lo_s = anchors[i]
                hi_b, hi_s = anchors[i + 1]
                if lo_b <= bindus <= hi_b:
                    t = (bindus - lo_b) / (hi_b - lo_b)
                    sav_score = lo_s + t * (hi_s - lo_s)
                    break

        weight       = self.scoring_matrix.get("sav_weight", 0.20)
        contribution = (sav_score - 50.0) * weight
        return round(contribution, 2)


    def _generate_confidence_flags(self, raw_score: float, final_score: int) -> list:
        flags = []
        if raw_score < 0:
            flags.append("clamped_to_zero")
            flags.append("severely_afflicted")
        elif raw_score > 100:
            flags.append("clamped_to_100")
        elif raw_score > 75:
            flags.append("strongly_supported")
        return flags