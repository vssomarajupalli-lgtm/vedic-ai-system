from fastapi import APIRouter, HTTPException
from typing import Any
import traceback

from app.schemas.question import QuestionRequest, QuestionResponse
from app.pipeline_runner import PipelineRunner
from app.core.logging import log
from app.core.question_router import QuestionRouter

router = APIRouter()

# Instantiate the stateless modules
pipeline_runner = PipelineRunner()
question_router = QuestionRouter()

@router.post("/ask-question", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> Any:
    """
    Stateless endpoint to answer an astrological question using an LLM,
    grounded by the deterministic math provided in the payload.
    """
    try:
        log.info("Processing question request...")
        
        # 1. Validation: Must have either text or ID
        if not request.question_text and not request.question_id:
            raise HTTPException(status_code=400, detail="Must provide either question_text or question_id")
        
        # Extract actual internal payload if wrapped inside a ChartProcessResponse
        internal_payload = request.engine_outputs.get("breakdown", request.engine_outputs)
        
        resolved_question_id = None
        question_text_to_process = request.question_text
        
        # 2. Question Router flow
        if request.question_id:
            route_result = question_router.route_question(request.question_id)
            if route_result["status"] == "error":
                # If error is a configuration error, 500, otherwise 422 for client errors
                status_code = 500 if route_result["error_type"] == "registry_configuration_error" else 422
                raise HTTPException(status_code=status_code, detail=route_result["message"])
                
            resolved_question_id = request.question_id
            metadata = route_result["metadata"]
            
            # Since the LLM still needs a natural language question text to base its answer on,
            # we inject the deterministic question_name if user left text blank
            if not question_text_to_process:
                question_text_to_process = metadata.get("question_name", "Astrological Query")
        
        # 3. Use PipelineRunner as the orchestrator to answer the question
        # (Preserves legacy pipeline compatibility until phase 11D)
        result = pipeline_runner.answer_question(
            question=question_text_to_process,
            pipeline_output=internal_payload
        )
        
        answer = result.get("answer_text", "")
        # Deterministic engine currently doesn't track used yogas in response
        used_yogas = []
        
        log.info("Question answered successfully.")
        
        return QuestionResponse(
            answer_text=answer,
            referenced_yogas=used_yogas,
            resolved_question_id=resolved_question_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error during question generation: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Question Engine failed: {str(e)}"
        )
