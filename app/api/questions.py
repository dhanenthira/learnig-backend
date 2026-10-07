from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.question import QuestionResponse
from app.core.database import get_db
from app.models.sql_models import QuestionModel

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("", response_model=List[QuestionResponse])
def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    query = db.query(QuestionModel)
    if category:
        query = query.filter(QuestionModel.category == category)
    if difficulty:
        query = query.filter(QuestionModel.difficulty == difficulty)
    if topic:
        query = query.filter(QuestionModel.topic == topic)

    questions = query.limit(limit).all()
    return [QuestionResponse.model_validate(q, from_attributes=True) for q in questions]

import uuid
from datetime import datetime
from app.schemas.question import QuestionCreate

@router.post("", response_model=QuestionResponse)
def create_question_direct(
    q_in: QuestionCreate,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    q_id = f"q_{uuid.uuid4().hex[:8]}"
    new_q = QuestionModel(
        id=q_id,
        title=q_in.title,
        content=q_in.content,
        category=q_in.category.value if hasattr(q_in.category, "value") else str(q_in.category).lower(),
        topic=q_in.topic,
        difficulty=q_in.difficulty.value if hasattr(q_in.difficulty, "value") else str(q_in.difficulty).lower(),
        question_type=q_in.question_type.value if hasattr(q_in.question_type, "value") else str(q_in.question_type),
        options=q_in.options,
        correct_answer=q_in.correct_answer,
        explanation=q_in.explanation or "",
        marks=q_in.marks,
        tags=q_in.tags or [],
        created_at=datetime.utcnow()
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return QuestionResponse.model_validate(new_q, from_attributes=True)

@router.delete("/{question_id}")
def delete_question_direct(
    question_id: str,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    q = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"status": "success", "message": f"Question {question_id} deleted successfully"}

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    apt_count = 0
    tech_count = 0
    code_count = 0
    mixed_count = 0

    if db:
        apt_count = db.query(QuestionModel).filter(QuestionModel.category == "aptitude").count()
        tech_count = db.query(QuestionModel).filter(QuestionModel.category == "technical").count()
        code_count = db.query(QuestionModel).filter(QuestionModel.category == "coding").count()
        mixed_count = db.query(QuestionModel).filter(QuestionModel.category == "mixed").count()

    return [
        {"id": "aptitude", "name": "Quantitative & Logical Aptitude", "count": apt_count, "icon": "brain"},
        {"id": "technical", "name": "Computer Science & Engineering", "count": tech_count, "icon": "cpu"},
        {"id": "coding", "name": "Data Structures & Algorithms", "count": code_count, "icon": "code-2"},
        {"id": "mixed", "name": "Grand Challenge Mix", "count": mixed_count, "icon": "sparkles"}
    ]
