from typing import Optional, List

from pydantic import BaseModel, Field

class TarotRequest(BaseModel):
    user_id: Optional[str] = Field(None, example="user123")
    provider: Optional[str] = Field(None, example="google")
    question: str = Field(..., example="내 연애운은 어떤가요?")
    cards: List[int] = Field(..., min_items=3, max_items=3, example=[1, 5, 22])

class TarotResponse(BaseModel):
    cards: List[int]
    result: str

class HistoryItem(BaseModel):
    question: str
    cards: List[int]
    result: str
    created_at: str = Field(..., example="2023-10-01T12:00:00Z")