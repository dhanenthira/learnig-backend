from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.schemas.practice import DailySetSummary, PracticeSubmitRequest, PracticeResultResponse, QuestionReviewItem
from app.schemas.question import QuestionResponse
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store
from datetime import datetime
import uuid

router = APIRouter(prefix="/practice", tags=["Daily Practice"])

@router.get("/daily-sets", response_model=List[DailySetSummary])
def get_daily_sets():
    return [DailySetSummary(**s) for s in data_store.daily_sets.values()]

@router.get("/set/{set_id}/questions", response_model=List[QuestionResponse])
def get_set_questions(set_id: str):
    daily_set = data_store.daily_sets.get(set_id)
    if not daily_set:
        raise HTTPException(status_code=404, detail="Practice set not found")
    
    questions = []
    for q_id in daily_set.get("question_ids", []):
        q = data_store.questions.get(q_id)
        if q:
            q_copy = dict(q)
            questions.append(QuestionResponse(**q_copy))
    return questions

@router.post("/submit", response_model=PracticeResultResponse)
def submit_practice(submission: PracticeSubmitRequest, current_user: UserResponse = Depends(get_current_user)):
    daily_set = data_store.daily_sets.get(submission.set_id)
    if not daily_set:
        raise HTTPException(status_code=404, detail="Practice set not found")
        
    reviews: List[QuestionReviewItem] = []
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    total_score = 0
    
    answers_map = {a.question_id: a.selected_option for a in submission.answers}
    
    for q_id in daily_set.get("question_ids", []):
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
    points = total_score * 10
    
    # Update user stats
    user = data_store.users.get(current_user.id)
    if user:
        user["questions_solved"] = user.get("questions_solved", 0) + correct_count
        user["total_points"] = user.get("total_points", 0) + points
        # mark set completed
        daily_set["is_completed"] = True
        daily_set["best_score"] = max(daily_set.get("best_score", 0) or 0, total_score)
        
    sub_id = f"sub_{uuid.uuid4().hex[:8]}"
    result = PracticeResultResponse(
        submission_id=sub_id,
        set_id=submission.set_id,
        total_questions=total_q,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unanswered_count=unanswered_count,
        total_score=total_score,
        max_score=daily_set.get("total_marks", total_q),
        accuracy=accuracy,
        time_spent_seconds=submission.total_time_seconds,
        reviews=reviews,
        points_earned=points,
        submitted_at=datetime.utcnow()
    )
    
    data_store.practice_submissions[sub_id] = result.dict()
    return result
