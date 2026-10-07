from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.friend import FriendProfile, FriendRequestAction
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import UserModel, UserFollowModel
import uuid
from datetime import datetime

router = APIRouter(prefix="/friends", tags=["Friends & Community"])

@router.get("/list", response_model=List[FriendProfile])
def get_friends_list(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    follows = db.query(UserFollowModel).filter(UserFollowModel.follower_id == current_user.id).all()
    friends = []
    for f in follows:
        u = db.query(UserModel).filter(UserModel.id == f.following_id).first()
        if u:
            friends.append(FriendProfile(
                user_id=u.id,
                student_id=u.student_id or u.id[:8],
                name=u.name,
                email=u.email,
                college_name=u.college_name,
                department=u.department,
                avatar_url=u.avatar_url,
                bio=u.bio or "",
                problems_solved=u.problems_solved or 0,
                accuracy=u.overall_accuracy or 0.0,
                streak_days=u.streak_days or 0,
                battles_won=u.battles_won or 0,
                is_following=True,
                has_pending_request=False
            ))
    return friends

@router.get("/search", response_model=List[FriendProfile])
def search_students(
    query: str = Query(..., min_length=1),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    follows = db.query(UserFollowModel).filter(UserFollowModel.follower_id == current_user.id).all()
    following_ids = {f.following_id for f in follows}
    
    users = db.query(UserModel).filter(
        UserModel.id != current_user.id,
        (UserModel.name.ilike(f"%{query}%") | UserModel.student_id.ilike(f"%{query}%") | UserModel.email.ilike(f"%{query}%"))
    ).all()

    results = []
    for u in users:
        results.append(FriendProfile(
            user_id=u.id,
            student_id=u.student_id or u.id[:8],
            name=u.name,
            email=u.email,
            college_name=u.college_name,
            department=u.department,
            avatar_url=u.avatar_url,
            bio=u.bio or "",
            problems_solved=u.problems_solved or 0,
            accuracy=u.overall_accuracy or 0.0,
            streak_days=u.streak_days or 0,
            battles_won=u.battles_won or 0,
            is_following=u.id in following_ids,
            has_pending_request=False
        ))
    return results

@router.post("/follow/{target_user_id}")
def follow_student(
    target_user_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target_user = db.query(UserModel).filter(UserModel.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target student not found")

    existing = db.query(UserFollowModel).filter(
        UserFollowModel.follower_id == current_user.id,
        UserFollowModel.following_id == target_user_id
    ).first()

    if not existing:
        new_follow = UserFollowModel(
            id=f"f_{uuid.uuid4().hex[:8]}",
            follower_id=current_user.id,
            following_id=target_user_id,
            created_at=datetime.utcnow()
        )
        db.add(new_follow)
        
        # Update follower counts in MySQL
        me = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if me:
            me.following_count = (me.following_count or 0) + 1
        target_user.followers_count = (target_user.followers_count or 0) + 1
        db.commit()

    return {"status": "success", "message": f"Successfully followed {target_user.name}"}

@router.post("/unfollow/{target_user_id}")
def unfollow_student(
    target_user_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    existing = db.query(UserFollowModel).filter(
        UserFollowModel.follower_id == current_user.id,
        UserFollowModel.following_id == target_user_id
    ).first()

    if existing:
        db.delete(existing)
        me = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        target_user = db.query(UserModel).filter(UserModel.id == target_user_id).first()
        if me:
            me.following_count = max(0, (me.following_count or 1) - 1)
        if target_user:
            target_user.followers_count = max(0, (target_user.followers_count or 1) - 1)
        db.commit()

    return {"status": "success", "message": f"Unfollowed student {target_user_id}"}
