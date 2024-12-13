from typing import List, Optional
from pydantic import BaseModel

from models.types.Answer import Answer


class QuestionOptions(BaseModel):
    minSelect: Optional[int] = None
    maxSelect: Optional[int] = None

class Question(BaseModel):
    name: str = ''
    type: str
    text: str = ''
    description: Optional[str] = None
    order: Optional[int] = None
    required: Optional[bool] = None
    options: Optional[QuestionOptions] = None
    answers: List[Answer]
