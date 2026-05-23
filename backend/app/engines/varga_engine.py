from typing import Dict, Any

from app.config.astrology_constants import D9_SCORES, D10_SCORES, VARGOTTAMA_BONUS

class VargaEngine:
    """
    Varga Engine (Phase 5)
    Calculates structural refinements from D9 (Navamsha) and D10 (Dashamamsha).
    
    Adheres to the following Immutable Rules:
    - Stateless evaluation mapping.
    - Strict adherence to Standardized JSON Contract output.
    - Additive modifiers only (Immutable D1 Rule).
    """

    def __init__(self):
        # Load scoring constants from central config
        self.D9_SCORES = D9_SCORES
        self.D10_SCORES = D10_SCORES
        self.VARGOTTAMA_BONUS = VARGOTTAMA_BONUS

    def evaluate(self, normalized_data: Dict[str, Any], dependency_scores: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluates Varga modifiers for all planets in the chart.
        Dependency scores are passed in via the PipelineRunner.
        """
        if dependency_scores is None:
            dependency_scores = {}

        results = {}
        planets = normalized_data.get("planets", {})
        vargas_data = normalized_data.get("vargas", {})

        for planet_name, planet_d1_data in planets.items():
            # Pass the base_score directly so it remains completely immutable
            base_score = dependency_scores.get(planet_name, {}).get("final_score", 0.0)
            results[planet_name] = self._evaluate_planet(
                planet_name, planet_d1_data, vargas_data, base_score
            )

        return results

    def _evaluate_planet(self, planet_name: str, planet_d1_data: Dict[str, Any], vargas_data: Dict[str, Any], base_score: float) -> Dict[str, Any]:
        modifiers = {}
        confidence_flags = []

        d1_dignity = planet_d1_data.get("dignity", "neutral").lower()

        # 1. Evaluate D9 (Navamsha) - General Inner Strength & Refinement
        d9_data = vargas_data.get("D9", {}).get("planets", {}).get(planet_name, {})
        if d9_data:
            d9_dignity = d9_data.get("dignity", "neutral").lower()
            d9_score = self.D9_SCORES.get(d9_dignity, 0.0)

            if d9_score != 0.0:
                modifiers["D9_dignity_modifier"] = d9_score
                confidence_flags.append(f"D9_{d9_dignity}")

            # Predictability & Contradiction Flags
            if d1_dignity == "exalted" and d9_dignity == "debilitated":
                confidence_flags.append("varga_contradicted")
            elif d1_dignity == "debilitated" and d9_dignity == "exalted":
                confidence_flags.append("neecha_bhanga_varga")

            # Vargottama Evaluation (Check D1 & D9 Sign match)
            if d9_data.get("is_vargottama"):
                modifiers["D9_vargottama_bonus"] = self.VARGOTTAMA_BONUS
                confidence_flags.append("D9_vargottama")

        # 2. Evaluate D10 (Dashamamsha) - Career & Action Refinement
        d10_data = vargas_data.get("D10", {}).get("planets", {}).get(planet_name, {})
        if d10_data:
            d10_dignity = d10_data.get("dignity", "neutral").lower()
            d10_score = self.D10_SCORES.get(d10_dignity, 0.0)

            if d10_score != 0.0:
                modifiers["D10_dignity_modifier"] = d10_score
                confidence_flags.append(f"D10_{d10_dignity}")

        # 3. Standardized JSON Contract
        # Adheres to Rule 1 (Immutable D1): final_score is passed directly through
        return {
            "metadata": {
                "entity_id": planet_name,
                "entity_type": "planet"
            },
            "final_score": base_score,
            "breakdown": {},
            "modifiers": modifiers,
            "temporal_activation": {},
            "confidence_flags": confidence_flags
        }