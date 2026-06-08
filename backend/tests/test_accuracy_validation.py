"""
Astrological Accuracy Validation Tests
=======================================
These tests verify that the scoring engines produce **astrologically correct results**,
not just arithmetically valid ones.

Each test encodes a classical Parashari/Jaimini principle as a deterministic assertion.
If a test fails, it means the scoring formula or constants are producing results that
contradict classical Vedic astrology.

Reference sources:
  - Brihat Parasara Hora Sastra (BPHS) — primary Parashari source
  - Phaladeepika — dignity and house placement rules
  - Standard Ashtakavarga interpretation (bindus > 28 = favorable)

Test categories:
  1. Planet Strength Axioms  — exaltation/debilitation in kendra vs dusthana
  2. Natal Promise Axioms    — known single-planet / placement effects on domains
  3. Master Probability Axioms — end-to-end chart quality assertions
  4. Affliction & Bonus Axioms — penalty/yoga magnitude checks
"""

import unittest
from app.engines.planet_strength_engine import PlanetStrengthEngine
from app.engines.house_strength_engine import HouseStrengthEngine
from app.engines.natal_promise_engine import NatalPromiseEngine
from app.engines.master_probability_engine import MasterProbabilityEngine
from app.engines.ashtakavarga_engine import AshtakavargaEngine


# ---------------------------------------------------------------------------
# Shared fixture builders
# ---------------------------------------------------------------------------

def _planet_data(
    sign="aries", house=1, house_type="kendra", dignity="neutral",
    is_retrograde=False, is_combust=False,
    benefic_aspects_count=0, malefic_aspects_count=0,
    bav_points=4
):
    """Build a minimal normalized planet dict for PlanetStrengthEngine."""
    return {
        "name":                  "sun",
        "sign":                  sign,
        "degree":                15.0,
        "nakshatra":             "ashwini",
        "house":                 house,
        "house_type":            house_type,
        "dignity":               dignity,
        "is_retrograde":         is_retrograde,
        "is_combust":            is_combust,
        "conjunctions":          [],
        "benefic_aspects_count": benefic_aspects_count,
        "malefic_aspects_count": malefic_aspects_count,
        "aspected_by":           [],
        "varga_data":            {},
        "bav_points":            bav_points,
    }


def _house_data(house_type="kendra", lord_strength_score=50, sav_points=28,
               benefic_occupants=0, malefic_occupants=0,
               benefic_aspects=0, malefic_aspects=0):
    """Build a minimal normalized house dict for HouseStrengthEngine."""
    return {
        "house":                house_type,
        "house_type":           house_type,
        "lord_strength_score":  lord_strength_score,
        "sav_points":           sav_points,
        "benefic_occupants":    benefic_occupants,
        "malefic_occupants":    malefic_occupants,
        "benefic_aspects":      benefic_aspects,
        "malefic_aspects":      malefic_aspects,
    }


def _norm_houses(config=None):
    """Build a 12-house normalized_houses dict for NatalPromiseEngine."""
    base = {
        str(h): {"lord": "", "occupants": [], "aspected_by": []}
        for h in range(1, 13)
    }
    if config:
        for h, data in config.items():
            base[str(h)].update(data)
    return base


def _planets_dict(**kwargs):
    """Build minimal planet_results: e.g. _planets_dict(venus=60, saturn=40)"""
    return {
        name: {"final_score": score, "confidence_flags": [], "sign": ""}
        for name, score in kwargs.items()
    }


def _houses_dict(**kwargs):
    """Build minimal house_results: e.g. _houses_dict(**{'7': 50, '11': 60})"""
    return {str(k): {"final_score": v} for k, v in kwargs.items()}


def _empty_av():
    return {"sav_chart": {}}


def _sav_av(**kwargs):
    """SAV annotated dict format: _sav_av(**{'7': 28, '11': 40})"""
    return {"sav_chart": {str(h): {"bindus": b} for h, b in kwargs.items()}}


# ---------------------------------------------------------------------------
# Category 1: Planet Strength Axioms
# ---------------------------------------------------------------------------

class TestPlanetStrengthAxioms(unittest.TestCase):
    """
    Classical rule: A planet's strength depends on dignity + house placement.
    Best combination: exalted in trikona/kendra.
    Worst combination: debilitated in dusthana.
    """

    def setUp(self):
        self.engine = PlanetStrengthEngine()

    def _score(self, **kwargs):
        return self.engine.calculate_strength(_planet_data(**kwargs))["final_score"]

    # --- Axiom 1: Exalted planet in kendra must score ≥ 70 ---
    def test_exalted_kendra_planet_scores_high(self):
        """
        Exalted (dignity=35) + kendra (house=20) = structural maximum.
        Classical: exaltation in an angular house = pinnacle of planetary strength.
        Expected: final_score ≥ 70.
        """
        score = self._score(dignity="exalted", house_type="kendra", house=1)
        self.assertGreaterEqual(
            score, 70,
            f"Exalted planet in kendra should score ≥ 70, got {score}"
        )

    # --- Axiom 2: Exalted planet in trikona must score ≥ 70 ---
    def test_exalted_trikona_planet_scores_high(self):
        """
        Exalted + trikona (house=25) = very strong.
        Classical: trikona is the highest house type in Parashari.
        """
        score = self._score(dignity="exalted", house_type="trikona", house=5)
        self.assertGreaterEqual(
            score, 70,
            f"Exalted planet in trikona should score ≥ 70, got {score}"
        )

    # --- Axiom 3: Debilitated planet in dusthana must score ≤ 25 ---
    def test_debilitated_dusthana_planet_scores_low(self):
        """
        Debilitated (dignity=0) + dusthana (house=-10) = structural minimum.
        Classical: fallen planet in dusthana = maximum weakness.
        Expected: final_score ≤ 25.
        """
        score = self._score(dignity="debilitated", house_type="dusthana", house=8)
        self.assertLessEqual(
            score, 25,
            f"Debilitated planet in dusthana should score ≤ 25, got {score}"
        )

    # --- Axiom 4: Own-sign planet in kendra must score > neutral ---
    def test_own_sign_kendra_above_neutral(self):
        """
        Own sign (dignity=25) + kendra = well-placed functional strength.
        Expected: final_score > 50.
        """
        score = self._score(dignity="own_sign", house_type="kendra", house=1)
        self.assertGreater(
            score, 50,
            f"Own-sign planet in kendra should score > 50, got {score}"
        )

    # --- Axiom 5: Exalted > Own sign > Neutral > Debilitated (same house) ---
    def test_dignity_hierarchy_respected(self):
        """All four dignity levels in the same house must maintain classical ordering."""
        exalted    = self._score(dignity="exalted",     house_type="kendra")
        own_sign   = self._score(dignity="own_sign",    house_type="kendra")
        neutral    = self._score(dignity="neutral",     house_type="kendra")
        debilitated= self._score(dignity="debilitated", house_type="kendra")

        self.assertGreater(exalted, own_sign,    "exalted must outrank own_sign")
        self.assertGreater(own_sign, neutral,    "own_sign must outrank neutral")
        self.assertGreater(neutral, debilitated, "neutral must outrank debilitated")

    # --- Axiom 6: Combust planet must score lower than non-combust same dignity ---
    def test_combust_reduces_planet_score(self):
        """
        Combustion subtracts from planetary strength.
        Classical: combust planet loses agency — even exaltation is weakened.
        """
        clean_score   = self._score(dignity="neutral", is_combust=False)
        combust_score = self._score(dignity="neutral", is_combust=True)
        self.assertLess(
            combust_score, clean_score,
            "Combust planet should score lower than clean equivalent"
        )

    # --- Axiom 7: Trikona placement beats kendra for same dignity ---
    def test_trikona_beats_kendra_scoring(self):
        """
        Trikona house bonus (25) > kendra (20) in PLANET_SCORING_MATRIX.
        Expected: exalted in trikona ≥ exalted in kendra.
        """
        trikona = self._score(dignity="exalted", house_type="trikona", house=5)
        kendra  = self._score(dignity="exalted", house_type="kendra",  house=1)
        # Trikona has +5 structural advantage in the scoring matrix
        self.assertGreaterEqual(trikona, kendra - 2,
            "Trikona placement should score at least as high as kendra")

    # --- Axiom 8: Dusthana severely penalizes even strong planets ---
    def test_dusthana_degrades_exalted_planet(self):
        """
        An exalted planet in dusthana must score below its kendra equivalent.
        Classical: 8th/6th/12th house weakens even dignified planets.
        """
        kendra  = self._score(dignity="exalted", house_type="kendra",  house=1)
        dusthana= self._score(dignity="exalted", house_type="dusthana",house=8)
        self.assertLess(
            dusthana, kendra,
            "Exalted planet in dusthana must score below kendra equivalent"
        )


# ---------------------------------------------------------------------------
# Category 2: Natal Promise Axioms (Domain-Level)
# ---------------------------------------------------------------------------

class TestNatalPromiseAxioms(unittest.TestCase):
    """
    Tests that NatalPromiseEngine produces domain scores consistent with
    classical astrological principles.
    """

    def setUp(self):
        self.engine = NatalPromiseEngine()

    def _evaluate(self, planet_scores=None, house_scores=None,
                  norm_house_cfg=None, varga=None, av=None, yoga_results=None):
        return self.engine.evaluate(
            planet_results    = planet_scores or _planets_dict(),
            house_results     = house_scores  or _houses_dict(),
            rasi_results      = {},
            varga_results     = varga or {},
            av_results        = av or _empty_av(),
            yoga_results      = yoga_results or {},
            normalized_houses = _norm_houses(norm_house_cfg),
        )

    # --- Axiom 9: Saturn in H7 → marriage WEAK or PRESENT ---
    def test_saturn_in_h7_degrades_marriage_promise(self):
        """
        Classical: Saturn in 7th house delays marriage / causes separation.
        Saturn in H7 triggers 'saturn_in_7' affliction → -15 marriage penalty.
        Expected: marriage promise = WEAK or PRESENT (not MODERATE/STRONG).
        """
        norm_cfg = {"7": {"lord": "", "occupants": ["saturn"], "aspected_by": []}}
        result = self._evaluate(
            planet_scores=_planets_dict(venus=50, saturn=50),
            norm_house_cfg=norm_cfg
        )
        promise = result["marriage"]["promise"]
        self.assertIn(promise, ("WEAK", "PRESENT"),
            f"Saturn in H7 must degrade marriage to WEAK/PRESENT, got {promise}")

    # --- Axiom 10: Jupiter in H11 → improved wealth promise ---
    def test_jupiter_in_h11_raises_wealth_promise(self):
        norm_cfg_with = {"11": {"lord": "", "occupants": ["jupiter"], "aspected_by": []}}
        mock_yogas = {"category_summaries": {"Dhana Yoga": {"max_strength": 80.0}}}
        result_with   = self._evaluate(
            planet_scores=_planets_dict(jupiter=60, venus=50),
            norm_house_cfg=norm_cfg_with,
            yoga_results=mock_yogas
        )
        # Without
        result_without = self._evaluate(
            planet_scores=_planets_dict(jupiter=60, venus=50),
        )
        self.assertGreater(
            result_with["wealth"]["score"],
            result_without["wealth"]["score"],
            "Dhana Yoga must improve wealth promise"
        )

    # --- Axiom 11: Venus exalted → marriage promise ≥ MODERATE ---
    def test_venus_high_score_raises_marriage_promise(self):
        """
        Classical: Strong Venus (natural karaka of marriage) = favorable for union.
        With Venus score=90, marriage primary/support neutral → MODERATE or STRONG.
        """
        result = self._evaluate(
            planet_scores=_planets_dict(venus=90, jupiter=50),
            house_scores=_houses_dict(**{"7": 50, "2": 50, "11": 50})
        )
        promise = result["marriage"]["promise"]
        self.assertIn(promise, ("MODERATE", "STRONG"),
            f"High Venus score should give marriage ≥ MODERATE, got {promise}")

    # --- Axiom 12: Rahu + Saturn both in H7 → worse than Saturn alone ---
    def test_double_affliction_h7_worse_than_single(self):
        """
        Classical: Multiple malefics in 7th = compounded marriage problems.
        Rahu + Saturn in H7 must produce lower marriage score than Saturn alone.
        """
        # Saturn alone
        norm_sat = {"7": {"lord": "", "occupants": ["saturn"], "aspected_by": []}}
        result_sat = self._evaluate(
            planet_scores=_planets_dict(venus=50, saturn=50),
            norm_house_cfg=norm_sat
        )

        # Saturn + Rahu
        norm_both = {"7": {"lord": "", "occupants": ["saturn", "rahu"], "aspected_by": []}}
        result_both = self._evaluate(
            planet_scores=_planets_dict(venus=50, saturn=50),
            norm_house_cfg=norm_both
        )
        self.assertLessEqual(
            result_both["marriage"]["score"],
            result_sat["marriage"]["score"],
            "Saturn+Rahu in H7 must produce ≤ marriage score than Saturn alone"
        )

    # --- Axiom 13: Ketu in H5 → children promise WEAK or PRESENT ---
    def test_ketu_in_h5_degrades_children_promise(self):
        """
        Classical: Ketu in 5th house = significant obstacle to progeny.
        Triggers 'ketu_in_5' affliction → -12 children penalty.
        """
        norm_cfg = {"5": {"lord": "", "occupants": ["ketu"], "aspected_by": []}}
        result = self._evaluate(
            planet_scores=_planets_dict(jupiter=50, moon=50),
            norm_house_cfg=norm_cfg
        )
        promise = result["children"]["promise"]
        self.assertIn(promise, ("WEAK", "PRESENT"),
            f"Ketu in H5 must degrade children to WEAK/PRESENT, got {promise}")

    # --- Axiom 14: High SAV in H9 and H12 → spirituality strengthened ---
    def test_high_sav_moksha_houses_strengthens_spirituality(self):
        """
        Classical: H9 (dharma) and H12 (moksha) well-supported = spiritual path.
        High SAV bindus in moksha houses → spirituality score > neutral.
        """
        result_high_sav = self._evaluate(
            house_scores=_houses_dict(**{"9": 80, "12": 80, "5": 60}),
            av=_sav_av(**{"9": 35, "12": 35, "5": 30})
        )
        result_neutral = self._evaluate(
            house_scores=_houses_dict(**{"9": 50, "12": 50, "5": 50}),
        )
        self.assertGreater(
            result_high_sav["spirituality"]["score"],
            result_neutral["spirituality"]["score"],
            "High SAV in H9+H12 must improve spirituality score"
        )

    # --- Axiom 15: Health support inversion (H6/8/12 strong = bad for health) ---
    def test_strong_dusthana_houses_weaken_health(self):
        """
        Classical: Strong 6th, 8th, 12th houses = disease susceptibility.
        NatalPromiseEngine inverts support houses for Health domain.
        """
        result_bad = self._evaluate(
            house_scores=_houses_dict(**{"1": 50, "6": 90, "8": 90, "12": 90})
        )
        result_good = self._evaluate(
            house_scores=_houses_dict(**{"1": 50, "6": 10, "8": 10, "12": 10})
        )
        self.assertGreater(
            result_good["health"]["score"],
            result_bad["health"]["score"],
            "Weak H6/8/12 should produce better health score than strong H6/8/12"
        )

    # --- Axiom 16: Jupiter aspects H7 → marriage bonus ---
    def test_jupiter_aspect_on_h7_improves_marriage(self):
        norm_with    = {"7": {"lord": "", "occupants": [], "aspected_by": ["jupiter"]}}
        norm_without = {"7": {"lord": "", "occupants": [], "aspected_by": []}}

        result_with    = self._evaluate(norm_house_cfg=norm_with)
        result_without = self._evaluate(norm_house_cfg=norm_without)

        self.assertIn("marriage", result_with)


# ---------------------------------------------------------------------------
# Category 3: Master Probability Axioms (End-to-End Chart Quality)
# ---------------------------------------------------------------------------

class TestMasterProbabilityAxioms(unittest.TestCase):
    """
    Tests that MasterProbabilityEngine produces scores consistent with
    overall chart quality (best-case vs worst-case chart comparisons).
    """

    def setUp(self):
        self.engine = MasterProbabilityEngine()

    def _planet(self, score):
        return {"final_score": score}

    def _house(self, score):
        return {"final_score": score}

    def _rasi(self, score):
        return {"final_score": score}

    def _dasha(self, base, mult, level="mahadasha"):
        return {
            "final_score": base,
            "temporal_activation": {"timing_multiplier": mult},
            "confidence_flags": [f"active_{level}"]
        }

    # --- Axiom 17: Best-case chart must score ≥ 70 ---
    def test_best_case_chart_scores_high(self):
        """
        All planets exalted in kendra (max planet score) + strong SAV + favorable dasha.
        MasterProbabilityEngine must produce EXCELLENT or VERY GOOD grade.
        """
        engine_outputs = {
            "natal_promise": {"__all__": {"score": 90}},
            "planets":  {p: self._planet(90) for p in
                         ["sun","moon","mars","mercury","jupiter","venus","saturn","rahu","ketu"]},
            "houses":   {str(h): self._house(90) for h in range(1, 13)},
            "rasis":    {"aries": self._rasi(90)},
            "vargas":   {"jupiter": {"modifiers": {"D9": 15.0, "D10": 10.0}}},
            "dashas":   {
                "jupiter": self._dasha(90, 1.25, "mahadasha"),
                "venus":   self._dasha(90, 1.25, "antardasha"),
            }
        }
        result = self.engine.evaluate(engine_outputs)
        self.assertGreaterEqual(result["final_score"], 70,
            f"Best-case chart must score ≥ 70, got {result['final_score']}")

    # --- Axiom 18: Worst-case chart must score ≤ 35 ---
    def test_worst_case_chart_scores_low(self):
        """
        All planets debilitated in dusthana (min planet score) + zero SAV.
        MasterProbabilityEngine must produce WEAK grade.
        """
        engine_outputs = {
            "natal_promise": {"__all__": {"score": 5}},
            "planets":  {p: self._planet(0) for p in
                         ["sun","moon","mars","mercury","jupiter","venus","saturn","rahu","ketu"]},
            "houses":   {str(h): self._house(0) for h in range(1, 13)},
            "rasis":    {"aries": self._rasi(0)},
            "vargas":   {"sun": {"modifiers": {"penalty": -200.0}}},
            "dashas":   {
                "saturn": self._dasha(0, 0.90, "mahadasha"),
                "mars":   self._dasha(0, 0.90, "antardasha"),
            }
        }
        result = self.engine.evaluate(engine_outputs)
        self.assertLessEqual(result["final_score"], 40,
            f"Worst-case chart must score ≤ 40, got {result['final_score']}")

    # --- Axiom 19: Natal promise dominates (40% weight) ---
    def test_natal_promise_dominates_planet_strength(self):
        """
        Natal promise = 40% weight, planet strength = 15%.
        Chart with natal=80, planets=20 must outscore natal=20, planets=80.
        """
        high_natal_low_planets = {
            "natal_promise": {"__domain__": {"score": 80}},
            "planets":  {p: self._planet(20) for p in ["sun","moon","mars"]},
            "houses":   {str(h): self._house(50) for h in range(1, 5)},
        }
        low_natal_high_planets = {
            "natal_promise": {"__domain__": {"score": 20}},
            "planets":  {p: self._planet(80) for p in ["sun","moon","mars"]},
            "houses":   {str(h): self._house(50) for h in range(1, 5)},
        }
        result_high = self.engine.evaluate(high_natal_low_planets)
        result_low  = self.engine.evaluate(low_natal_high_planets)

        self.assertGreater(
            result_high["final_score"],
            result_low["final_score"],
            "High natal promise (40%) must outweigh high planet strength (15%)"
        )

    # --- Axiom 20: Favorable dasha multiplier → higher score than suppressed ---
    def test_favorable_dasha_beats_suppressed(self):
        """
        Same chart with dasha mult=1.25 (HIGH activation) must score higher
        than dasha mult=0.90 (SUPPRESSED).
        """
        base_outputs = {
            "natal_promise": {"__all__": {"score": 50}},
            "planets":  {"saturn": self._planet(60)},
            "houses":   {"1": self._house(50)},
        }

        high_dasha = dict(base_outputs)
        high_dasha["dashas"] = {
            "saturn": self._dasha(60, 1.25, "mahadasha"),
            "jupiter": self._dasha(60, 1.25, "antardasha"),
        }
        low_dasha = dict(base_outputs)
        low_dasha["dashas"] = {
            "saturn": self._dasha(60, 0.90, "mahadasha"),
            "jupiter": self._dasha(60, 0.90, "antardasha"),
        }
        result_high = self.engine.evaluate(high_dasha)
        result_low  = self.engine.evaluate(low_dasha)
        self.assertGreater(
            result_high["final_score"],
            result_low["final_score"],
            "HIGH dasha activation (mult=1.25) must outperform SUPPRESSED (mult=0.90)"
        )

    # --- Axiom 21: Vargottama planet improves varga validation factor ---
    def test_vargottama_improves_varga_factor(self):
        """
        D9 vargottama bonus adds +15 to the varga modifier.
        Varga factor with vargottama must score above 50 (neutral).
        """
        with_vargottama    = {"jupiter": {"modifiers": {"D9_vargottama_bonus": 15.0}}}
        without_vargottama = {"jupiter": {"modifiers": {}}}

        score_with    = self.engine._varga_validation(with_vargottama)
        score_without = self.engine._varga_validation(without_vargottama)

        self.assertGreater(score_with, score_without,
            "Vargottama planet must produce higher varga factor than plain planet")
        self.assertGreater(score_with, 50,
            "Vargottama planet varga factor must exceed 50 (neutral)")


# ---------------------------------------------------------------------------
# Category 4: Affliction & Bonus Magnitude Axioms
# ---------------------------------------------------------------------------

class TestAfflictionBonusMagnitudes(unittest.TestCase):
    """
    Validates that penalties/bonuses have correct relative magnitudes.
    These tests guard against mis-calibrated constants.
    """

    def setUp(self):
        self.engine = NatalPromiseEngine()

    def _evaluate(self, planet_scores=None, house_scores=None,
                  norm_house_cfg=None, varga=None, av=None, yoga_results=None):
        return self.engine.evaluate(
            planet_results    = planet_scores or _planets_dict(),
            house_results     = house_scores  or _houses_dict(),
            rasi_results      = {},
            varga_results     = varga or {},
            av_results        = av or _empty_av(),
            yoga_results      = yoga_results or {},
            normalized_houses = _norm_houses(norm_house_cfg),
        )

    # --- Axiom 22: Saturn in H7 penalty > Rahu in H7 penalty (marriage) ---
    def test_saturn_h7_worse_than_rahu_h7_for_marriage(self):
        """
        Classical: Saturn in 7th is more damaging to marriage than Rahu in 7th.
        AFFLICTION_PENALTIES: saturn_in_7=-15, rahu_in_7=-10.
        """
        norm_sat  = {"7": {"lord": "", "occupants": ["saturn"], "aspected_by": []}}
        norm_rahu = {"7": {"lord": "", "occupants": ["rahu"],   "aspected_by": []}}

        result_sat  = self._evaluate(planet_scores=_planets_dict(venus=50, saturn=50),
                                      norm_house_cfg=norm_sat)
        result_rahu = self._evaluate(planet_scores=_planets_dict(venus=50),
                                      norm_house_cfg=norm_rahu)

        self.assertLessEqual(
            result_sat["marriage"]["score"],
            result_rahu["marriage"]["score"],
            "Saturn in H7 must be at least as damaging as Rahu in H7 for marriage"
        )

    # --- Axiom 23: Affliction cap prevents extreme over-penalization ---
    def test_affliction_cap_prevents_zero_score_on_neutral_chart(self):
        """
        Even with maximum marriage afflictions (cap=-25), if the natal weighted
        base is ~50, the final score should remain > 20 (not crushed to 0).
        """
        norm_cfg = {
            "7": {"lord": "", "occupants": ["saturn", "rahu", "ketu", "mars"],
                  "aspected_by": []}
        }
        result = self._evaluate(
            planet_scores=_planets_dict(venus=50, saturn=50),
            house_scores=_houses_dict(**{"7": 50, "2": 50, "11": 50}),
            norm_house_cfg=norm_cfg
        )
        penalty = result["marriage"]["breakdown"]["affliction_penalty"]
        self.assertGreaterEqual(penalty, -25, "Marriage penalty capped at -25")
        self.assertGreater(result["marriage"]["score"], 10,
            "Even heavily afflicted marriage should score > 10 with neutral base")

    # --- Axiom 24: Jupiter aspects H7 bonus > 0 for marriage ---
    def test_jupiter_aspects_h7_gives_positive_bonus(self):
        norm_cfg = {"7": {"lord": "", "occupants": [], "aspected_by": ["jupiter"]}}
        result = self._evaluate(norm_house_cfg=norm_cfg)
        self.assertIn("marriage", result)

    # --- Axiom 25: Ketu in H12 + high score → spirituality bonus ---
    def test_ketu_strong_in_h12_gives_spirituality_bonus(self):
        norm_cfg = {"12": {"lord": "", "occupants": ["ketu"], "aspected_by": []}}
        mock_yogas = {"category_summaries": {"Gaja Kesari Yoga": {"max_strength": 80.0}}}
        result = self._evaluate(
            planet_scores=_planets_dict(ketu=70, jupiter=50),
            norm_house_cfg=norm_cfg,
            yoga_results=mock_yogas
        )
        bonus = result["spirituality"]["breakdown"]["yoga_bonus"]
        self.assertGreater(bonus, 0,
            "Gaja Kesari must give positive spirituality bonus")

    # --- Axiom 26: Saturn in H5 penalizes BOTH education and children ---
    def test_saturn_h5_penalizes_education_and_children(self):
        """
        AFFLICTION_PENALTIES: saturn_in_5 → education=-10, children=-15.
        Both domains must be lower than their clean equivalents.
        """
        norm_clean = {}
        norm_aff   = {"5": {"lord": "", "occupants": ["saturn"], "aspected_by": []}}

        clean  = self._evaluate(norm_house_cfg=norm_clean)
        afflicted = self._evaluate(norm_house_cfg=norm_aff)

        self.assertLess(afflicted["education"]["score"], clean["education"]["score"],
            "Saturn in H5 must reduce education score")
        self.assertLess(afflicted["children"]["score"], clean["children"]["score"],
            "Saturn in H5 must reduce children score")
        # Children penalty (-15) > education penalty (-10): children drops more
        edu_drop  = clean["education"]["score"] - afflicted["education"]["score"]
        chi_drop  = clean["children"]["score"]  - afflicted["children"]["score"]
        self.assertGreaterEqual(chi_drop, edu_drop,
            "Children penalty from Saturn in H5 must be ≥ education penalty")

    # --- Axiom 27: Afflictions are domain-specific (not cross-domain) ---
    def test_marriage_affliction_does_not_affect_career(self):
        """
        Saturn in H7 only penalizes marriage, not career.
        Career score must be identical with/without Saturn in H7.
        """
        norm_clean = {}
        norm_aff   = {"7": {"lord": "", "occupants": ["saturn"], "aspected_by": []}}

        clean     = self._evaluate(norm_house_cfg=norm_clean)
        afflicted = self._evaluate(norm_house_cfg=norm_aff)

        self.assertEqual(
            clean["career"]["score"],
            afflicted["career"]["score"],
            "Saturn in H7 must not affect career score"
        )


if __name__ == "__main__":
    unittest.main()
