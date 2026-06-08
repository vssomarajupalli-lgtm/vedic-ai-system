from typing import Dict, Any, List
from datetime import datetime, timezone

from app.reports.schemas import FinalReportSchema
from app.reports.sections.extractors import (
    MasterProbabilitySection,
    YogaAnalysisSection,
    NatalPromiseSection,
    ExecutiveSummarySection,
    GenericSection
)

class ReportBuilder:
    """
    Orchestrates the conversion of raw PipelineRunner output into 
    the human-readable FinalReportSchema using isolated extractors.
    """
    
    def __init__(self):
        # Register the extractors
        self.master_extractor = MasterProbabilitySection()
        self.yoga_extractor = YogaAnalysisSection()
        self.promise_extractor = NatalPromiseSection()
        self.executive_extractor = ExecutiveSummarySection()
        
        # Generic extractors for raw passthrough with titles
        self.planet_extractor = GenericSection("planets", "Planetary Strength Analysis")
        self.house_extractor = GenericSection("houses", "House Strength Analysis")
        self.dasha_extractor = GenericSection("dasha", "Vimshottari Dasha Analysis")
        self.transit_extractor = GenericSection("transits", "Gochara (Transit) Analysis")
        self.av_extractor = GenericSection("ashtakavarga", "Ashtakavarga Analysis")

    def build_json_report(self, pipeline_data: Dict[str, Any], machine_index: Dict[str, Any], questions: List[Dict[str, str]] = None) -> FinalReportSchema:
        """
        Builds the complete immutable report schema.
        """
        
        # Extract basic client info if available
        client_info = {}
        if machine_index:
            native = machine_index.get("native_info", {})
            client_info = {
                "name": native.get("name", "Unknown"),
                "dob": native.get("dob", "Unknown"),
                "tob": native.get("tob", "Unknown"),
                "pob": native.get("pob", "Unknown"),
            }
            
        return FinalReportSchema(
            generated_at=datetime.now(timezone.utc).isoformat(),
            client_info=client_info,
            executive_summary=self.executive_extractor.extract(pipeline_data),
            master_probability=self.master_extractor.extract(pipeline_data),
            natal_promise_analysis=self.promise_extractor.extract(pipeline_data),
            planet_analysis=self.planet_extractor.extract(pipeline_data),
            house_analysis=self.house_extractor.extract(pipeline_data),
            yoga_analysis=self.yoga_extractor.extract(pipeline_data),
            dasha_analysis=self.dasha_extractor.extract(pipeline_data),
            transit_analysis=self.transit_extractor.extract(pipeline_data),
            ashtakavarga_analysis=self.av_extractor.extract(pipeline_data),
            question_responses=questions or []
        )
