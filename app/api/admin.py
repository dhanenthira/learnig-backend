from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.schemas.user import UserResponse
from app.schemas.question import QuestionCreate, QuestionAdminResponse
from app.api.auth import get_current_admin_user
from app.services.data_store import data_store
from datetime import datetime
import uuid

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get("/dashboard")
def get_admin_dashboard(current_admin: UserResponse = Depends(get_current_admin_user)):
    students_list = [u for u in data_store.users.values() if u.get("role") == "student"]
    questions_list = list(data_store.questions.values())
    coding_list = list(data_store.coding_problems.values())
    
    total_submissions = sum(u.get("questions_solved", 0) for u in students_list) + 120
    
    return {
        "analytics": {
            "total_students": len(students_list),
            "active_students": max(1, int(len(students_list) * 0.8)),
            "published_questions": len(questions_list) + len(coding_list),
            "total_submissions": total_submissions
        },
        "recent_students": students_list[:5],
        "category_performance": [
            {"category": "Aptitude", "accuracy": 82.5, "attempts": 1420},
            {"category": "Technical", "accuracy": 78.4, "attempts": 2130},
            {"category": "Coding Arena", "accuracy": 69.1, "attempts": 950}
        ],
        "weekly_activity": [
            {"day": "Mon", "submissions": 120},
            {"day": "Tue", "submissions": 185},
            {"day": "Wed", "submissions": 240},
            {"day": "Thu", "submissions": 210},
            {"day": "Fri", "submissions": 310},
            {"day": "Sat", "submissions": 450},
            {"day": "Sun", "submissions": 390}
        ],
        "recent_submissions": [
            {"student_name": "Alex Mercer", "problem": "Two Sum", "status": "Accepted", "time": "10 mins ago"},
            {"student_name": "Sophia Chen", "problem": "Time & Distance", "status": "Correct", "time": "25 mins ago"},
            {"student_name": "Marcus Vance", "problem": "Binary Search Complexity", "status": "Correct", "time": "1 hour ago"}
        ]
    }

@router.get("/students", response_model=List[UserResponse])
def get_all_students(current_admin: UserResponse = Depends(get_current_admin_user)):
    return [UserResponse(**u) for u in data_store.users.values() if u.get("role") == "student"]

@router.post("/questions", response_model=QuestionAdminResponse)
def create_question(q_in: QuestionCreate, current_admin: UserResponse = Depends(get_current_admin_user)):
    q_id = f"q_{uuid.uuid4().hex[:8]}"
    q_dict = {
        "id": q_id,
        "title": q_in.title,
        "content": q_in.content,
        "category": q_in.category,
        "topic": q_in.topic,
        "difficulty": q_in.difficulty,
        "question_type": q_in.question_type,
        "options": q_in.options,
        "correct_answer": q_in.correct_answer,
        "explanation": q_in.explanation,
        "marks": q_in.marks,
        "tags": q_in.tags,
        "created_at": datetime.utcnow()
    }
    data_store.questions[q_id] = q_dict
    return QuestionAdminResponse(**q_dict)

@router.delete("/questions/{q_id}")
def delete_question(q_id: str, current_admin: UserResponse = Depends(get_current_admin_user)):
    if q_id in data_store.questions:
        del data_store.questions[q_id]
        return {"status": "success", "message": f"Question {q_id} deleted"}
    raise HTTPException(status_code=404, detail="Question not found")
