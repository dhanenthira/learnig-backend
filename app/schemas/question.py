from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class CategoryEnum(str, Enum):
    APTITUDE = "aptitude"
    TECHNICAL = "technical"
    CODING = "coding"
    MIXED = "mixed"

class DifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MCQ = "mcq"
    MULTI_SELECT = "multi_select"
    NUMERIC = "numeric"

class QuestionBase(BaseModel):
    title: str
    content: str
    category: CategoryEnum
    topic: str
    difficulty: DifficultyEnum
    question_type: QuestionType = QuestionType.MCQ
    options: List[str] = []
    explanation: Optional[str] = ""
    marks: int = 1
    tags: List[str] = []

class QuestionCreate(QuestionBase):
    correct_answer: str # Kept hidden on public client responses

class QuestionResponse(QuestionBase):
    id: str
    created_at: datetime
    # Note: correct_answer is omitted when question is active/unsubmitted

class QuestionAdminResponse(QuestionBase):
    id: str
    correct_answer: str
    created_at: datetime
