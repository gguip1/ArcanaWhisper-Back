from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from schema.tarot import TarotCards

class HistoryModel(BaseModel):
    user_id: Optional[str]
    provider: Optional[str]
    question: str
    cards: TarotCards = Field(..., example={"cards": [1, 5, 22], "reversed": [False, True, False]})
    result: str
    created_at: datetime = Field(default_factory=datetime.utcnow)