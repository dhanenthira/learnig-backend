from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.schemas.report import StudentAnalyticsResponse, AdminAnalyticsResponse
from app.schemas.user import UserResponse
from app.api.auth import get_current_user, get_current_admin_user
from app.services.data_store import data_store

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/student/{user_id}", response_model=StudentAnalyticsResponse)
def get_student_report(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    user = data_store.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return StudentAnalyticsResponse(
        total_questions=850,
        questions_solved=user.get("questions_solved", 380),
        overall_accuracy=user.get("overall_accuracy", 88.2),
        coding_problems_solved=user.get("coding_problems_solved", 56),
        streak_days=user.get("streak_days", 14),
        rank=2,
        total_points=user.get("total_points", 4850),
        category_performances=[
            {"category": "Quantitative Aptitude", "total_attempted": 180, "correct": 162, "accuracy": 90.0, "total_time_minutes": 140.0},
            {"category": "Computer Science Core", "total_attempted": 120, "correct": 105, "accuracy": 87.5, "total_time_minutes": 95.0},
            {"category": "Data Structures & Algos", "total_attempted": 80, "correct": 68, "accuracy": 85.0, "total_time_minutes": 180.0},
        ],
        weekly_activity=[
            {"day": "Mon", "problems_solved": 8, "minutes_spent": 45},
            {"day": "Tue", "problems_solved": 12, "minutes_spent": 60},
            {"day": "Wed", "problems_solved": 15, "minutes_spent": 75},
            {"day": "Thu", "problems_solved": 10, "minutes_spent": 50},
            {"day": "Fri", "problems_solved": 18, "minutes_spent": 90},
            {"day": "Sat", "problems_solved": 25, "minutes_spent": 120},
            {"day": "Sun", "problems_solved": 20, "minutes_spent": 100},
        ],
        recent_activity=[
            {"activity": "Solved Two Sum Target Indices", "type": "Coding", "status": "Passed", "date": "Today"},
            {"activity": "Completed Daily Aptitude Challenge #42", "type": "Practice", "status": "100%", "date": "Yesterday"},
            {"activity": "Grand Assessment Screening", "type": "Test", "status": "Rank #12", "date": "3 days ago"}
        ],
        weak_areas=["Dynamic Programming", "Probability & Combinatorics"],
        strong_areas=["Arrays & Hash Maps", "Time & Distance", "Binary Search"]
    )

@router.get("/admin", response_model=AdminAnalyticsResponse)
def get_admin_analytics(current_admin: UserResponse = Depends(get_current_admin_user)):
    students_list = [u for u in data_store.users.values() if u.get("role") == "student"]
    return AdminAnalyticsResponse(
        total_students=len(students_list),
        active_students_today=max(1, int(len(students_list) * 0.8)),
        published_questions=len(data_store.questions) + len(data_store.coding_problems),
        total_submissions=3850,
        category_breakdown={"Aptitude": 45, "Technical": 35, "Coding": 20},
        weekly_registrations=[
            {"week": "Week 1", "registrations": 42},
            {"week": "Week 2", "registrations": 68},
            {"week": "Week 3", "registrations": 95},
            {"week": "Week 4", "registrations": 140}
        ],
        difficulty_distribution={"Easy": 40, "Medium": 45, "Hard": 15},
        system_accuracy_avg=84.6
    )
