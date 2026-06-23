from typing import Any, Dict, List, Union
from app.config.astrology_constants import (
    DOMAIN_CONFIG, DOMAIN_KARAKA, NATAL_PROMISE_GRADES,
    DOMAIN_BONUSES, SAV_BINDU_SCALE
)
from app.utils.astrology_math import clamp_score

_NEUTRAL = 50.0

class NatalPromiseEngine:
    """
    Deterministic natal promise scoring engine.

    Evaluates the birth chart promise for 8 life domains using a
    strict 4-pillar weighted formula per domain:

        bhava          × 0.35   (HouseStrengthEngine)
        bhavadhipati   × 0.30   (PlanetStrengthEngine lord of primary house)
        karaka         × 0.20   (PlanetStrengthEngine natural significator)
        varga          × 0.15   (VargaEngine domain-specific chart)
        + yoga_bonus            (Dhana / Ketu amplifier / benefic protection)

    Architecture Rules:
        - No Double Penalty Rule: Afflictions are evaluated strictly inside Planet/House engines.
        - Zero astrological recalculation. Consumes pre-computed scores only.
        - No AI/ML. Pure arithmetic.
    """

    def __init__(self):
        self.domains  = list(DOMAIN_CONFIG.keys())
        self.config   = DOMAIN_CONFIG
        self.karaka   = DOMAIN_KARAKA
        self.grades   = NATAL_PROMISE_GRADES

    def evaluate(
        self,
        planet_results:    Dict[str, Any],
        house_results:     Dict[str, Any],
        rasi_results:      Dict[str, Any],
        varga_results:     Dict[str, Any],
        av_results:        Dict[str, Any],
        yoga_results:      Dict[str, Any],
        normalized_houses: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluates natal promise for all 8 domains.
        """
        result = {}
        for domain in self.domains:
            result[domain] = self._score_domain(
                domain, planet_results, house_results,
                varga_results, normalized_houses, yoga_results
            )
        print("NatalPromiseEngine output sample (Marriage):", result.get("marriage", {}).get("score"))
        return result

    def _score_domain(
        self,
        domain:            str,
        planet_results:    dict,
        house_results:     dict,
        varga_results:     dict,
        normalized_houses: dict,
        yoga_results:      dict,
    ) -> dict:
        cfg     = self.config[domain]
        weights = cfg["weights"]

        # --- Pillar 1: Bhava Strength (35%) ---
        primary_houses = cfg["primary_house"]
        f_bhava, primary_house_key = self._primary_house_score(
            primary_houses, house_results
        )

        # --- Pillar 2: Bhavadhipati Strength (30%) ---
        f_bhavadhipati = self._lord_score(
            primary_house_key, normalized_houses, planet_results
        )

        # --- Pillar 3: Karaka Strength (20%) ---
        karaka_cfg = self.karaka[domain]
        f_karaka = self._karaka_score(
            karaka_cfg["primary"], karaka_cfg.get("secondary"), planet_results, domain
        )

        # --- Pillar 4: Varga Validation (15%) ---
        varga_id = cfg["varga"]
        f_varga = self._varga_score(varga_id, varga_results, karaka_cfg["primary"])

        # --- Weighted sum ---
        raw = (
            weights["bhava"]        * f_bhava +
            weights["bhavadhipati"] * f_bhavadhipati +
            weights["karaka"]       * f_karaka  +
            weights["varga"]        * f_varga
        )

        # --- Yoga bonuses ---
        bonus_total = 0.0
        y_cats = yoga_results.get("category_summaries", {})
        
        if domain == "wealth":
            bonus_total += y_cats.get("Dhana Yoga", {}).get("max_strength", 0) * 0.15
        elif domain == "career":
            bonus_total += y_cats.get("Raja Yoga", {}).get("max_strength", 0) * 0.15
            bonus_total += y_cats.get("Neecha Bhanga Raja Yoga", {}).get("max_strength", 0) * 0.10
        elif domain == "health":
            bonus_total -= y_cats.get("Arishta Yoga", {}).get("max_strength", 0) * 0.15
        elif domain in ["education", "spirituality"]:
            bonus_total += y_cats.get("Gaja Kesari Yoga", {}).get("max_strength", 0) * 0.10
            
        raw += bonus_total

        score   = clamp_score(round(raw))
        promise = self._promise_grade(score)

        return {
            "score":   score,
            "raw_score": round(raw - bonus_total, 4),
            "promise": promise,
            "breakdown": {
                "bhava":          round(f_bhava, 2),
                "bhavadhipati":   round(f_bhavadhipati, 2),
                "karaka":         round(f_karaka,  2),
                "varga":          round(f_varga,   2),
                "yoga_bonus":     bonus_total,
            },
            "primary_house": primary_house_key,
            "varga_chart":   varga_id,
            "karaka":        karaka_cfg["primary"],
            "afflictions":   [], # Afflictions are now handled inside the respective planet/house engines
        }

    # -------------------------------------------------------------------------
    # Factor Computations
    # -------------------------------------------------------------------------

    def _primary_house_score(
        self,
        primary_house: Union[str, List[str]],
        house_results: dict
    ):
        if isinstance(primary_house, list):
            scores = [
                house_results.get(h, {}).get("final_score", _NEUTRAL)
                for h in primary_house
            ]
            avg = sum(scores) / len(scores) if scores else _NEUTRAL
            return avg, primary_house[0]
        else:
            score = house_results.get(primary_house, {}).get("final_score", _NEUTRAL)
            return score, primary_house

    def _karaka_score(
        self,
        primary_karaka:   str,
        secondary_karaka: str,
        planet_results:   dict,
        domain:           str,
    ) -> float:
        p_score = planet_results.get(primary_karaka, {}).get("final_score", _NEUTRAL)

        if secondary_karaka is None:
            return p_score

        s_score = planet_results.get(secondary_karaka, {}).get("final_score", _NEUTRAL)

        blend = {
            "career":      max(p_score, (p_score + s_score) / 2),
            "education":   0.60 * p_score + 0.40 * s_score,
            "children":    0.70 * p_score + 0.30 * s_score,
            "property":    0.60 * p_score + 0.40 * s_score,
            "health":      0.60 * p_score + 0.40 * s_score,
        }
        return blend.get(domain, p_score)

    def _lord_score(
        self,
        primary_house_key: str,
        normalized_houses: dict,
        planet_results:    dict,
    ) -> float:
        lord = normalized_houses.get(primary_house_key, {}).get("lord", "")
        if not lord or lord not in planet_results:
            return _NEUTRAL
        return planet_results[lord].get("final_score", _NEUTRAL)

    def _varga_score(
        self,
        varga_id:      str,
        varga_results: dict,
        primary_karaka: str,
    ) -> float:
        varga = varga_results.get(varga_id, {})
        if not varga:
            return _NEUTRAL

        net = 0.0
        planets_in_varga = varga.get("planets", {})
        for planet_data in planets_in_varga.values():
            mods = planet_data.get("modifiers", {})
            net += sum(mods.values())
            if planet_data.get("is_vargottama"):
                net += 15.0 

        score = clamp_score(_NEUTRAL + net)
        return score

    def _promise_grade(self, score: int) -> str:
        for threshold, label in self.grades:
            if score >= threshold:
                return label
        return "PRESENT"

