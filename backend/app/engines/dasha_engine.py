from typing import Dict, Any
from app.config.astrology_constants import DASHA_SCORING_MATRIX
from app.utils.astrology_math import calculate_planetary_axis

class DashaEngine:
    """
    Dasha Engine (Phase 6)
    Evaluates temporal activation based on currently active Vimshottari Dasha lords.
    
    NOTE: This engine does NOT calculate timelines. It assumes the Mahadasha (MD)
    and Antardasha (AD) lords have been extracted from the PDF by the parser.
    It focuses exclusively on relationship analysis and timing multipliers.
    """

    def __init__(self):
        self.scoring_matrix = DASHA_SCORING_MATRIX

    def evaluate(self, normalized_data: Dict[str, Any], dependency_scores: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluates the timing multipliers for the currently active Dasha lords.
        """
        if dependency_scores is None:
            dependency_scores = {}

        results = {}
        dashas = normalized_data.get("dashas", {})
        
        md_lord = dashas.get("mahadasha", {}).get("lord")
        ad_lord = dashas.get("antardasha", {}).get("lord")

        # If the parser hasn't found active dashas, return an empty evaluation
        if not md_lord or not ad_lord:
            return results

        md_lord = md_lord.lower()
        ad_lord = ad_lord.lower()

        planets = normalized_data.get("planets", {})
        md_planet_data = planets.get(md_lord, {})
        ad_planet_data = planets.get(ad_lord, {})

        # Calculate the astrological axis (relationship) between MD and AD lords
        relationship_key = calculate_planetary_axis(
            md_planet_data.get("house", 1),
            ad_planet_data.get("house", 1)
        )

        relationship_multiplier = self.scoring_matrix["relationship_scalars"].get(relationship_key, 1.0)

        # Generate results for MD Lord
        md_base_score = dependency_scores.get(md_lord, {}).get("final_score", 0.0)
        results[md_lord] = self._build_dasha_payload(
            md_lord, md_base_score, "mahadasha", relationship_multiplier, relationship_key
        )

        # Generate results for AD Lord
        ad_base_score = dependency_scores.get(ad_lord, {}).get("final_score", 0.0)
        results[ad_lord] = self._build_dasha_payload(
            ad_lord, ad_base_score, "antardasha", relationship_multiplier, relationship_key
        )

        return results

    def _build_dasha_payload(self, entity_id: str, base_score: float, level: str, multiplier: float, axis: str) -> Dict[str, Any]:
        """Constructs the standard JSON contract with temporal activation populated."""
        return {
            "metadata": {
                "entity_id": entity_id,
                "entity_type": "planet"
            },
            "final_score": base_score, # Immutable D1 Rule
            "breakdown": {},
            "modifiers": {},
            "temporal_activation": {
                "active_dasha_level": level,
                "timing_multiplier": multiplier
            },
            "confidence_flags": [f"active_{level}", f"dasha_axis_{axis}"]
        }