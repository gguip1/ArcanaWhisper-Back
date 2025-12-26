from typing import Optional, List

from pydantic import BaseModel, Field

class TarotCards(BaseModel):
    cards: List[int] = Field(..., min_items=3, max_items=3, example=[1, 5, 22])
    reversed: List[bool] = Field(None, example=[False, True, False])

class TarotRequest(BaseModel):
    user_id: Optional[str] = Field(None, example="user123")
    provider: Optional[str] = Field(None, example="google")
    question: str = Field(..., example="내 연애운은 어떤가요?")
    cards: TarotCards = Field(..., example={"cards": [1, 5, 22], "reversed": [False, True, False]})
    # cards: List[int] = Field(..., min_items=3, max_items=3, example=[1, 5, 22])

class TarotResponse(BaseModel):
    cards: TarotCards = Field(..., example={"cards": [1, 5, 22], "reversed": [False, True, False]})
    result: str
    history_id: str = Field(..., description="Firestore document ID for sharing")

class HistoryItem(BaseModel):
    question: str
    cards: TarotCards = Field(..., example={"cards": [1, 5, 22], "reversed": [False, True, False]})
    result: str
    created_at: str = Field(..., example="2023-10-01T12:00:00Z")

class HistoryResponse(BaseModel):
    history: List[HistoryItem]
    next_cursor_doc_id: Optional[str]