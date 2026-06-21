from app.config.astrology_constants import HOUSE_SCORING_MATRIX, NATURAL_BENEFICS, NATURAL_MALEFICS, PROBABILITY_GRADES
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

    def calculate_strength(self, house_data: dict, bhava_bala_data: dict = None) -> dict:
        """
        Calculates the overall strength of a single house.
        
        Args:
            house_data (dict): Normalized JSON data for a single house, including the lord's pre-calculated strength.
            bhava_bala_data (dict): Optional authentic bhava bala metrics extracted from the PDF.
            
        Returns:
            dict: Explainable payload with final score and score breakdown.
        """
        breakdown = {}
        total_score = 0

        # 1. Evaluate House Type (Kendra, Trikona, Dusthana, etc.)
        type_score = self._evaluate_house_type(house_data.get("house_type", "neutral"))
        breakdown["house_type"] = type_score

        # 2. Evaluate Lord Contribution (Assumes planet engine has already run for the lord)
        lord_score = self._evaluate_lord_contribution(house_data.get("lord_strength_score", 50))
        breakdown["lord_contribution"] = lord_score

        # 3. Evaluate Occupants
        occupant_score = self._evaluate_influences(house_data.get("occupants", []), "occupants")
        breakdown["occupants_impact"] = occupant_score

        # 4. Evaluate Aspects Received
        aspect_score = self._evaluate_influences(house_data.get("aspected_by", []), "aspects")
        breakdown["aspects_impact"] = aspect_score

        # 5. SAV (Sarvashtakavarga) Environment
        # Contribution is signed [-10, +10]: above-average SAV helps; below-average SAV hurts.
        # Houses with 28+ bindus (average) get a neutral or positive contribution.
        sav_score = self._evaluate_sav_support(house_data.get("sav_points", 0))
        breakdown["sav_support"] = sav_score


        # Check if authentic bhava_bala data is available
        house_num_str = str(house_data.get("house", "unknown"))
        bhava_info = None
        if bhava_bala_data and isinstance(bhava_bala_data, dict):
            bhava_info = bhava_bala_data.get(house_num_str)

        if bhava_info and "total_bala" in bhava_info:
            total_bala = float(bhava_info["total_bala"])
            base_score = self._map_bhava_bala_to_score(total_bala)
            breakdown["bhava_bala_base_score"] = base_score
            # The base score completely overrides the heuristics
            total_score = base_score + sav_score
        else:
            # Fallback to legacy additive heuristics
            total_score = type_score + lord_score + occupant_score + aspect_score + sav_score

        # Apply Lagna Floor (prevent H1 from dropping to 0 due to compounding penalties)
        if house_num_str == "1" and total_score < 15:
            total_score = 15
            if "clamped_to_zero" in breakdown: 
                del breakdown["clamped_to_zero"] # In case used later

        # Clamp final score between 0 and 100
        final_score = clamp_score(total_score)

        return {
            "metadata": {
                "entity_id": str(house_data.get("house", "unknown")),
                "entity_type": "house",
                "lord": house_data.get("lord", "unknown")
            },
            "final_score": final_score,
            "grade":       self._assign_grade(final_score),
            "raw_score":   float(total_score),
            "breakdown":   breakdown,
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

    def _map_bhava_bala_to_score(self, total_bala: float) -> float:
        """
        Maps Bhava Bala total_bala (in Rupas) to the [0, 100] internal probability scale.
        Anchors:
            >= 10.0 -> 100
            8.5 -> 75
            7.0 -> 50
            6.0 -> 25
            <= 5.0 -> 0
        """
        anchors = [
            (5.0, 0),
            (6.0, 25),
            (7.0, 50),
            (8.5, 75),
            (10.0, 100)
        ]
        
        if total_bala <= anchors[0][0]:
            return anchors[0][1]
        elif total_bala >= anchors[-1][0]:
            return anchors[-1][1]
            
        for i in range(len(anchors) - 1):
            lo_b, lo_s = anchors[i]
            hi_b, hi_s = anchors[i + 1]
            if lo_b <= total_bala <= hi_b:
                t = (total_bala - lo_b) / (hi_b - lo_b)
                return lo_s + t * (hi_s - lo_s)
        return 50.0

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


    def _assign_grade(self, score: int) -> str:
        """Maps a house final_score to a PROBABILITY_GRADES label.
        
        Uses the same grade thresholds as all other engines so that house
        grades are directly comparable to planet and master grades:
            EXCELLENT  ≥ 80  — strongly supported bhava
            VERY GOOD  ≥ 65  — well supported
            GOOD       ≥ 50  — favorable environment
            WEAK       ≥ 35  — limited support
            TOO WEAK    < 35 — severely afflicted bhava
        """
        for threshold, label in PROBABILITY_GRADES:
            if score >= threshold:
                return label
        return "TOO WEAK"

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