from typing import List

from pydantic import BaseModel, Field

class TarotRequest(BaseModel):
    cards: List[int] = Field(..., min_items=3, max_items=3, example=[1, 5, 22])

class TarotResponse(BaseModel):
    message: str
    cards: List[int]
    result: str