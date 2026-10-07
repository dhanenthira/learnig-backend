from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.notification import NotificationItem, NotificationPreferences
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import NotificationModel

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationItem])
def get_notifications(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    notifs = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id).order_by(NotificationModel.created_at.desc()).all()
    return [NotificationItem.model_validate(n, from_attributes=True) for n in notifs]

@router.post("/mark-all-read")
def mark_all_read(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    notifs = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id).all()
    for n in notifs:
        n.is_read = True
    db.commit()
    return {"status": "success", "message": "All notifications marked as read"}

@router.post("/preferences")
def update_preferences(pref: NotificationPreferences, current_user: UserResponse = Depends(get_current_user)):
    return {"status": "success", "preferences": pref}
