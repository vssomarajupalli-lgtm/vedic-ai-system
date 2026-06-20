from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class FormulaSchema(BaseModel):
    formula_key: str = Field(..., description="Unique string identifier (e.g., MAR_TIMING_001)")
    formula_name: str = Field(..., description="Human-readable name")
    formula_category: str = Field(..., description="High-level classification (e.g., Timing Assessment)")
    
    required_engines: List[str] = Field(..., description="Engines that MUST execute for this formula")
    required_signals: List[str] = Field(..., description="Specific astrological variables to be plucked from the engines")
    required_dasha_layers: List[str] = Field(default_factory=list, description="Depth of time-tracking required (e.g., Mahadasha)")
    required_vargas: List[str] = Field(default_factory=list, description="Divisional charts required for synthesis")
    required_confidence_layers: List[str] = Field(..., description="Checklist of astrological conditions to evaluate")
    
    future_gochara_required: bool = Field(default=False, description="Flag for Moon-centered Mandali (transit forecasting)")
    answer_template_key: str = Field(..., description="Pointer to the linguistic boundary for the Answer Composer")

class FormulaRegistry(BaseModel):
    formulas: List[FormulaSchema]

class FormulaEvaluationResult(BaseModel):
    final_state: str = Field(..., description="FAVORABLE, MIXED, or UNFAVORABLE")
    isolated_signals: Dict[str, Any] = Field(..., description="Minimized payload of only the requested signals")
    answer_template_key: str = Field(..., description="Template to use in the Answer Composer")
    system_warnings: List[str] = Field(default_factory=list, description="Warnings like engine degradation")
