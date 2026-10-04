from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/dashboard")
def get_student_dashboard(current_user: UserResponse = Depends(get_current_user)):
    user = data_store.users.get(current_user.id, current_user.dict())
    
    # Daily challenge summary
    daily_sets = list(data_store.daily_sets.values())
    
    # Learning progress
    modules = list(data_store.modules.values())
    
    # Recent activity
    recent_activity = [
        {"title": "Completed Two Sum Target Indices", "type": "coding", "time": "2 hours ago", "points": "+25 XP"},
        {"title": "Daily Technical Challenge #42", "type": "practice", "time": "Yesterday", "points": "+20 XP"},
        {"title": "Won 1v1 Battle vs Sophia Chen", "type": "battle", "time": "2 days ago", "points": "+50 XP"}
    ]
    
    # Upcoming tests
    tests = [t for t in data_store.tests.values() if t["status"] in ["upcoming", "active"]]

    # Leaderboard preview
    leaderboard_preview = [
        {"rank": 1, "name": "Sophia Chen", "student_id": "CA-2026-8190", "points": 5620, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sophia"},
        {"rank": 2, "name": user.get("name"), "student_id": user.get("student_id"), "points": user.get("total_points", 4850), "avatar": user.get("avatar_url")},
        {"rank": 3, "name": "Marcus Vance", "student_id": "CA-2026-7241", "points": 4310, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Marcus"},
    ]

    return {
        "user": user,
        "stats": {
            "total_questions": 850,
            "questions_solved": user.get("questions_solved", 380),
            "overall_accuracy": user.get("overall_accuracy", 88.2),
            "coding_problems_solved": user.get("coding_problems_solved", 56),
            "streak_days": user.get("streak_days", 14),
            "total_points": user.get("total_points", 4850),
            "battles_won": user.get("battles_won", 19)
        },
        "daily_challenges": daily_sets,
        "learning_modules": modules,
        "recent_activity": recent_activity,
        "upcoming_tests": tests,
        "leaderboard_preview": leaderboard_preview
    }

@router.put("/profile", response_model=UserResponse)
def update_profile(updates: Dict[str, Any], current_user: UserResponse = Depends(get_current_user)):
    user = data_store.users.get(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for k in ["name", "college_name", "department", "graduation_year", "bio", "avatar_url"]:
        if k in updates and updates[k] is not None:
            user[k] = updates[k]
            
    return UserResponse(**user)
