from typing import Optional
from pydantic import BaseModel

class Answer(BaseModel):
    text: str
    type: str  # 'radio' | 'checkbox' | 'custom'
    description: Optional[str] = None
    order: Optional[int] = None
    isCorrect: Optional[bool] = None
