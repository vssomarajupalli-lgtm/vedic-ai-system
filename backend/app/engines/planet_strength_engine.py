from app.config.astrology_constants import PLANET_SCORING_MATRIX
from app.utils.astrology_math import clamp_score

class PlanetStrengthEngine:
    """
    Deterministic scoring engine for calculating planetary operational strength.
    Calculates a 0-100 score based on strict astrological rules.
    No AI reasoning is used in these calculations.
    """

    def __init__(self):
        # Load scoring constants from central config to improve maintainability
        self.scoring_matrix = PLANET_SCORING_MATRIX

    def calculate_strength(self, planet_data: dict, shadbala_data: dict = None) -> dict:
        """
        Calculates the overall strength of a planet.
        
        Args:
            planet_data (dict): Normalized JSON data for a single planet.
            shadbala_data (dict): Optional authentic shadbala metrics extracted from the PDF.
            
        Returns:
            dict: Explainable payload with final score and score breakdown.
        """
        breakdown = {}
        total_score = 0

        # 1. Evaluate Dignity
        dignity_score = self._evaluate_dignity(planet_data.get("dignity", "neutral"))
        breakdown["dignity"] = dignity_score

        # 2. Evaluate House Placement
        house_score = self._evaluate_house(planet_data.get("house_type", "neutral"))
        breakdown["house_placement"] = house_score

        # 3. Evaluate State (Combustion / Retrogression)
        state_score = self._evaluate_state(
            planet_data.get("is_combust", False),
            planet_data.get("is_retrograde", False)
        )
        breakdown["state_modifiers"] = state_score

        # 4. Evaluate Aspects & Conjunctions
        aspect_score = self._evaluate_aspects(
            planet_data.get("benefic_aspects_count", 0),
            planet_data.get("malefic_aspects_count", 0)
        )
        breakdown["aspects"] = aspect_score

        # Check if authentic shadbala data is available
        planet_name = planet_data.get("name", "unknown").lower()
        # Look for English name or fallback to handling exact dict keys if needed
        # The parser normalizes keys to english names (sun, moon, etc.)
        shadbala_info = None
        if shadbala_data and isinstance(shadbala_data, dict):
            shadbala_info = shadbala_data.get(planet_name)

        if shadbala_info and "required_percentage" in shadbala_info:
            req_pct = float(shadbala_info["required_percentage"])
            base_score = self._map_shadbala_to_score(req_pct)
            breakdown["shadbala_base_score"] = base_score
            total_score = base_score
        else:
            # Fallback to legacy additive heuristics
            total_score = dignity_score + house_score + state_score + aspect_score

        # 5. Future Extensibility: Ashtakavarga & Vargas (Phase 3+ enhancements)
        bav_score = self._evaluate_ashtakavarga(planet_data.get("bav_points", 0)) or 0
        if bav_score:
            breakdown["ashtakavarga_support"] = bav_score
            total_score += bav_score
            
        varga_score = self._evaluate_varga_support(planet_data.get("varga_data", {})) or 0
        if varga_score:
            breakdown["varga_support"] = varga_score
            total_score += varga_score

        # Clamp final score between 0 and 100
        final_score = clamp_score(total_score)

        return {
            "metadata": {
                "entity_id": planet_data.get("name", "unknown"),
                "entity_type": "planet"
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

    def _evaluate_dignity(self, dignity: str) -> int:
        # Normalise: lower-case and replace spaces with underscores so that
        # both 'Own Sign' (raw PDF form) and 'own_sign' (canonical form) resolve
        # correctly to the matrix key.  Without this, 'own sign' falls back to
        # 'neutral' (10) instead of 'own_sign' (35) — a silent scoring error.
        key = dignity.lower().replace(" ", "_")
        return self.scoring_matrix["dignity"].get(key, self.scoring_matrix["dignity"]["neutral"])

    def _evaluate_house(self, house_type: str) -> int:
        # Same normalisation as dignity: 'Own House' -> 'own_house', etc.
        key = house_type.lower().replace(" ", "_")
        return self.scoring_matrix["house_placement"].get(key, self.scoring_matrix["house_placement"]["neutral"])


    def _evaluate_state(self, is_combust: bool, is_retrograde: bool) -> int:
        score = 0
        if is_combust: score += self.scoring_matrix["state_modifiers"]["combust"]
        if is_retrograde: score += self.scoring_matrix["state_modifiers"]["retrograde"]
        return score

    def _evaluate_aspects(self, benefic_count: int, malefic_count: int) -> int:
        score = (benefic_count * self.scoring_matrix["aspects"]["benefic_aspect"])
        score += (malefic_count * self.scoring_matrix["aspects"]["malefic_aspect"])
        return score

    def _map_shadbala_to_score(self, req_pct: float) -> float:
        """
        Maps Shadbala required_percentage to the [0, 100] internal probability scale.
        Anchors:
            >= 160 -> 100
            140 -> 80
            120 -> 65
            100 -> 50
            80 -> 35
            <= 40 -> 0
        """
        anchors = [
            (0, 0),
            (40, 0),
            (80, 35),
            (100, 50),
            (120, 65),
            (140, 80),
            (160, 100)
        ]
        
        if req_pct <= anchors[1][0]:
            return anchors[1][1]
        elif req_pct >= anchors[-1][0]:
            return anchors[-1][1]
            
        for i in range(len(anchors) - 1):
            lo_p, lo_s = anchors[i]
            hi_p, hi_s = anchors[i + 1]
            if lo_p <= req_pct <= hi_p:
                t = (req_pct - lo_p) / (hi_p - lo_p)
                return lo_s + t * (hi_s - lo_s)
        return 50.0

    # --- Future Extensibility Stubs ---

    def _evaluate_ashtakavarga(self, bav_points: int) -> int:
        """Stub for future Phase integration of Bhinna Ashtakavarga support."""
        pass

    def _evaluate_varga_support(self, varga_data: dict) -> int:
        """Stub for future Phase integration of D9/Varga manifestation refinement."""
        pass

    def _generate_confidence_flags(self, raw_score: float, final_score: int) -> list:
        """Generates debug and synthesis flags based on the score."""
        flags = []
        if raw_score < 0:
            flags.append("clamped_to_zero")
            flags.append("severely_afflicted")
        elif raw_score > 100:
            flags.append("clamped_to_100")
        elif raw_score > 75:
            flags.append("highly_dignified")
        return flags