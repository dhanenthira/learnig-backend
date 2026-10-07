from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.report import LeaderboardEntry
from app.core.database import get_db
from app.models.sql_models import UserModel

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("", response_model=List[LeaderboardEntry])
def get_leaderboard(
    period: str = Query("all_time", pattern="^(daily|weekly|monthly|all_time)$"),
    category: str = Query("all", pattern="^(all|aptitude|technical|coding)$"),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    students = db.query(UserModel).filter(UserModel.role == "student").order_by(UserModel.total_points.desc()).all()
    
    entries = []
    for idx, s in enumerate(students, start=1):
        entries.append(LeaderboardEntry(
            rank=idx,
            user_id=s.id,
            student_id=s.student_id or f"CA-2026-{idx}",
            name=s.name,
            avatar_url=s.avatar_url,
            questions_solved=s.questions_solved or 0,
            accuracy=s.overall_accuracy or 0.0,
            coding_points=s.total_points or 0,
            battle_wins=s.battles_won or 0,
            streak_days=s.streak_days or 0
        ))
    return entries
