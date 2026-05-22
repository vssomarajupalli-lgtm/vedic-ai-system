from app.config.astrology_constants import HOUSE_SCORING_MATRIX, NATURAL_BENEFICS, NATURAL_MALEFICS

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

        # 5. Future Extensibility: Ashtakavarga & Vargas (Phase 4/5 enhancements)
        sav_score = self._evaluate_sav_support(house_data.get("sav_points", 0)) or 0
        if sav_score:
            breakdown["sav_support"] = sav_score
            total_score += sav_score

        # Clamp final score between 0 and 100
        final_score = max(0, min(100, int(total_score)))

        return {
            "house": house_data.get("house", "Unknown"),
            "final_score": final_score,
            "breakdown": breakdown
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

    # --- Future Extensibility Stubs ---

    def _evaluate_sav_support(self, sav_points: int) -> int:
        """Stub for future integration of Sarvashtakavarga (SAV) bindus."""
        # Example future logic: (sav_points - 28) * multiplier
        pass