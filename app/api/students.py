from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import UserModel, DailySetModel, LearningModuleModel, AssessmentTestModel, QuestionModel
from app.schemas.practice import DailySetSummary
from app.schemas.lesson import ModuleSummary
from app.schemas.test import AssessmentTest

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/dashboard")
def get_student_dashboard(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        user = db.query(UserModel).first()
    
    daily_sets = db.query(DailySetModel).all()
    modules = db.query(LearningModuleModel).all()
    tests = db.query(AssessmentTestModel).filter(AssessmentTestModel.status.in_(["upcoming", "active"])).all()

    # Top students for leaderboard preview
    top_students = db.query(UserModel).filter(UserModel.role == "student").order_by(UserModel.total_points.desc()).limit(3).all()
    leaderboard_preview = []
    for idx, s in enumerate(top_students, start=1):
        leaderboard_preview.append({
            "rank": idx,
            "name": s.name,
            "student_id": s.student_id,
            "points": s.total_points or 0,
            "avatar": s.avatar_url
        })

    recent_activity = []

    user_resp = UserResponse.model_validate(user, from_attributes=True) if user else current_user

    total_q_count = db.query(QuestionModel).count()

    return {
        "user": user_resp.model_dump(),
        "stats": {
            "total_questions": total_q_count,
            "questions_solved": user.questions_solved if user else 0,
            "overall_accuracy": user.overall_accuracy if user else 0.0,
            "coding_problems_solved": user.coding_problems_solved if user else 0,
            "streak_days": user.streak_days if user else 0,
            "total_points": user.total_points if user else 0,
            "battles_won": user.battles_won if user else 0
        },
        "daily_challenges": [DailySetSummary.model_validate(s, from_attributes=True).model_dump() for s in daily_sets],
        "learning_modules": [ModuleSummary.model_validate(m, from_attributes=True).model_dump() for m in modules],
        "recent_activity": recent_activity,
        "upcoming_tests": [AssessmentTest.model_validate(t, from_attributes=True).model_dump() for t in tests],
        "leaderboard_preview": leaderboard_preview
    }

@router.put("/profile", response_model=UserResponse)
def update_profile(
    updates: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for k in ["name", "college_name", "department", "graduation_year", "bio", "avatar_url"]:
        if k in updates:
            setattr(user, k, updates[k])
            
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user, from_attributes=True)

@router.get("/{student_id}", response_model=UserResponse)
def get_student_by_id(
    student_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    target = db.query(UserModel).filter(
        (UserModel.id == student_id) | (UserModel.student_id == student_id)
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")

    return UserResponse.model_validate(target, from_attributes=True)

