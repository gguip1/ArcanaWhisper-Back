from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from src.dependencies.dependencies import get_history_repository
from src.repository.history_repository import HistoryRepository
from src.schema.tarot import HistoryResponse, TarotRequest, TarotResponse
from src.services.history_service import HistoryService
from src.services.tarot_service import TarotService

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

@router.get("/tarot/history", response_model=HistoryResponse)
def get_tarot_history(
    user_id: str = Query(..., description="OAuth 식별자"),
    provider: str = Query(..., description="OAuth 제공자"),
    cursor_doc_id: Optional[str] = Query(None, description="다음 페이지를 위한 커서"),
    history_repository: HistoryRepository = Depends(get_history_repository)
    ):
    historyService = HistoryService(
        user_id=user_id,
        provider=provider,
        cursor_doc_id=cursor_doc_id,
        history_repository=history_repository
    )
    history = historyService.get_history()
    
    return history