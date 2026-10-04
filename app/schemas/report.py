from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CategoryPerformance(BaseModel):
    category: str
    total_attempted: int
    correct: int
    accuracy: float
    total_time_minutes: float

class WeeklyActivityItem(BaseModel):
    day: str
    problems_solved: int
    minutes_spent: int

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    student_id: str
    name: str
    avatar_url: Optional[str] = None
    questions_solved: int
    accuracy: float
    coding_points: int
    battle_wins: int
    streak_days: int

class StudentAnalyticsResponse(BaseModel):
    total_questions: int
    questions_solved: int
    overall_accuracy: float
    coding_problems_solved: int
    streak_days: int
    rank: int
    total_points: int
    category_performances: List[CategoryPerformance] = []
    weekly_activity: List[WeeklyActivityItem] = []
    recent_activity: List[Dict[str, Any]] = []
    weak_areas: List[str] = []
    strong_areas: List[str] = []

class AdminAnalyticsResponse(BaseModel):
    total_students: int
    active_students_today: int
    published_questions: int
    total_submissions: int
    category_breakdown: Dict[str, int] = {}
    weekly_registrations: List[Dict[str, Any]] = []
    difficulty_distribution: Dict[str, int] = {}
    system_accuracy_avg: float
