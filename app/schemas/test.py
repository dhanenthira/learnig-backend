from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from app.schemas.question import CategoryEnum, DifficultyEnum, QuestionResponse
from app.schemas.practice import QuestionAnswer, QuestionReviewItem

class TestStatusEnum(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"

class AssessmentTest(BaseModel):
    id: str
    title: str
    description: str
    category: CategoryEnum
    difficulty: DifficultyEnum
    duration_minutes: int
    total_marks: int
    total_questions: int
    rules: List[str] = []
    start_time: datetime
    end_time: datetime
    status: TestStatusEnum
    is_attempted: bool = False
    score: Optional[int] = None
    questions: Optional[List[QuestionResponse]] = None

class TestSubmitRequest(BaseModel):
    test_id: str
    answers: List[QuestionAnswer]
    time_taken_seconds: int

class TestResultResponse(BaseModel):
    test_id: str
    title: str
    total_score: int
    max_score: int
    accuracy: float
    time_taken_seconds: int
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    rank: Optional[int] = None
    percentile: Optional[float] = None
    reviews: List[QuestionReviewItem] = []
    submitted_at: datetime
