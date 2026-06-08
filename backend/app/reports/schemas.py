from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime, timezone

class ReportSectionData(BaseModel):
    """
    Standardized block for any section of the generated report.
    """
    title: str
    summary_text: str = ""
    data_points: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

class FinalReportSchema(BaseModel):
    """
    The complete generated report serving as the source of truth for 
    JSON exports, HTML rendering, and PDF generation.
    """
    report_version: str = "1.0.0"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Core identifying information
    client_info: Dict[str, str] = Field(default_factory=dict)
    
    # Executive overview
    executive_summary: ReportSectionData
    master_probability: ReportSectionData
    natal_promise_analysis: ReportSectionData
    
    # Granular analysis blocks
    planet_analysis: ReportSectionData
    house_analysis: ReportSectionData
    yoga_analysis: ReportSectionData
    dasha_analysis: ReportSectionData
    transit_analysis: ReportSectionData
    ashtakavarga_analysis: ReportSectionData
    
    # Historical narrative interactions
    question_responses: List[Dict[str, str]] = Field(default_factory=list)
