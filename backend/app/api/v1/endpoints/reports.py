from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from typing import Any, Optional, Dict
import traceback

from app.schemas.chart import ChartProcessRequest
from app.pipeline_runner import PipelineRunner
from app.reports.builder import ReportBuilder
from app.reports.html_generator import HTMLGenerator
from app.reports.pdf_generator import PDFGenerator
from app.reports.schemas import FinalReportSchema
from app.core.logging import log

router = APIRouter()
pipeline = PipelineRunner()
report_builder = ReportBuilder()
html_generator = HTMLGenerator()
pdf_generator = PDFGenerator()

@router.post("/generate-report")
def generate_report(
    request: ChartProcessRequest, 
    format: str = Query("json", description="Export format: json, html, pdf")
) -> Any:
    """
    Stateless endpoint that accepts raw scraped JSON, runs the astrology engine,
    and formats the output via the ReportBuilder instead of returning raw arrays.
    """
    try:
        log.info(f"Generating report in format: {format}")
        
        # 1. Execute engine (Identical to process-chart)
        raw_data = request.canonical_content
        raw_data["_machine_index"] = request.machine_index
        outputs = pipeline.process(raw_data)
        
        # 2. Extract into final schema
        report = report_builder.build_json_report(outputs, request.machine_index)
        
        # 3. Handle export formats
        if format.lower() == "json":
            return report
        elif format.lower() == "html":
            html_content = html_generator.generate(report)
            return HTMLResponse(content=html_content)
        elif format.lower() == "pdf":
            try:
                pdf_bytes = pdf_generator.generate(report)
                return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=vedic_ai_report.pdf"})
            except RuntimeError as re:
                raise HTTPException(status_code=501, detail=str(re))
        else:
            raise HTTPException(status_code=400, detail="Invalid format requested. Supported: json, html, pdf.")
            
    except Exception as e:
        log.error(f"Error generating report: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Report Generation failed: {str(e)}")
