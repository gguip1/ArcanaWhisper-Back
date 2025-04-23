from fastapi import APIRouter

from model.history_model import HistoryModel
from schema.tarot import TarotRequest, TarotResponse
from services.llm_service import LLMService

from repository.history_repository import HistoryRepository

router = APIRouter()

@router.post("/tarot", response_model=TarotResponse)
async def get_tarot_reading(request: TarotRequest):
    question = request.question
    
    llmService = LLMService(question, request.cards)
    result = await llmService.get_tarot_reading()
    
    # if request.user_id is not None and request.provider is not None:
    history_repository = HistoryRepository()
    history_repository.save_tarot_reading(
        HistoryModel(
            user_id=request.user_id,
            provider=request.provider,
            question=question,
            cards=request.cards,
            result=result
        )
    )
    
    return {
        "cards": request.cards,
        "result": result
    }