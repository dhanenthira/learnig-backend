from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    type: str # daily_challenge, learning, test, friend, battle, announcement
    is_read: bool = False
    action_url: Optional[str] = None
    created_at: datetime

class NotificationPreferences(BaseModel):
    daily_reminders: bool = True
    friend_activity: bool = True
    test_alerts: bool = True
    battle_invites: bool = True
    email_digest: bool = False
