from typing import Optional, List

from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    user_id: Optional[str] = Field(None, example="user123")
    provider: Optional[str] = Field(None, example="google")