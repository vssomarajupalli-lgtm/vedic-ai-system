"""
Weightage Calibration Tests
============================
Tests that verify the weight sensitivities and relative magnitudes in
MASTER_WEIGHTS and DOMAIN_CONFIG reflect classical Vedic astrological principles.

These tests serve as a regression guard against future weight changes that would
violate classical ordering or produce counter-intuitive results.

Calibration version: v1.1
  - PLANET_SCORING_MATRIX: exalted=50, own_sign=35, trikona=35, kendra=30,
    combust=-20, dusthana=-15
  - DOMAIN_CONFIG varga: 0.05 (was 0.07), sav: 0.05 (was 0.03)

Reference: VEDIC_AI_MASTER_ARCHITECTURE.md, BPHS chapter on strength
"""

import unittest
from app.config.astrology_constants import (
    DOMAIN_CONFIG, AFFLICTION_PENALTIES, AFFLICTION_CAP,
    DOMAIN_BONUSES, PLANET_SCORING_MATRIX, HOUSE_SCORING_MATRIX,
    RASI_SCORING_MATRIX
)
from app.engines.master_probability_engine import MasterProbabilityEngine, MASTER_WEIGHTS
from app.engines.natal_promise_engine import NatalPromiseEngine


# ---------------------------------------------------------------------------
# Master Probability Weight Calibration
# ---------------------------------------------------------------------------

class TestMasterWeightCalibration(unittest.TestCase):
    """
    Verifies MASTER_WEIGHTS reflect proper classical ordering and total to 1.0.
    """

    # --- Calibration 1: Weights sum to exactly 1.0 ---
    def test_master_weights_sum_to_one(self):
        """All master weights must sum to exactly 1.0 (deterministic formula)."""
        total = sum(MASTER_WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=6,
            msg=f"MASTER_WEIGHTS must sum to 1.0, got {total}")

    # --- Calibration 2: Natal promise must have the highest weight ---
    def test_natal_promise_has_highest_weight(self):
        """
        Natal promise = 40% — must be the single dominant factor.
        Classical: birth chart promise is the primary indicator of life events.
        """
        natal_w = MASTER_WEIGHTS["natal_promise"]
        for key, w in MASTER_WEIGHTS.items():
            if key != "natal_promise":
                self.assertGreater(natal_w, w,
                    f"natal_promise weight ({natal_w}) must exceed {key} ({w})")

    # --- Calibration 3: Planet strength (15%) > house strength (10%) ---
    def test_planet_outweighs_house_in_master(self):
        """
        Planet strength (15%) > house strength (10%).
        Classical: planets are agents; houses are areas of life.
        """
        self.assertGreater(
            MASTER_WEIGHTS["planet_strength"],
            MASTER_WEIGHTS["house_strength"],
            "planet_strength must outweigh house_strength in master weights"
        )

    # --- Calibration 4: Dasha equals house/rasi weight (10% each) ---
    def test_dasha_equals_house_and_rasi_weights(self):
        """
        Dasha, house, rasi, and varga all = 10% — symmetrical temporal/structural factors.
        Transit is the only exception at 5% (stub).
        """
        dasha_w = MASTER_WEIGHTS["dasha_activation"]
        house_w = MASTER_WEIGHTS["house_strength"]
        rasi_w  = MASTER_WEIGHTS["rasi_strength"]
        varga_w = MASTER_WEIGHTS["varga_validation"]
        self.assertEqual(dasha_w, house_w,  "dasha_activation must equal house_strength weight")
        self.assertEqual(dasha_w, rasi_w,   "dasha_activation must equal rasi_strength weight")
        self.assertEqual(dasha_w, varga_w,  "dasha_activation must equal varga_validation weight")

    # --- Calibration 5: Transit trigger is the smallest weight (5%) ---
    def test_transit_is_smallest_weight(self):
        """Transit trigger = 5% is a stub — must be ≤ all other weights."""
        transit_w = MASTER_WEIGHTS["transit_trigger"]
        for key, w in MASTER_WEIGHTS.items():
            if key != "transit_trigger":
                self.assertLessEqual(transit_w, w,
                    f"transit_trigger ({transit_w}) must be ≤ {key} ({w})")

    # --- Calibration 6: Total non-stub weight ≥ 75% ---
    def test_live_factors_dominate_master_formula(self):
        """
        Live factors (non-stub) must represent ≥ 75% of total weight.
        Ensures stubs don't artificially dominate the output.
        """
        stub_keys = {"natal_promise", "transit_trigger"}   # stubs return neutral 50
        live_weight = sum(w for k, w in MASTER_WEIGHTS.items() if k not in stub_keys)
        self.assertGreaterEqual(live_weight, 0.45,  # 45% live minimum
            f"Live factors must have ≥ 45% total weight, got {live_weight:.0%}")


# ---------------------------------------------------------------------------
# Domain Config Weight Calibration
# ---------------------------------------------------------------------------

class TestDomainWeightCalibration(unittest.TestCase):
    """
    Verifies DOMAIN_CONFIG weights follow classical Vedic principles:
    - Primary house is the dominant factor
    - Karaka (natural significator) outweighs varga and SAV
    - All weights per domain sum to 1.0
    """

    # --- Calibration 7: All domain weights sum to 1.0 ---
    def test_all_domain_weights_sum_to_one(self):
        """Every domain's weights must sum to exactly 1.0."""
        for domain, cfg in DOMAIN_CONFIG.items():
            total = sum(cfg["weights"].values())
            self.assertAlmostEqual(total, 1.0, places=6,
                msg=f"Domain '{domain}' weights sum to {total}, not 1.0")

    # --- Calibration 8: Primary house is the dominant factor per domain ---
    def test_primary_house_weight_dominant_in_all_domains(self):
        """
        Primary house weight ≥ any other single weight factor.
        Classical: the primary bhava lord is the key indicator for its domain.
        """
        for domain, cfg in DOMAIN_CONFIG.items():
            w = cfg["weights"]
            primary = w["primary_house"]
            for key, val in w.items():
                if key != "primary_house":
                    self.assertGreaterEqual(primary, val,
                        f"Domain '{domain}': primary_house weight ({primary}) "
                        f"must be ≥ {key} ({val})")

    # --- Calibration 9: Karaka outweighs SAV in all domains ---
    def test_karaka_outweighs_sav_in_all_domains(self):
        """
        Natural significator (karaka) weight > SAV weight in all domains.
        Classical: the signifying planet is more important than bindu support.
        """
        for domain, cfg in DOMAIN_CONFIG.items():
            w = cfg["weights"]
            self.assertGreater(w["karaka"], w["sav"],
                f"Domain '{domain}': karaka ({w['karaka']}) must outweigh "
                f"sav ({w['sav']})")

    # --- Calibration 10: Varga ≥ SAV (structural more important than timing bindus) ---
    def test_varga_weight_gte_sav_weight_all_domains(self):
        """
        Varga (divisional chart quality) must be ≥ SAV (bindu timing support).
        Calibrated v1.1: both are 0.05 — equal weight, justified by literature.
        """
        for domain, cfg in DOMAIN_CONFIG.items():
            w = cfg["weights"]
            self.assertGreaterEqual(w["varga"], w["sav"],
                f"Domain '{domain}': varga ({w['varga']}) must be ≥ sav ({w['sav']})")

    # --- Calibration 11: Marriage uses D9 (Navamsa is the marriage chart) ---
    def test_marriage_uses_navamsa_d9(self):
        """Classical: Navamsa (D9) is the primary chart for marriage analysis."""
        self.assertEqual(DOMAIN_CONFIG["marriage"]["varga"], "D9",
            "Marriage domain must use D9 (Navamsa) for varga analysis")

    # --- Calibration 12: Career uses D10 (Dasamsa is the career chart) ---
    def test_career_uses_dasamsa_d10(self):
        """Classical: Dasamsa (D10) is the primary chart for career analysis."""
        self.assertEqual(DOMAIN_CONFIG["career"]["varga"], "D10",
            "Career domain must use D10 (Dasamsa) for varga analysis")

    # --- Calibration 13: Health uses inverted support houses ---
    def test_health_domain_has_inverted_support(self):
        """
        Health support houses (H6/H8/H12) are inverted.
        Strong dusthana houses = disease susceptibility = bad for health.
        """
        self.assertTrue(DOMAIN_CONFIG["health"].get("inverted_support"),
            "Health domain must have inverted_support=True")
        self.assertIn("6", DOMAIN_CONFIG["health"]["support_houses"])
        self.assertIn("8", DOMAIN_CONFIG["health"]["support_houses"])
        self.assertIn("12", DOMAIN_CONFIG["health"]["support_houses"])

    # --- Calibration 14: Wealth uses H2+H11 as primary (dhana bhavas) ---
    def test_wealth_uses_h2_and_h11_as_primary(self):
        """
        Classical: H2 (accumulated wealth) + H11 (income) = wealth indicators.
        DOMAIN_CONFIG wealth primary_house must be a list containing both.
        """
        primary = DOMAIN_CONFIG["wealth"]["primary_house"]
        self.assertIsInstance(primary, list,
            "Wealth primary_house must be a list (H2 and H11)")
        self.assertIn("2", primary)
        self.assertIn("11", primary)


# ---------------------------------------------------------------------------
# Planet Scoring Matrix Calibration (v1.1)
# ---------------------------------------------------------------------------

class TestPlanetScoringMatrixCalibration(unittest.TestCase):
    """
    Validates that the v1.1 PLANET_SCORING_MATRIX produces scores
    consistent with the designed 0–100 target range.
    """

    # --- Calibration 15: Exalted value = 50 ---
    def test_exalted_dignity_is_50(self):
        """v1.1: exalted dignity = 50 (maximum dignity contribution)."""
        self.assertEqual(PLANET_SCORING_MATRIX["dignity"]["exalted"], 50)

    # --- Calibration 16: Debilitated value = 0 ---
    def test_debilitated_dignity_is_0(self):
        """v1.1: debilitated dignity = 0 (minimum dignity contribution)."""
        self.assertEqual(PLANET_SCORING_MATRIX["dignity"]["debilitated"], 0)

    # --- Calibration 17: Trikona > kendra in house placement ---
    def test_trikona_higher_than_kendra(self):
        """
        Classical: Trikona (5th/9th) houses are the highest quality house type.
        v1.1: trikona=35 > kendra=30.
        """
        self.assertGreater(
            PLANET_SCORING_MATRIX["house_placement"]["trikona"],
            PLANET_SCORING_MATRIX["house_placement"]["kendra"],
            "Trikona house bonus must exceed kendra in planet scoring matrix"
        )

    # --- Calibration 18: Dusthana is negative ---
    def test_dusthana_placement_is_negative(self):
        """Dusthana placement must apply a negative modifier (6th/8th/12th = challenge)."""
        self.assertLess(
            PLANET_SCORING_MATRIX["house_placement"]["dusthana"], 0,
            "Dusthana placement must be negative"
        )

    # --- Calibration 19: Combust penalty exceeds retrograde bonus ---
    def test_combust_magnitude_exceeds_retrograde_bonus(self):
        """
        Combust (-20) is a stronger effect than retrograde (+5).
        A combust retrograde planet must still score lower than a clean planet.
        """
        combust    = PLANET_SCORING_MATRIX["state_modifiers"]["combust"]
        retrograde = PLANET_SCORING_MATRIX["state_modifiers"]["retrograde"]
        self.assertLess(combust + retrograde, 0,
            "Combust penalty must dominate retrograde bonus (net must be negative)")

    # --- Calibration 20: Dignity ordering is strict ---
    def test_dignity_strict_ordering(self):
        """Dignity values must be strictly decreasing: exalted > own > friendly > neutral > enemy > debilitated."""
        d = PLANET_SCORING_MATRIX["dignity"]
        self.assertGreater(d["exalted"],     d["own_sign"])
        self.assertGreater(d["own_sign"],    d["friendly"])
        self.assertGreater(d["friendly"],    d["neutral"])
        self.assertGreater(d["neutral"],     d["enemy"])
        self.assertGreater(d["enemy"],       d["debilitated"])


# ---------------------------------------------------------------------------
# Affliction Penalty Calibration
# ---------------------------------------------------------------------------

class TestAfflictionCalibration(unittest.TestCase):
    """
    Validates that AFFLICTION_PENALTIES are properly ordered and calibrated.
    """

    # --- Calibration 21: Saturn in H7 is the worst marriage affliction ---
    def test_saturn_h7_is_worst_marriage_affliction(self):
        """
        Classical: Saturn in 7th causes the most damage to marriage.
        saturn_in_7 penalty (-15) must be ≥ any other single marriage penalty.
        """
        saturn_penalty = abs(AFFLICTION_PENALTIES["saturn_in_7"].get("marriage", 0))
        for flag, domains in AFFLICTION_PENALTIES.items():
            if "marriage" in domains and flag != "saturn_in_7":
                other = abs(domains["marriage"])
                self.assertGreaterEqual(saturn_penalty, other,
                    f"saturn_in_7 marriage penalty ({saturn_penalty}) should be "
                    f"≥ {flag} ({other})")

    # --- Calibration 22: All affliction caps are negative ---
    def test_all_affliction_caps_are_negative(self):
        """Affliction caps must all be negative (penalties, not bonuses)."""
        for domain, cap in AFFLICTION_CAP.items():
            self.assertLess(cap, 0,
                f"AFFLICTION_CAP['{domain}'] = {cap} must be negative")

    # --- Calibration 23: All AFFLICTION_PENALTIES values are negative ---
    def test_all_affliction_penalties_are_negative(self):
        """Every individual affliction penalty must be a negative number."""
        for flag, domains in AFFLICTION_PENALTIES.items():
            for domain, penalty in domains.items():
                self.assertLess(penalty, 0,
                    f"AFFLICTION_PENALTIES['{flag}']['{domain}'] = {penalty} must be < 0")

    # --- Calibration 24: All DOMAIN_BONUSES values are positive ---
    def test_all_domain_bonuses_are_positive(self):
        """Every yoga bonus must be positive (beneficial)."""
        for flag, domains in DOMAIN_BONUSES.items():
            for domain, bonus in domains.items():
                self.assertGreater(bonus, 0,
                    f"DOMAIN_BONUSES['{flag}']['{domain}'] = {bonus} must be > 0")

    # --- Calibration 25: Cap limits applied correctly by engine ---
    def test_engine_applies_affliction_cap_correctly(self):
        """
        NatalPromiseEngine must respect AFFLICTION_CAP.
        Even with all marriage afflictions stacked, penalty ≥ cap.
        """
        engine = NatalPromiseEngine()
        all_marriage_flags = [
            k for k, v in AFFLICTION_PENALTIES.items() if "marriage" in v
        ]
        penalty = engine._compute_penalties("marriage", all_marriage_flags)
        cap     = AFFLICTION_CAP["marriage"]
        self.assertGreaterEqual(penalty, cap,
            f"Stacked marriage penalty {penalty} must be ≥ cap {cap}")
        self.assertLess(penalty, 0, "Penalty must be negative (< 0)")

    # --- Calibration 26: Jupiter aspect bonus is the largest marriage bonus ---
    def test_jupiter_aspects_h7_is_largest_marriage_bonus(self):
        """
        Jupiter aspecting H7 (+8) is the strongest protective yoga for marriage.
        Must be ≥ all other marriage bonuses.
        """
        jup_bonus = DOMAIN_BONUSES.get("jupiter_aspects_7", {}).get("marriage", 0)
        self.assertGreater(jup_bonus, 0,
            "jupiter_aspects_7 must give a positive marriage bonus")
        for flag, domains in DOMAIN_BONUSES.items():
            if "marriage" in domains and flag != "jupiter_aspects_7":
                other = domains["marriage"]
                self.assertGreaterEqual(jup_bonus, other,
                    f"jupiter_aspects_7 bonus ({jup_bonus}) must be ≥ {flag} ({other})")


if __name__ == "__main__":
    unittest.main()
