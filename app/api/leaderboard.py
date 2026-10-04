from fastapi import APIRouter, Query
from typing import List, Optional
from app.schemas.report import LeaderboardEntry
from app.services.data_store import data_store

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("", response_model=List[LeaderboardEntry])
def get_leaderboard(
    period: str = Query("all_time", pattern="^(daily|weekly|monthly|all_time)$"),
    category: str = Query("all", pattern="^(all|aptitude|technical|coding)$")
):
    students = [u for u in data_store.users.values() if u.get("role") == "student"]
    
    # Sort by points descending
    sorted_students = sorted(students, key=lambda x: x.get("total_points", 0), reverse=True)
    
    entries = []
    for idx, s in enumerate(sorted_students, start=1):
        entries.append(LeaderboardEntry(
            rank=idx,
            user_id=s["id"],
            student_id=s["student_id"],
            name=s["name"],
            avatar_url=s.get("avatar_url"),
            questions_solved=s.get("questions_solved", 0),
            accuracy=s.get("overall_accuracy", 0.0),
            coding_points=s.get("total_points", 0),
            battle_wins=s.get("battles_won", 0),
            streak_days=s.get("streak_days", 0)
        ))
    return entries
