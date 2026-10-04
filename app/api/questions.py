from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.question import QuestionResponse, CategoryEnum, DifficultyEnum
from app.services.data_store import data_store

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("", response_model=List[QuestionResponse])
def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 50
):
    results = []
    for q in data_store.questions.values():
        if category and q.get("category") != category:
            continue
        if difficulty and q.get("difficulty") != difficulty:
            continue
        if topic and q.get("topic") != topic:
            continue
        # Client response does not reveal correct_answer directly
        q_copy = dict(q)
        results.append(QuestionResponse(**q_copy))
        if len(results) >= limit:
            break
    return results

@router.get("/categories")
def get_categories():
    return [
        {"id": "aptitude", "name": "Quantitative & Logical Aptitude", "count": 240, "icon": "brain"},
        {"id": "technical", "name": "Computer Science & Engineering", "count": 310, "icon": "cpu"},
        {"id": "coding", "name": "Data Structures & Algorithms", "count": 180, "icon": "code-2"},
        {"id": "mixed", "name": "Grand Challenge Mix", "count": 120, "icon": "sparkles"}
    ]
