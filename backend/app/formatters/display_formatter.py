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
        
        from datetime import datetime
        def format_date(date_str: str) -> str:
            if not date_str or date_str == "Unknown":
                return "Unknown"
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime("%d-%b-%Y")
            except ValueError:
                return date_str

        dasha_display = DashaActivationDisplay(
            mahadasha=f"{md_lord} ({round(md_str)}%)",
            mahadasha_start=format_date(synthesis.get("md_start")),
            mahadasha_end=format_date(synthesis.get("md_end")),
            antardasha=f"{ad_lord} ({round(ad_str)}%)",
            antardasha_start=format_date(synthesis.get("ad_start")),
            antardasha_end=format_date(synthesis.get("ad_end")),
            pratyantardasha=f"{pd_lord} ({round(pd_str)}%)",
            pratyantardasha_start=format_date(synthesis.get("pd_start")),
            pratyantardasha_end=format_date(synthesis.get("pd_end")),
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
        def format_signal_name(signal: str) -> str:
            return " ".join(word.capitalize() for word in signal.split('_'))

        supporting_factors = []
        attention_factors = []
        
        for signal_key, signal_data in isolated_signals.items():
            name = format_signal_name(signal_key)
            score = signal_data.get("final_score", 0)
            
            if score >= 50:
                supporting_factors.append(f"{name} provides strong support ({round(score)}/100).")
            else:
                attention_factors.append(f"{name} lacks strength ({round(score)}/100).")
        
        return StructuredQuestionResult(
            question_title=question_title,
            promise_assessment=promise_assessment,
            dasha_activation=dasha_display,
            final_conclusion=final_conclusion,
            timing_window=timing_window,
            supporting_factors=supporting_factors,
            attention_factors=attention_factors,
            isolated_signals=isolated_signals,
            mandali_commentary="Reserved for Phase 15. Do not implement yet."
        )
