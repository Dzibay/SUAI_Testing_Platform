from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from models.types.Question import Question


class Survey(BaseModel):
    id: str
    owner: str
    title: str
    description: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    startDate: datetime
    endDate: datetime
    status: str  # 'completed' | 'pending' | 'waiting'
    maxResponses: Optional[int] = None
    isAnonymous: Optional[bool] = None
    tags: Optional[List[str]] = None
    questions: List[Question]
