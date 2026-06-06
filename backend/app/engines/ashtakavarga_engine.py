from app.config.astrology_constants import (
    SAV_BINDU_SCALE,
    BAV_GRADE_THRESHOLDS,
    BAV_PLANET_MODIFIER,
    SAV_FAVORABLE_THRESHOLD,
    SAV_STRONG_THRESHOLD,
    SAV_WEAK_THRESHOLD,
    DASHA_BAV_CONFIDENCE,
    BAV_EXCLUDED_PLANETS,
    BAV_PLANETS
)
from app.utils.astrology_math import clamp_score


class AshtakavargaEngine:
    """
    Deterministic Ashtakavarga scoring engine.

    Processes extracted BAV (Bhinnashtakavarga) and SAV (Sarvashtakavarga)
    bindu data from canonical_content.json.

    Produces:
        1. BAV chart with grade per house per planet
        2. SAV chart with normalized score per house
        3. Planet BAV support modifiers (injected into PlanetStrengthEngine)
        4. Dasha lord BAV support and timing confidence multiplier
        5. SAV analytics (totals, peaks, favorable/unfavorable classification)
        6. Cross-engine modifier summary

    Architecture Rules:
        - Zero astrological recalculation. (Rule 4)
        - Reads SAV/BAV as extracted values; does NOT recompute from positions.
        - BAV consistency check raises a flag but does NOT override either value.
        - Rahu/Ketu excluded from BAV (classical Parashari standard).
        - All constants in astrology_constants.py.
    """

    def __init__(self):
        self.sav_scale         = SAV_BINDU_SCALE
        self.bav_grade_map     = BAV_GRADE_THRESHOLDS
        self.planet_modifier   = BAV_PLANET_MODIFIER
        self.dasha_confidence  = DASHA_BAV_CONFIDENCE
        self.excluded_planets  = BAV_EXCLUDED_PLANETS
        self.bav_planets       = BAV_PLANETS

    # -------------------------------------------------------------------------
    # Public Interface
    # -------------------------------------------------------------------------

    def evaluate(
        self,
        normalized_payload: dict,
        dependency_scores: dict = None
    ) -> dict:
        """
        Evaluates complete Ashtakavarga analysis.

        Args:
            normalized_payload (dict): Full JsonNormalizer output.
                Required keys: "ashtakavarga", "planets", "dashas"
            dependency_scores (dict): PlanetStrengthEngine outputs.
                Keyed by planet system name → {"final_score": int}

        Returns:
            dict: Full AV analysis payload (see module docstring).
        """
        dependency_scores  = dependency_scores or {}
        av_data            = normalized_payload.get("ashtakavarga", {})
        normalized_planets = normalized_payload.get("planets", {})
        normalized_dashas  = normalized_payload.get("dashas", {})

        raw_sav = av_data.get("sav_chart",  {})
        raw_bav = av_data.get("bav_charts", {})

        # --- Core computations ---
        bav_charts_out     = self._build_bav_charts(raw_bav)
        sav_chart_out      = self._build_sav_chart(raw_sav)
        planet_bav_support = self._compute_planet_bav_support(
            normalized_planets, raw_bav, dependency_scores
        )
        dasha_bav_support  = self._compute_dasha_bav_support(
            normalized_dashas, normalized_planets, raw_bav
        )
        sav_analytics      = self._compute_sav_analytics(raw_sav, raw_bav)
        engine_modifiers   = self._build_engine_modifiers(
            planet_bav_support, dasha_bav_support
        )

        return {
            "bav_charts":        bav_charts_out,
            "sav_chart":         sav_chart_out,
            "planet_bav_support": planet_bav_support,
            "dasha_bav_support": dasha_bav_support,
            "sav_analytics":     sav_analytics,
            "engine_modifiers":  engine_modifiers
        }

    # -------------------------------------------------------------------------
    # BAV Charts
    # -------------------------------------------------------------------------

    def _build_bav_charts(self, raw_bav: dict) -> dict:
        """
        Builds the annotated BAV chart for each of the 7 classical planets.
        Each house entry gets: bindus (int) and grade (str).
        """
        result = {}
        for planet in self.bav_planets:
            if planet not in raw_bav:
                continue
            house_data = raw_bav[planet]
            planet_chart = {}
            for house_str in [str(h) for h in range(1, 13)]:
                bindus = int(house_data.get(house_str, 0))
                planet_chart[house_str] = {
                    "bindus": bindus,
                    "grade":  self._bav_grade(bindus)
                }
            result[planet] = planet_chart
        return result

    # -------------------------------------------------------------------------
    # SAV Chart
    # -------------------------------------------------------------------------

    def _build_sav_chart(self, raw_sav: dict) -> dict:
        """
        Builds the annotated SAV chart for all 12 houses.
        Each house entry gets: bindus, score (piecewise normalized), grade, is_favorable.
        """
        result = {}
        for house_num in range(1, 13):
            house_str = str(house_num)
            bindus    = int(raw_sav.get(house_str, 0))
            score     = self._sav_score(bindus)
            result[house_str] = {
                "bindus":       bindus,
                "score":        round(score, 2),
                "grade":        self._sav_grade(bindus),
                "is_favorable": bindus >= SAV_FAVORABLE_THRESHOLD,
                "is_strong":    bindus >= SAV_STRONG_THRESHOLD,
                "is_weak":      bindus < SAV_WEAK_THRESHOLD
            }
        return result

    # -------------------------------------------------------------------------
    # Planet BAV Support
    # -------------------------------------------------------------------------

    def _compute_planet_bav_support(
        self,
        normalized_planets: dict,
        raw_bav: dict,
        dependency_scores: dict
    ) -> dict:
        """
        For each of the 7 BAV planets, computes:
            - natal house number
            - BAV bindus in that house (from planet's own BAV chart)
            - normalized score
            - grade
            - modifier (+5 / 0 / -5) → fed to PlanetStrengthEngine

        Missing BAV chart → default 4 bindus (neutral / AVERAGE).
        Missing natal house → house 0 (safe fallback, no modifier applied).
        """
        result = {}
        for planet in self.bav_planets:
            planet_data = normalized_planets.get(planet, {})
            house       = int(planet_data.get("house", 0))
            house_str   = str(house)

            # Read bindus from planet's own BAV chart for its natal house
            planet_bav  = raw_bav.get(planet, {})
            if planet_bav and house > 0:
                bindus = int(planet_bav.get(house_str, 4))  # 4 = neutral default
            elif house == 0:
                bindus = 4  # unknown house → neutral
            else:
                bindus = 4  # missing BAV chart → neutral

            score    = self._bav_score(bindus)
            grade    = self._bav_grade(bindus)
            modifier = self._bav_modifier(bindus)

            result[planet] = {
                "house":    house,
                "bindus":   bindus,
                "score":    round(score, 2),
                "grade":    grade,
                "modifier": modifier
            }
        return result

    # -------------------------------------------------------------------------
    # Dasha BAV Support
    # -------------------------------------------------------------------------

    def _compute_dasha_bav_support(
        self,
        normalized_dashas: dict,
        normalized_planets: dict,
        raw_bav: dict
    ) -> dict:
        """
        Computes BAV support for the active Mahadasha and Antardasha lords.

        For each dasha lord:
            - Finds the lord's natal house from normalized_planets
            - Reads the lord's own BAV bindus in that house
            - Calculates a timing confidence multiplier

        Combined dasha BAV score: 0.60 × MD_score + 0.40 × AD_score
        Timing confidence multiplier from DASHA_BAV_CONFIDENCE.
        """
        md_lord = normalized_dashas.get("mahadasha", {}).get("lord", "")
        ad_lord = normalized_dashas.get("antardasha", {}).get("lord", "")

        md_data = self._single_dasha_bav(md_lord, normalized_planets, raw_bav)
        ad_data = self._single_dasha_bav(ad_lord, normalized_planets, raw_bav)

        combined = round(0.60 * md_data["score"] + 0.40 * ad_data["score"], 2)
        combined_confidence  = self._confidence_label(combined)
        combined_multiplier  = self.dasha_confidence[combined_confidence]

        return {
            "mahadasha":                   md_data,
            "antardasha":                  ad_data,
            "combined_dasha_bav_score":    combined,
            "timing_confidence":           combined_confidence,
            "timing_confidence_multiplier": combined_multiplier
        }

    def _single_dasha_bav(
        self,
        lord: str,
        normalized_planets: dict,
        raw_bav: dict
    ) -> dict:
        """Computes BAV data for a single dasha lord."""
        if not lord or lord in self.excluded_planets:
            # Rahu/Ketu as dasha lords have no BAV → neutral defaults
            return {
                "lord": lord, "house": 0,
                "bindus": 4, "score": 50.0,
                "grade": "AVERAGE", "timing_confidence": "moderate"
            }

        planet_data = normalized_planets.get(lord, {})
        house       = int(planet_data.get("house", 0))
        house_str   = str(house)

        planet_bav = raw_bav.get(lord, {})
        bindus     = int(planet_bav.get(house_str, 4)) if (planet_bav and house > 0) else 4
        score      = self._bav_score(bindus)
        grade      = self._bav_grade(bindus)
        confidence = self._confidence_label(score)

        return {
            "lord":              lord,
            "house":             house,
            "bindus":            bindus,
            "score":             round(score, 2),
            "grade":             grade,
            "timing_confidence": confidence
        }

    # -------------------------------------------------------------------------
    # SAV Analytics
    # -------------------------------------------------------------------------

    def _compute_sav_analytics(self, raw_sav: dict, raw_bav: dict) -> dict:
        """
        Computes aggregate SAV statistics.

        Includes:
            - total_bindus (sum of all 12 houses)
            - average_per_house
            - peak_house (highest SAV)
            - weakest_house (lowest SAV)
            - favorable_houses (bindus >= 28)
            - unfavorable_houses (bindus < 22)
            - bav_consistency_check: per-house flag where BAV sum == SAV bindu
        """
        totals = {}
        for h in range(1, 13):
            hs = str(h)
            totals[hs] = int(raw_sav.get(hs, 0))

        total_bindus   = sum(totals.values())
        avg_per_house  = round(total_bindus / 12, 2)
        peak_house     = max(totals, key=totals.get) if totals else "1"
        weakest_house  = min(totals, key=totals.get) if totals else "1"
        favorable      = [h for h, b in totals.items() if b >= SAV_FAVORABLE_THRESHOLD]
        unfavorable    = [h for h, b in totals.items() if b < SAV_WEAK_THRESHOLD]

        # BAV consistency check: sum(BAV per house for 7 planets) vs SAV
        consistency = {}
        for h in range(1, 13):
            hs = str(h)
            bav_sum = sum(
                int(raw_bav.get(p, {}).get(hs, 0))
                for p in self.bav_planets
            )
            sav_val = totals[hs]
            consistency[hs] = {
                "bav_sum":    bav_sum,
                "sav_val":    sav_val,
                "consistent": bav_sum == sav_val
            }

        all_consistent = all(v["consistent"] for v in consistency.values())

        return {
            "total_bindus":        total_bindus,
            "average_per_house":   avg_per_house,
            "peak_house":          peak_house,
            "weakest_house":       weakest_house,
            "favorable_houses":    sorted(favorable, key=int),
            "unfavorable_houses":  sorted(unfavorable, key=int),
            "bav_consistency_check": all_consistent,
            "house_consistency":   consistency
        }

    # -------------------------------------------------------------------------
    # Engine Modifier Summary
    # -------------------------------------------------------------------------

    def _build_engine_modifiers(
        self,
        planet_bav_support: dict,
        dasha_bav_support:  dict
    ) -> dict:
        """
        Assembles the cross-engine modifier dict for consumption by PipelineRunner.

        planet_score_adjustments → injected into PlanetStrengthEngine
        dasha_bav_confidence_multiplier → injected into DashaEngine
        """
        planet_adjustments = {
            planet: data["modifier"]
            for planet, data in planet_bav_support.items()
        }

        return {
            "planet_score_adjustments":      planet_adjustments,
            "dasha_bav_confidence_multiplier": dasha_bav_support.get(
                "timing_confidence_multiplier", 1.0
            )
        }

    # -------------------------------------------------------------------------
    # Scoring Helpers
    # -------------------------------------------------------------------------

    def _bav_score(self, bindus: int) -> float:
        """Linear mapping: 0-8 bindus → 0-100 score. Range is inherently [0,100]."""
        return round((bindus / 8) * 100, 2)

    def _sav_score(self, bindus: int) -> float:
        """
        Piecewise linear interpolation of SAV bindus → 0-100 score.
        Uses SAV_BINDU_SCALE anchors from astrology_constants.py.
        Canonical implementation shared with RasiStrengthEngine.
        """
        anchors = self.sav_scale

        if bindus <= anchors[0][0]:
            return float(anchors[0][1])
        if bindus >= anchors[-1][0]:
            return float(anchors[-1][1])

        for i in range(len(anchors) - 1):
            lo_b, lo_s = anchors[i]
            hi_b, hi_s = anchors[i + 1]
            if lo_b <= bindus <= hi_b:
                t = (bindus - lo_b) / (hi_b - lo_b)
                return lo_s + t * (hi_s - lo_s)

        return 50.0

    def _bav_grade(self, bindus: int) -> str:
        """Returns classical Vedic BAV grade for a given bindu count."""
        for threshold, grade in self.bav_grade_map:
            if bindus >= threshold:
                return grade
        return "CRITICAL"

    def _sav_grade(self, bindus: int) -> str:
        """Returns SAV-specific grade based on classical thresholds."""
        if bindus >= SAV_STRONG_THRESHOLD:    return "STRONG"
        if bindus >= SAV_FAVORABLE_THRESHOLD: return "FAVORABLE"
        if bindus >= SAV_WEAK_THRESHOLD:      return "AVERAGE"
        if bindus > 0:                        return "WEAK"
        return "CRITICAL"

    def _bav_modifier(self, bindus: int) -> int:
        """Returns the planet score adjustment based on BAV bindu count."""
        if bindus >= 5:  return self.planet_modifier["high"]
        if bindus == 4:  return self.planet_modifier["neutral"]
        return self.planet_modifier["low"]

    def _confidence_label(self, score: float) -> str:
        """Maps a 0-100 BAV score to a timing confidence label."""
        if score >= 62.5:  return "high"
        if score >= 50.0:  return "moderate"
        return "low"
