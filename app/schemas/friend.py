from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FriendProfile(BaseModel):
    user_id: str
    student_id: str
    name: str
    email: str
    college_name: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = ""
    problems_solved: int = 0
    accuracy: float = 0.0
    streak_days: int = 0
    battles_won: int = 0
    is_following: bool = False
    has_pending_request: bool = False

class FriendRequestAction(BaseModel):
    target_user_id: str

class FriendSearchQuery(BaseModel):
    query: str
