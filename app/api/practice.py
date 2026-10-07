from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.schemas.practice import DailySetSummary, PracticeSubmitRequest, PracticeResultResponse, QuestionReviewItem
from app.schemas.question import QuestionResponse
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import DailySetModel, QuestionModel, UserModel, SubmissionModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/practice", tags=["Daily Practice"])

@router.get("/daily-sets", response_model=List[DailySetSummary])
def get_daily_sets(db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    sets = db.query(DailySetModel).all()
    return [DailySetSummary.model_validate(s, from_attributes=True) for s in sets]

@router.get("/set/{set_id}/questions", response_model=List[QuestionResponse])
def get_set_questions(set_id: str, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    daily_set = db.query(DailySetModel).filter(DailySetModel.id == set_id).first()
    if not daily_set:
        raise HTTPException(status_code=404, detail="Practice set not found")
    
    questions = []
    for q_id in daily_set.question_ids or []:
        q = db.query(QuestionModel).filter(QuestionModel.id == q_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q, from_attributes=True))
    return questions

@router.post("/submit", response_model=PracticeResultResponse)
def submit_practice(
    submission: PracticeSubmitRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    daily_set = db.query(DailySetModel).filter(DailySetModel.id == submission.set_id).first()
    if not daily_set:
        raise HTTPException(status_code=404, detail="Practice set not found")
        
    reviews: List[QuestionReviewItem] = []
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    total_score = 0
    
    answers_map = {a.question_id: a.selected_option for a in submission.answers}
    
    for q_id in daily_set.question_ids or []:
        q = db.query(QuestionModel).filter(QuestionModel.id == q_id).first()
        if not q:
            continue
            
        selected = answers_map.get(q_id)
        correct = q.correct_answer
        is_correct = (selected == correct) if selected else False
        
        if selected is None:
            unanswered_count += 1
            marks = 0
        elif is_correct:
            correct_count += 1
            marks = q.marks or 1
            total_score += marks
        else:
            incorrect_count += 1
            marks = 0
            
        reviews.append(QuestionReviewItem(
            question_id=q.id,
            title=q.title,
            content=q.content,
            options=q.options or [],
            selected_option=selected,
            correct_answer=correct,
            is_correct=is_correct,
            explanation=q.explanation or "",
            marks_awarded=marks
        ))
        
    total_q = len(daily_set.question_ids or [])
    accuracy = round((correct_count / max(1, (correct_count + incorrect_count))) * 100, 1) if (correct_count + incorrect_count) > 0 else 0.0
    points_earned = total_score * 10
    
    # Update user progress in MySQL
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if db_user:
        db_user.total_points = (db_user.total_points or 0) + points_earned
        db_user.questions_solved = (db_user.questions_solved or 0) + correct_count
        db_user.problems_solved = (db_user.problems_solved or 0) + 1
        db_user.streak_days = max(1, (db_user.streak_days or 1) + 1)
        
    daily_set.is_completed = True
    daily_set.best_score = max(daily_set.best_score or 0, total_score)
    
    sub_id = f"sub_prac_{uuid.uuid4().hex[:8]}"
    new_sub = SubmissionModel(
        id=sub_id,
        user_id=current_user.id,
        problem_id=submission.set_id,
        submission_type="practice",
        status="completed",
        passed_test_cases=correct_count,
        total_test_cases=total_q,
        score=float(total_score),
        max_score=float(daily_set.total_marks or total_q),
        answers=answers_map,
        reviews=[r.model_dump() for r in reviews],
        submitted_at=datetime.utcnow()
    )
    db.add(new_sub)
    db.commit()
    
    return PracticeResultResponse(
        submission_id=sub_id,
        set_id=submission.set_id,
        total_questions=total_q,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unanswered_count=unanswered_count,
        total_score=total_score,
        max_score=daily_set.total_marks or total_q,
        accuracy=accuracy,
        time_spent_seconds=submission.total_time_seconds,
        reviews=reviews,
        points_earned=points_earned,
        submitted_at=datetime.utcnow()
    )
