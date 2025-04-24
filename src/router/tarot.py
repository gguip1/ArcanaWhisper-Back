from fastapi import APIRouter, Depends, Query
from typing import List

from dependencies.dependencies import get_history_repository
from repository.history_repository import HistoryRepository
from schema.tarot import HistoryItem, TarotRequest, TarotResponse
from schema.user import UserRequest
from services.history_service import HistoryService
from services.tarot_service import TarotService

router = APIRouter()

@router.post("/tarot", response_model=TarotResponse)
async def get_tarot_reading(
    request: TarotRequest,
    history_repository: HistoryRepository = Depends(get_history_repository)
    ):
    tarotService = TarotService(
        request.user_id, 
        request.provider, 
        request.question, 
        request.cards,
        history_repository
    )
    result = await tarotService.get_tarot_reading()
    
    return result

@router.get("/tarot/history", response_model=List[HistoryItem])
async def get_tarot_history(
    # request: UserRequest,
    user_id: str = Query(..., description="OAuth 식별자"),
    provider: str = Query(..., description="OAuth 제공자"),
    history_repository: HistoryRepository = Depends(get_history_repository)
    ):
    historyService = HistoryService(
        user_id,
        provider, 
        history_repository
    )
    history = historyService.get_history()
    
    return history