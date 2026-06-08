from fastapi import APIRouter, HTTPException
from typing import Any
import traceback

from app.schemas.question import QuestionRequest, QuestionResponse
from app.engines.question_engine import QuestionEngine
from app.core.logging import log

router = APIRouter()

# Instantiate the stateless QuestionEngine
# Note: For it to answer properly, the OPENAI_API_KEY env var must be set,
# though the architecture dictates we handle configuration gracefully.
question_engine = QuestionEngine()

@router.post("/ask-question", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> Any:
    """
    Stateless endpoint to answer an astrological question using an LLM,
    grounded by the deterministic math provided in the payload.
    """
    try:
        log.info(f"Processing question: {request.question_text[:50]}...")
        
        # The QuestionEngine expects the full math payload in its context builder
        answer, used_yogas = question_engine.answer(
            question=request.question_text,
            chart_results=request.engine_outputs
        )
        
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
