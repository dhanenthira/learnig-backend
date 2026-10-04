from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.notification import NotificationItem, NotificationPreferences
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationItem])
def get_notifications(current_user: UserResponse = Depends(get_current_user)):
    user_notifs = data_store.notifications.get(current_user.id, [])
    return [NotificationItem(**n) for n in user_notifs]

@router.post("/mark-all-read")
def mark_all_read(current_user: UserResponse = Depends(get_current_user)):
    user_notifs = data_store.notifications.get(current_user.id, [])
    for n in user_notifs:
        n["is_read"] = True
    return {"status": "success", "message": "All notifications marked as read"}

@router.post("/preferences")
def update_preferences(pref: NotificationPreferences, current_user: UserResponse = Depends(get_current_user)):
    return {"status": "success", "preferences": pref}
