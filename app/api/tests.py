from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.test import AssessmentTest, TestSubmitRequest, TestResultResponse
from app.schemas.question import QuestionResponse
from app.schemas.practice import QuestionReviewItem
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import AssessmentTestModel, QuestionModel, UserModel, SubmissionModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/tests", tags=["Assessment Tests"])

@router.get("/available", response_model=List[AssessmentTest])
def get_available_tests(db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    tests = db.query(AssessmentTestModel).all()
    results = []
    for t in tests:
        t_data = AssessmentTest.model_validate(t, from_attributes=True)
        t_data.total_questions = len(t.question_ids or [])
        results.append(t_data)
    return results

@router.get("/{test_id}", response_model=AssessmentTest)
def get_test_detail(test_id: str, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    test = db.query(AssessmentTestModel).filter(AssessmentTestModel.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Assessment test not found")
        
    t_data = AssessmentTest.model_validate(test, from_attributes=True)
    questions = []
    for q_id in test.question_ids or []:
        q = db.query(QuestionModel).filter(QuestionModel.id == q_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q, from_attributes=True))
    t_data.questions = questions
    t_data.total_questions = len(questions)
    return t_data

@router.post("/submit", response_model=TestResultResponse)
def submit_test(
    submission: TestSubmitRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    test = db.query(AssessmentTestModel).filter(AssessmentTestModel.id == submission.test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    reviews: List[QuestionReviewItem] = []
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    total_score = 0
    
    answers_map = {a.question_id: a.selected_option for a in submission.answers}
    
    for q_id in test.question_ids or []:
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
        
    accuracy = round((correct_count / max(1, (correct_count + incorrect_count))) * 100, 1) if (correct_count + incorrect_count) > 0 else 0.0
    
    # Update user points in MySQL
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if db_user:
        db_user.total_points = (db_user.total_points or 0) + (total_score * 15)
        db_user.questions_solved = (db_user.questions_solved or 0) + correct_count
        
    test.is_attempted = True
    test.score = total_score
    
    sub_id = f"tsub_{uuid.uuid4().hex[:8]}"
    new_sub = SubmissionModel(
        id=sub_id,
        user_id=current_user.id,
        problem_id=submission.test_id,
        submission_type="test",
        status="completed",
        passed_test_cases=correct_count,
        total_test_cases=len(test.question_ids or []),
        score=float(total_score),
        max_score=float(test.total_marks or len(test.question_ids or [])),
        answers=answers_map,
        reviews=[r.model_dump() for r in reviews],
        submitted_at=datetime.utcnow()
    )
    db.add(new_sub)
    db.commit()

    return TestResultResponse(
        test_id=submission.test_id,
        title=test.title,
        total_score=total_score,
        max_score=test.total_marks or len(test.question_ids or []),
        accuracy=accuracy,
        time_taken_seconds=submission.time_taken_seconds,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unanswered_count=unanswered_count,
        rank=1,
        percentile=95.0,
        reviews=reviews,
        submitted_at=datetime.utcnow()
    )
