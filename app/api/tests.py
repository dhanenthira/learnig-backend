from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.test import AssessmentTest, TestSubmitRequest, TestResultResponse
from app.schemas.question import QuestionResponse
from app.schemas.practice import QuestionReviewItem
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store
from datetime import datetime
import uuid

router = APIRouter(prefix="/tests", tags=["Assessment Tests"])

@router.get("/available", response_model=List[AssessmentTest])
def get_available_tests():
    tests_list = []
    for t in data_store.tests.values():
        t_copy = dict(t)
        # populate question count
        t_copy["total_questions"] = len(t.get("question_ids", []))
        tests_list.append(AssessmentTest(**t_copy))
    return tests_list

@router.get("/{test_id}", response_model=AssessmentTest)
def get_test_detail(test_id: str):
    test = data_store.tests.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Assessment test not found")
        
    t_copy = dict(test)
    questions = []
    for q_id in test.get("question_ids", []):
        q = data_store.questions.get(q_id)
        if q:
            questions.append(QuestionResponse(**dict(q)))
    t_copy["questions"] = questions
    t_copy["total_questions"] = len(questions)
    return AssessmentTest(**t_copy)

@router.post("/submit", response_model=TestResultResponse)
def submit_test(submission: TestSubmitRequest, current_user: UserResponse = Depends(get_current_user)):
    test = data_store.tests.get(submission.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    reviews: List[QuestionReviewItem] = []
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    total_score = 0
    
    answers_map = {a.question_id: a.selected_option for a in submission.answers}
    
    for q_id in test.get("question_ids", []):
        q = data_store.questions.get(q_id)
        if not q:
            continue
            
        selected = answers_map.get(q_id)
        correct = q.get("correct_answer")
        is_correct = (selected == correct) if selected else False
        
        if selected is None:
            unanswered_count += 1
            marks = 0
        elif is_correct:
            correct_count += 1
            marks = q.get("marks", 1)
            total_score += marks
        else:
            incorrect_count += 1
            marks = 0
            
        reviews.append(QuestionReviewItem(
            question_id=q_id,
            title=q.get("title", ""),
            content=q.get("content", ""),
            options=q.get("options", []),
            selected_option=selected,
            correct_answer=correct,
            is_correct=is_correct,
            explanation=q.get("explanation", ""),
            marks_awarded=marks
        ))
        
    total_q = len(reviews)
    accuracy = round((correct_count / max(1, total_q)) * 100, 1)
    
    # Mark test attempted
    test["is_attempted"] = True
    test["score"] = total_score
    
    user = data_store.users.get(current_user.id)
    if user:
        user["total_points"] = user.get("total_points", 0) + (total_score * 20)
        
    res = TestResultResponse(
        test_id=submission.test_id,
        title=test.get("title", "Assessment"),
        total_score=total_score,
        max_score=test.get("total_marks", total_q),
        accuracy=accuracy,
        time_taken_seconds=submission.time_taken_seconds,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unanswered_count=unanswered_count,
        rank=12,
        percentile=94.5,
        reviews=reviews,
        submitted_at=datetime.utcnow()
    )
    
    data_store.test_submissions[f"tsub_{uuid.uuid4().hex[:8]}"] = res.dict()
    return res
