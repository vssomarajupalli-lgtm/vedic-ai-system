from typing import Any, Dict, List, Union
from app.config.astrology_constants import (
    DOMAIN_CONFIG, DOMAIN_KARAKA, NATAL_PROMISE_GRADES,
    AFFLICTION_PENALTIES, AFFLICTION_CAP, DOMAIN_BONUSES,
    DUSTHANA_HOUSES, SAV_BINDU_SCALE, SIGN_LORD_MAP,
    NATURAL_MALEFICS
)
from app.utils.astrology_math import clamp_score


_NEUTRAL = 50.0   # score returned when a factor has no data


class NatalPromiseEngine:
    """
    Deterministic natal promise scoring engine.

    Evaluates the birth chart promise for 8 life domains using a
    6-factor weighted formula per domain:

        primary_house  × w1   (HouseStrengthEngine)
        support_houses × w2   (HouseStrengthEngine — averaged)
        karaka_planet  × w3   (PlanetStrengthEngine natural significator)
        house_lord     × w4   (PlanetStrengthEngine lord of primary house)
        varga          × w5   (VargaEngine domain-specific chart)
        sav_support    × w6   (AshtakavargaEngine SAV bindus)
        + yoga_bonus          (Dhana / Ketu amplifier / benefic protection)
        + affliction_penalty  (discrete penalties, capped per domain)

    Architecture Rules:
        - Zero astrological recalculation. Consumes pre-computed scores only.
        - normalized_houses is read ONLY for affliction detection (occupants,
          lord names, aspects). It is never scored here.
        - No AI/ML. Pure arithmetic.
    """

    def __init__(self):
        self.domains  = list(DOMAIN_CONFIG.keys())
        self.config   = DOMAIN_CONFIG
        self.karaka   = DOMAIN_KARAKA
        self.grades   = NATAL_PROMISE_GRADES

    # -------------------------------------------------------------------------
    # Public Interface
    # -------------------------------------------------------------------------

    def evaluate(
        self,
        planet_results:    Dict[str, Any],
        house_results:     Dict[str, Any],
        rasi_results:      Dict[str, Any],
        varga_results:     Dict[str, Any],
        av_results:        Dict[str, Any],
        normalized_houses: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluates natal promise for all 8 domains.

        Args:
            planet_results:    PlanetStrengthEngine outputs (BAV-adjusted)
            house_results:     HouseStrengthEngine outputs
            rasi_results:      RasiStrengthEngine outputs (for sign lookup)
            varga_results:     VargaEngine outputs
            av_results:        AshtakavargaEngine outputs (SAV chart)
            normalized_houses: JsonNormalizer house dicts (occupants/lord/sign)

        Returns:
            dict: {domain: {score, promise, breakdown, ...}} for all 8 domains.
        """
        # Pre-compute affliction flags once — shared across all domains
        affliction_flags = self._detect_affliction_flags(
            normalized_houses, planet_results
        )
        # Pre-compute yoga bonus flags once
        bonus_flags = self._detect_bonus_flags(
            normalized_houses, planet_results
        )

        result = {}
        for domain in self.domains:
            result[domain] = self._score_domain(
                domain, planet_results, house_results,
                varga_results, av_results, normalized_houses,
                affliction_flags, bonus_flags
            )
        return result

    # -------------------------------------------------------------------------
    # Domain Scoring
    # -------------------------------------------------------------------------

    def _score_domain(
        self,
        domain:            str,
        planet_results:    dict,
        house_results:     dict,
        varga_results:     dict,
        av_results:        dict,
        normalized_houses: dict,
        affliction_flags:  List[str],
        bonus_flags:       List[str],
    ) -> dict:
        cfg     = self.config[domain]
        weights = cfg["weights"]

        # --- Factor 1: Primary house score ---
        primary_houses = cfg["primary_house"]
        f_primary, primary_house_key = self._primary_house_score(
            primary_houses, house_results
        )

        # --- Factor 2: Support house average (with optional inversion) ---
        inverted = cfg.get("inverted_support", False)
        f_support = self._support_house_avg(
            cfg["support_houses"], house_results, inverted
        )

        # --- Factor 3: Karaka planet score (primary + blended secondary) ---
        karaka_cfg = self.karaka[domain]
        f_karaka = self._karaka_score(
            karaka_cfg["primary"], karaka_cfg.get("secondary"), planet_results, domain
        )

        # --- Factor 4: Lord of primary house ---
        f_lord = self._lord_score(
            primary_house_key, normalized_houses, planet_results
        )

        # --- Factor 5: Domain varga validation score ---
        varga_id = cfg["varga"]
        f_varga = self._varga_score(varga_id, varga_results, karaka_cfg["primary"])

        # --- Factor 6: SAV support for primary house ---
        sav_chart = av_results.get("sav_chart", {})
        f_sav = self._sav_score(primary_house_key, sav_chart)

        # --- Weighted sum ---
        raw = (
            weights["primary_house"]  * f_primary +
            weights["support_houses"] * f_support +
            weights["karaka"]         * f_karaka  +
            weights["lord"]           * f_lord    +
            weights["varga"]          * f_varga   +
            weights["sav"]            * f_sav
        )

        # --- Yoga bonuses ---
        bonus_total = self._compute_bonuses(domain, bonus_flags)
        raw += bonus_total

        # --- Affliction penalties (capped) ---
        penalty_total = self._compute_penalties(domain, affliction_flags)
        raw += penalty_total       # penalty_total is already ≤ 0

        score   = clamp_score(round(raw))
        promise = self._promise_grade(score)

        return {
            "score":   score,
            "raw_score": round(raw - bonus_total - penalty_total, 4),  # pre-adjustments
            "promise": promise,
            "breakdown": {
                "primary_house":    round(f_primary, 2),
                "support_houses":   round(f_support, 2),
                "karaka_planet":    round(f_karaka,  2),
                "house_lord":       round(f_lord,    2),
                "varga_support":    round(f_varga,   2),
                "sav_support":      round(f_sav,     2),
                "yoga_bonus":       bonus_total,
                "affliction_penalty": penalty_total,
            },
            "primary_house": primary_house_key,
            "varga_chart":   varga_id,
            "karaka":        karaka_cfg["primary"],
            "afflictions":   [f for f in affliction_flags
                              if domain in AFFLICTION_PENALTIES.get(f, {})],
        }

    # -------------------------------------------------------------------------
    # Factor Computations
    # -------------------------------------------------------------------------

    def _primary_house_score(
        self,
        primary_house: Union[str, List[str]],
        house_results: dict
    ):
        """
        Returns (score, house_key_str).
        If primary_house is a list (e.g. wealth uses ["2","11"]),
        averages the scores and returns the first house as the key.
        """
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

    def _support_house_avg(
        self,
        houses:       List[str],
        house_results: dict,
        inverted:      bool
    ) -> float:
        """
        Averages support house scores.
        For Health domain (inverted=True), strong affliction houses = bad.
        Inversion: contribution = 100 - house_score (strong H6/8/12 = weak health).
        Returns neutral 50 if no support houses have data.
        """
        if not houses:
            return _NEUTRAL
        scores = []
        for h in houses:
            raw = house_results.get(h, {}).get("final_score", _NEUTRAL)
            scores.append((100 - raw) if inverted else raw)
        return sum(scores) / len(scores)

    def _karaka_score(
        self,
        primary_karaka:   str,
        secondary_karaka: str,
        planet_results:   dict,
        domain:           str,
    ) -> float:
        """
        Computes blended karaka score.
        Some domains blend primary and secondary significators:
            career:     max(saturn, avg(saturn, sun))   — govt vs corporate
            education:  0.60 × mercury + 0.40 × jupiter — school vs wisdom
            children:   0.70 × jupiter + 0.30 × moon   — progeny vs nurture
            property:   0.60 × mars    + 0.40 × moon   — land vs home
            health:     0.60 × sun     + 0.40 × moon   — vitality vs mind
        All others: primary karaka only.
        """
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
        """
        Reads the lord name from normalized_houses[primary_house_key]["lord"]
        then fetches that planet's final_score from planet_results.
        Returns neutral 50 if lord is missing or unscored.
        """
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
        """
        Reads domain-specific varga modifiers for the karaka planet.
        Normalised: 50 + net_modifier, clamped to [0, 100].
        Returns neutral 50 if the varga chart was not extracted.
        """
        varga = varga_results.get(varga_id, {})
        if not varga:
            return _NEUTRAL

        # Aggregate all planet modifiers in this varga
        net = 0.0
        planets_in_varga = varga.get("planets", {})
        for planet_data in planets_in_varga.values():
            mods = planet_data.get("modifiers", {})
            net += sum(mods.values())
            if planet_data.get("is_vargottama"):
                net += 15.0  # vargottama bonus already in modifiers but guard for raw data

        # Normalize around neutral baseline 50
        score = clamp_score(_NEUTRAL + net)
        return score

    def _sav_score(
        self,
        house_key: str,
        sav_chart: dict,
    ) -> float:
        """
        Converts SAV bindus for a house to [0, 100] using SAV_BINDU_SCALE.

        AshtakavargaEngine produces annotated dicts: {"bindus": int, "score": float, ...}
        Raw normalized payload produces plain ints.
        Both formats are handled safely.

        Returns neutral 50 if bindus are missing.
        """
        raw = sav_chart.get(house_key)
        if raw is None:
            return _NEUTRAL
        # Handle annotated dict from AshtakavargaEngine output
        if isinstance(raw, dict):
            bindus = int(raw.get("bindus", 0))
        else:
            bindus = int(raw)
        return self._interpolate(bindus, SAV_BINDU_SCALE)

    # -------------------------------------------------------------------------
    # Affliction Detection
    # -------------------------------------------------------------------------

    def _detect_affliction_flags(
        self,
        normalized_houses: dict,
        planet_results:    dict,
    ) -> List[str]:
        """
        Scans normalized house occupants and planet confidence flags to build
        a list of active affliction flag names (matching AFFLICTION_PENALTIES keys).

        All detection is from pre-extracted, normalized data — zero new calculations.
        """
        flags = []

        # House occupant afflictions
        occupant_checks = {
            "1":  ["rahu_in_1"],
            "2":  ["saturn_in_2"],
            "4":  ["saturn_in_4", "rahu_in_4"],
            "5":  ["saturn_in_5", "rahu_in_5", "ketu_in_5"],
            "7":  ["saturn_in_7", "mars_in_7", "rahu_in_7", "ketu_in_7"],
            "10": ["rahu_in_10"],
            "11": ["rahu_in_11"],
        }
        planet_trigger = {
            "rahu_in_1":   "rahu",
            "saturn_in_2": "saturn",
            "saturn_in_4": "saturn",
            "rahu_in_4":   "rahu",
            "saturn_in_5": "saturn",
            "rahu_in_5":   "rahu",
            "ketu_in_5":   "ketu",
            "saturn_in_7": "saturn",
            "mars_in_7":   "mars",
            "rahu_in_7":   "rahu",
            "ketu_in_7":   "ketu",
            "rahu_in_10":  "rahu",
            "rahu_in_11":  "rahu",
        }
        for h, flag_list in occupant_checks.items():
            occupants = normalized_houses.get(h, {}).get("occupants", [])
            for flag in flag_list:
                planet = planet_trigger.get(flag, "")
                if planet and planet in occupants:
                    flags.append(flag)

        # Saturn retrograde in 10th
        h10_occupants = normalized_houses.get("10", {}).get("occupants", [])
        if "saturn" in h10_occupants:
            saturn_flags = planet_results.get("saturn", {}).get("confidence_flags", [])
            if any("retro" in str(f) for f in saturn_flags):
                flags.append("saturn_retro_in_10")

        # Lord-in-dusthana checks (H6/8/12)
        lord_dusthana_map = {
            "5":  ["lord5_in_dusthana"],
            "4":  ["lord4_in_dusthana"],
            "10": ["lord10_in_dusthana"],
            "9":  [],  # no lord9_in_dusthana — handled separately
        }
        for h, flag_list in lord_dusthana_map.items():
            lord = normalized_houses.get(h, {}).get("lord", "")
            if not lord or not flag_list:
                continue
            lord_house = self._planet_house(lord, normalized_houses)
            if str(lord_house) in DUSTHANA_HOUSES:
                flags.extend(flag_list)

        # Lord5 debilitated
        lord5 = normalized_houses.get("5", {}).get("lord", "")
        if lord5 and lord5 in planet_results:
            l5_flags = planet_results[lord5].get("confidence_flags", [])
            if any("debilitat" in str(f) for f in l5_flags):
                flags.append("lord5_debilitated")

        # Lord9 combust
        lord9 = normalized_houses.get("9", {}).get("lord", "")
        if lord9 and lord9 in planet_results:
            l9_flags = planet_results[lord9].get("confidence_flags", [])
            if any("combust" in str(f) for f in l9_flags):
                flags.append("lord9_combust")

        # Planet state flags (combust, debilitated)
        planet_state_flags = {
            "venus_combust":      ("venus",   "combust"),
            "mercury_combust":    ("mercury", "combust"),
            "sun_combust":        ("sun",     "combust"),
            "jupiter_debilitated":("jupiter", "debilitat"),
            "mars_debilitated":   ("mars",    "debilitat"),
        }
        for flag, (planet, keyword) in planet_state_flags.items():
            p_flags = planet_results.get(planet, {}).get("confidence_flags", [])
            if any(keyword in str(f) for f in p_flags):
                flags.append(flag)

        # Saturn aspects lagna (aspected_by on H1)
        h1_aspected = normalized_houses.get("1", {}).get("aspected_by", [])
        if "saturn" in h1_aspected:
            flags.append("saturn_aspects_lagna")

        return flags

    def _detect_bonus_flags(
        self,
        normalized_houses: dict,
        planet_results:    dict,
    ) -> List[str]:
        """
        Detects classical yoga bonus conditions.
        Returns list of active bonus flag names (matching DOMAIN_BONUSES keys).
        """
        flags = []

        # Dhana Yoga: 2nd lord + 11th lord in same sign
        lord2 = normalized_houses.get("2", {}).get("lord", "")
        lord11 = normalized_houses.get("11", {}).get("lord", "")
        if lord2 and lord11:
            lord2_sign  = planet_results.get(lord2,  {}).get("sign", "")
            lord11_sign = planet_results.get(lord11, {}).get("sign", "")
            if lord2 == lord11 or (lord2_sign and lord2_sign == lord11_sign):
                flags.append("same_2_11_lords")

        # Jupiter in H2 or H11
        h2_occ  = normalized_houses.get("2",  {}).get("occupants", [])
        h11_occ = normalized_houses.get("11", {}).get("occupants", [])
        if "jupiter" in h2_occ or "jupiter" in h11_occ:
            flags.append("jupiter_in_2_or_11")

        # Venus in H2
        if "venus" in h2_occ:
            flags.append("venus_in_2")

        # Ketu strong in moksha houses (H9, H12, H5)
        ketu_score = planet_results.get("ketu", {}).get("final_score", 0)
        if ketu_score > 50:
            for h in ["9", "12", "5"]:
                if "ketu" in normalized_houses.get(h, {}).get("occupants", []):
                    flags.append("ketu_strong_in_moksha")
                    break

        # Jupiter aspects H7 (standard Vedic aspect from H4, H5, H9, H10 relative)
        h7_aspected = normalized_houses.get("7", {}).get("aspected_by", [])
        if "jupiter" in h7_aspected:
            flags.append("jupiter_aspects_7")

        # Venus exalted (Pisces)
        venus_flags = planet_results.get("venus", {}).get("confidence_flags", [])
        venus_dignity = planet_results.get("venus", {}).get("breakdown", {})
        if any("exalt" in str(f) for f in venus_flags):
            flags.append("venus_exalted")

        return flags

    # -------------------------------------------------------------------------
    # Penalty + Bonus Application
    # -------------------------------------------------------------------------

    def _compute_penalties(self, domain: str, affliction_flags: List[str]) -> float:
        """
        Sums all active affliction penalties for this domain.
        Caps at AFFLICTION_CAP[domain] to prevent over-penalisation.
        Returns a value ≤ 0.
        """
        total = 0.0
        cap   = AFFLICTION_CAP.get(domain, -25)
        for flag in affliction_flags:
            penalty = AFFLICTION_PENALTIES.get(flag, {}).get(domain, 0)
            total  += penalty
        return max(total, cap)  # cap is negative — max returns less-negative value

    def _compute_bonuses(self, domain: str, bonus_flags: List[str]) -> float:
        """
        Sums all active yoga bonuses for this domain.
        Returns a value ≥ 0.
        """
        total = 0.0
        for flag in bonus_flags:
            bonus = DOMAIN_BONUSES.get(flag, {}).get(domain, 0)
            total += bonus
        return total

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _primary_house_key(self, primary_house: Union[str, List[str]]) -> str:
        """Returns the first (or only) house key as a string."""
        return primary_house[0] if isinstance(primary_house, list) else primary_house

    def _planet_house(self, planet: str, normalized_houses: dict) -> int:
        """
        Returns the house number (1-12) where a planet is located,
        by scanning occupants in normalized_houses.
        Returns 0 if not found.
        """
        for h, data in normalized_houses.items():
            if planet in data.get("occupants", []):
                try:
                    return int(h)
                except ValueError:
                    pass
        return 0

    def _promise_grade(self, score: int) -> str:
        """Looks up the 4-tier promise label from NATAL_PROMISE_GRADES."""
        for threshold, label in self.grades:
            if score >= threshold:
                return label
        return "PRESENT"

    @staticmethod
    def _interpolate(value: float, scale: list) -> float:
        """
        Piecewise linear interpolation using the SAV_BINDU_SCALE anchor table.
        Returns a score in [0, 100].
        """
        if value <= scale[0][0]:
            return float(scale[0][1])
        if value >= scale[-1][0]:
            return float(scale[-1][1])
        for i in range(len(scale) - 1):
            x0, y0 = scale[i]
            x1, y1 = scale[i + 1]
            if x0 <= value <= x1:
                ratio = (value - x0) / (x1 - x0)
                return y0 + ratio * (y1 - y0)
        return float(scale[-1][1])
