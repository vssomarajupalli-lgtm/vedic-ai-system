from app.formulas.schema import FormulaSchema

# Seed formulas implemented strictly as data structs (no logic)
# Based on PHASE 12B FORMULA_REPOSITORY_DATA_MODEL_v1.md

SEED_FORMULAS = [
    FormulaSchema(
        formula_key="MAR_PROS_001",
        formula_name="Marriage Prospects",
        formula_category="Natal Assessment",
        required_engines=["NatalPromiseEngine"],
        required_signals=["7th_house", "7th_lord", "venus"],
        required_vargas=["D1", "D9"],
        required_confidence_layers=["7th_lord_dignity", "venus_dignity", "d9_lagnesh_strength"],
        future_gochara_required=False,
        answer_template_key="natal_assessment_v1"
    ),
    FormulaSchema(
        formula_key="MAR_TIMING_001",
        formula_name="Marriage Timing",
        formula_category="Timing Assessment",
        required_engines=["NatalPromiseEngine", "DashaEngine", "TransitEngine"],
        required_signals=["7th_house", "7th_lord", "venus", "lagna_lord"],
        required_dasha_layers=["mahadasha", "antardasha"],
        required_confidence_layers=["dasha_lord_aspect_7th", "dasha_lord_is_venus", "jupiter_transit_7th_lagna"],
        future_gochara_required=True,
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="MAR_DELAY_001",
        formula_name="Delay in Marriage",
        formula_category="Risk Assessment",
        required_engines=["NatalPromiseEngine"],
        required_signals=["saturn", "7th_house", "8th_house"],
        required_vargas=["D1"],
        required_confidence_layers=["saturn_aspect_7th", "7th_lord_in_8th_or_12th", "venus_papakartari"],
        future_gochara_required=False,
        answer_template_key="risk_assessment_v1"
    ),
    FormulaSchema(
        formula_key="CAR_GROWTH_001",
        formula_name="Career Growth",
        formula_category="Timing/Natal Assessment",
        required_engines=["NatalPromiseEngine", "AshtakavargaEngine", "DashaEngine"],
        required_signals=["10th_house", "10th_lord", "11th_house"],
        required_vargas=["D1", "D10"],
        required_confidence_layers=["10th_lord_d10_strength", "10th_house_bindus_gt_28", "positive_dasha"],
        future_gochara_required=True,
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="CAR_CHANGE_001",
        formula_name="Job Change",
        formula_category="Timing Assessment",
        required_engines=["DashaEngine", "TransitEngine"],
        required_signals=["5th_house", "9th_house", "10th_house"],
        required_dasha_layers=["antardasha", "pratyantardasha"],
        required_confidence_layers=["dasha_lords_connect_5th_9th", "transit_saturn_jupiter_activate_10th"],
        future_gochara_required=True,
        answer_template_key="timing_assessment_v1"
    ),
    FormulaSchema(
        formula_key="CAR_FOREIGN_001",
        formula_name="Foreign Career",
        formula_category="Multi-factor Assessment",
        required_engines=["NatalPromiseEngine", "DashaEngine"],
        required_signals=["9th_house", "12th_house", "10th_house", "rahu"],
        required_vargas=["D1", "D10"],
        required_confidence_layers=["10th_lord_connect_12th", "rahu_influence_10th", "dasha_activates_9th_12th"],
        future_gochara_required=False,
        answer_template_key="multifactor_assessment_v1"
    ),
    FormulaSchema(
        formula_key="WEA_SAVING_001",
        formula_name="Savings Potential",
        formula_category="Strength Assessment",
        required_engines=["NatalPromiseEngine"],
        required_signals=["2nd_house", "2nd_lord", "jupiter"],
        required_vargas=["D1"],
        required_confidence_layers=["2nd_lord_dignity", "jupiter_strength", "absence_malefic_aspect_2nd"],
        future_gochara_required=False,
        answer_template_key="strength_assessment_v1"
    ),
    FormulaSchema(
        formula_key="WEA_SUDDEN_001",
        formula_name="Sudden Financial Gains",
        formula_category="Multi-factor Assessment",
        required_engines=["NatalPromiseEngine", "DashaEngine"],
        required_signals=["8th_house", "11th_house", "rahu", "2nd_house"],
        required_vargas=["D1"],
        required_confidence_layers=["8th_lord_connect_11th", "rahu_in_8th_11th", "dasha_activates_yoga"],
        future_gochara_required=False,
        answer_template_key="multifactor_assessment_v1"
    )
]

def get_seed_registry():
    return SEED_FORMULAS
