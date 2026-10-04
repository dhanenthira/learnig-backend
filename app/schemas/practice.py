from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from app.schemas.question import CategoryEnum, DifficultyEnum, QuestionResponse

class DailySetSummary(BaseModel):
    id: str
    title: str
    category: CategoryEnum
    difficulty: DifficultyEnum
    question_count: int
    estimated_minutes: int
    marks_per_question: int = 1
    total_marks: int
    is_completed: bool = False
    best_score: Optional[int] = None
    created_date: str

class StartPracticeRequest(BaseModel):
    set_id: str
    timer_enabled: bool = True

class QuestionAnswer(BaseModel):
    question_id: str
    selected_option: Optional[str] = None
    is_marked_for_review: bool = False
    time_spent_seconds: int = 0

class PracticeSubmitRequest(BaseModel):
    set_id: str
    answers: List[QuestionAnswer]
    total_time_seconds: int

class QuestionReviewItem(BaseModel):
    question_id: str
    title: str
    content: str
    options: List[str]
    selected_option: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str
    marks_awarded: int

class PracticeResultResponse(BaseModel):
    submission_id: str
    set_id: str
    total_questions: int
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    total_score: int
    max_score: int
    accuracy: float
    time_spent_seconds: int
    reviews: List[QuestionReviewItem]
    points_earned: int
    submitted_at: datetime
