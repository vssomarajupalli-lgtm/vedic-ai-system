from typing import Dict, Any, List
from app.schemas.question import (
    StructuredQuestionResult,
    PromiseAssessmentDisplay,
    DashaActivationDisplay,
    FinalConclusionDisplay,
    TimingWindowDisplay
)

class DisplayFormatter:
    """
    Transforms internal mathematical outputs and Boolean gate results into 
    the highly structured Questionnaire Display format (Phase 14H.1).
    Does NOT modify calculation engine rules.
    """
    
    @staticmethod
    def _map_display_grade(internal_grade: str) -> str:
        mapping = {
            "PRESENT": "Very Weak",
            "WEAK": "Weak",
            "MODERATE": "Good",
            "STRONG": "Excellent"
        }
        return mapping.get(internal_grade.upper(), internal_grade)

    @staticmethod
    def format_question_result(
        question_title: str,
        domain: str,
        natal_promise: Dict[str, Any],
        dasha_activation: Dict[str, Any],
        final_state: str,
        isolated_signals: Dict[str, Any]
    ) -> StructuredQuestionResult:
        
        # 1. Promise Assessment
        domain_promise = natal_promise.get(domain, {})
        p_score = domain_promise.get("score", 50)
        p_grade_internal = domain_promise.get("promise", "MODERATE")
        p_grade_display = DisplayFormatter._map_display_grade(p_grade_internal)
        
        promise_assessment = PromiseAssessmentDisplay(
            promise_score=f"{p_score}%",
            promise_grade=p_grade_display,
            interpretation=f"{domain.capitalize()} promise is {p_grade_display.lower()}."
        )
        
        # 2. Dasha Activation
        synthesis = dasha_activation.get("synthesis", {})
        md_lord = synthesis.get("active_md", "unknown").capitalize()
        ad_lord = synthesis.get("active_ad", "unknown").capitalize()
        pd_lord = synthesis.get("active_pd", "unknown").capitalize()
        
        md_str = synthesis.get("md_strength", 50.0)
        ad_str = synthesis.get("ad_strength", 50.0)
        pd_str = synthesis.get("pd_strength", 50.0)
        
        activation_index = round((md_str + ad_str + pd_str) / 3.0)
        
        # Determine internal activation grade based on index
        if activation_index >= 70:
            act_grade_internal = "STRONG"
        elif activation_index >= 50:
            act_grade_internal = "MODERATE"
        elif activation_index >= 30:
            act_grade_internal = "WEAK"
        else:
            act_grade_internal = "PRESENT"
            
        act_grade_display = DisplayFormatter._map_display_grade(act_grade_internal)
        
        dasha_display = DashaActivationDisplay(
            mahadasha=f"{md_lord} ({round(md_str)}%)",
            antardasha=f"{ad_lord} ({round(ad_str)}%)",
            pratyantardasha=f"{pd_lord} ({round(pd_str)}%)",
            activation_index=f"{activation_index}%",
            activation_grade=act_grade_display
        )
        
        # 3. Final Conclusion
        final_conclusion = FinalConclusionDisplay(
            promise_status=p_grade_display.upper(),
            dasha_support=act_grade_display.upper(),
            assessment=final_state
        )
        
        # 4. Timing Window
        timing_window = TimingWindowDisplay(
            mahadasha=md_lord,
            antardasha=ad_lord,
            pratyantardasha=pd_lord,
            most_supportive_period="Current Dasha Window"
        )
        
        # 5. Supporting / Attention Factors
        # In a real implementation we would scan isolated_signals for favorable/unfavorable indicators.
        supporting_factors = ["Primary lord is strong."] if p_score >= 50 else []
        attention_factors = ["Primary house lacks support."] if p_score < 50 else []
        
        return StructuredQuestionResult(
            question_title=question_title,
            promise_assessment=promise_assessment,
            dasha_activation=dasha_display,
            final_conclusion=final_conclusion,
            timing_window=timing_window,
            supporting_factors=supporting_factors,
            attention_factors=attention_factors,
            mandali_commentary="Reserved for Phase 15. Do not implement yet."
        )
