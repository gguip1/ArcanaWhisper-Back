from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class HistoryModel(BaseModel):
    user_id: Optional[str]
    provider: Optional[str]
    question: str
    cards: List[int] = Field(..., min_items=3, max_items=3)
    result: str
    created_at: datetime = Field(default_factory=datetime.utcnow)