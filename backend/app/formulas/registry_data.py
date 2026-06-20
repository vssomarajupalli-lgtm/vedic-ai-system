from app.formulas.schema import FormulaSchema

# Seed formulas implemented strictly as data structs (no logic)
# Based on PHASE 12B FORMULA_REPOSITORY_DATA_MODEL_v1.md

SEED_FORMULAS = [
    # ---------------------------------------------------------
    # MARRIAGE FAMILY
    # ---------------------------------------------------------
    FormulaSchema(
        formula_key="MAR_TIMING_BASE",
        formula_name="Marriage Timing Base",
        formula_category="Timing Assessment",
        required_engines=["NatalPromiseEngine", "DashaEngine", "TransitEngine"],
        required_signals=["7th_house", "7th_lord", "venus", "lagna_lord"],
        required_dasha_layers=["mahadasha", "antardasha"],
        required_confidence_layers=["dasha_lord_aspect_7th", "dasha_lord_is_venus", "jupiter_transit_7th_lagna"],
        future_gochara_required=True,
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="MAR_TIMING_NORMAL",
        formula_name="Standard Marriage Timing",
        formula_category="Timing Assessment",
        parent_formula_key="MAR_TIMING_BASE",
        required_confidence_layers=["absence_of_saturn_delay"],
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="MAR_TIMING_DELAY",
        formula_name="Delayed Marriage Timing",
        formula_category="Timing Assessment",
        parent_formula_key="MAR_TIMING_BASE",
        required_signals=["saturn"],
        required_confidence_layers=["saturn_aspect_7th"],
        answer_template_key="timing_assessment_v1"
    ),

    # ---------------------------------------------------------
    # CAREER FAMILY
    # ---------------------------------------------------------
    FormulaSchema(
        formula_key="CAR_GROWTH_BASE",
        formula_name="Career Growth Base",
        formula_category="Timing Assessment",
        required_engines=["NatalPromiseEngine", "AshtakavargaEngine", "DashaEngine"],
        required_signals=["10th_house", "10th_lord", "11th_house"],
        required_vargas=["D1", "D10"],
        required_confidence_layers=["10th_lord_d10_strength", "positive_dasha"],
        future_gochara_required=True,
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="CAR_PROMOTION_TIMING",
        formula_name="Promotion Timing",
        formula_category="Timing Assessment",
        parent_formula_key="CAR_GROWTH_BASE",
        required_confidence_layers=["10th_house_bindus_gt_28"],
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="CAR_CHANGE_TIMING",
        formula_name="Job Change Timing",
        formula_category="Timing Assessment",
        parent_formula_key="CAR_GROWTH_BASE",
        required_engines=["TransitEngine"],
        required_signals=["5th_house", "9th_house"],
        required_confidence_layers=["dasha_lords_connect_5th_9th", "transit_saturn_jupiter_activate_10th"],
        answer_template_key="timing_assessment_v1"
    ),

    # ---------------------------------------------------------
    # WEALTH FAMILY
    # ---------------------------------------------------------
    FormulaSchema(
        formula_key="WEA_SUDDEN_BASE",
        formula_name="Sudden Wealth Base",
        formula_category="Multi-factor Assessment",
        required_engines=["NatalPromiseEngine", "DashaEngine"],
        required_signals=["8th_house", "11th_house", "rahu", "2nd_house"],
        required_vargas=["D1"],
        required_confidence_layers=["8th_lord_connect_11th", "dasha_activates_yoga"],
        future_gochara_required=False,
        answer_template_key="multifactor_assessment_v1"
    ),
    FormulaSchema(
        formula_key="WEA_SUDDEN_GAIN",
        formula_name="Sudden Financial Gains",
        formula_category="Multi-factor Assessment",
        parent_formula_key="WEA_SUDDEN_BASE",
        required_confidence_layers=["rahu_in_8th_11th", "absence_malefic_aspect_2nd"],
        answer_template_key="multifactor_assessment_v1"
    ),
    FormulaSchema(
        formula_key="WEA_SUDDEN_LOSS",
        formula_name="Sudden Financial Loss",
        formula_category="Multi-factor Assessment",
        parent_formula_key="WEA_SUDDEN_BASE",
        required_signals=["12th_house"],
        required_confidence_layers=["rahu_afflicts_2nd_lord", "12th_lord_active"],
        answer_template_key="multifactor_assessment_v1"
    )
]

def get_seed_registry():
    return SEED_FORMULAS
