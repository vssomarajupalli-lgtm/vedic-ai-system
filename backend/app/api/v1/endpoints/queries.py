from fastapi import APIRouter, HTTPException
from typing import Any
import traceback

from app.schemas.question import QuestionRequest, QuestionResponse
from app.pipeline_runner import PipelineRunner
from app.core.logging import log

router = APIRouter()

# Instantiate the stateless PipelineRunner
pipeline_runner = PipelineRunner()

@router.post("/ask-question", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> Any:
    """
    Stateless endpoint to answer an astrological question using an LLM,
    grounded by the deterministic math provided in the payload.
    """
    try:
        log.info(f"Processing question: {request.question_text[:50]}...")
        
        # Extract actual internal payload if wrapped inside a ChartProcessResponse
        internal_payload = request.engine_outputs.get("breakdown", request.engine_outputs)
        
        # Use PipelineRunner as the orchestrator to answer the question
        result = pipeline_runner.answer_question(
            question=request.question_text,
            pipeline_output=internal_payload
        )
        
        answer = result.get("answer_text", "")
        # Deterministic engine currently doesn't track used yogas in response
        used_yogas = []
        
        log.info("Question answered successfully.")
        
        return QuestionResponse(
            answer_text=answer,
            referenced_yogas=used_yogas
        )
        
    except Exception as e:
        log.error(f"Error during question generation: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Question Engine failed: {str(e)}"
        )
