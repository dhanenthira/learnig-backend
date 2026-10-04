from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.friend import FriendProfile, FriendRequestAction
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store

router = APIRouter(prefix="/friends", tags=["Friends & Community"])

@router.get("/list", response_model=List[FriendProfile])
def get_friends_list(current_user: UserResponse = Depends(get_current_user)):
    following_ids = data_store.follows.get(current_user.id, [])
    friends = []
    for u_id in following_ids:
        u = data_store.users.get(u_id)
        if u:
            friends.append(FriendProfile(
                user_id=u["id"],
                student_id=u["student_id"],
                name=u["name"],
                email=u["email"],
                college_name=u.get("college_name"),
                department=u.get("department"),
                avatar_url=u.get("avatar_url"),
                bio=u.get("bio", ""),
                problems_solved=u.get("problems_solved", 0),
                accuracy=u.get("overall_accuracy", 0.0),
                streak_days=u.get("streak_days", 0),
                battles_won=u.get("battles_won", 0),
                is_following=True,
                has_pending_request=False
            ))
    return friends

@router.get("/search", response_model=List[FriendProfile])
def search_students(query: str = Query(..., min_length=1), current_user: UserResponse = Depends(get_current_user)):
    q = query.lower()
    results = []
    following_ids = set(data_store.follows.get(current_user.id, []))
    
    for u in data_store.users.values():
        if u["id"] == current_user.id:
            continue
        if q in u["name"].lower() or q in u["student_id"].lower() or q in u["email"].lower():
            results.append(FriendProfile(
                user_id=u["id"],
                student_id=u["student_id"],
                name=u["name"],
                email=u["email"],
                college_name=u.get("college_name"),
                department=u.get("department"),
                avatar_url=u.get("avatar_url"),
                bio=u.get("bio", ""),
                problems_solved=u.get("problems_solved", 0),
                accuracy=u.get("overall_accuracy", 0.0),
                streak_days=u.get("streak_days", 0),
                battles_won=u.get("battles_won", 0),
                is_following=u["id"] in following_ids,
                has_pending_request=False
            ))
    return results

@router.post("/follow")
def follow_user(req: FriendRequestAction, current_user: UserResponse = Depends(get_current_user)):
    target_id = req.target_user_id
    if target_id not in data_store.users:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if current_user.id not in data_store.follows:
        data_store.follows[current_user.id] = []
        
    if target_id not in data_store.follows[current_user.id]:
        data_store.follows[current_user.id].append(target_id)
        # update follower counts
        target = data_store.users[target_id]
        target["followers_count"] = target.get("followers_count", 0) + 1
        
        user = data_store.users[current_user.id]
        user["following_count"] = user.get("following_count", 0) + 1
        
    return {"status": "success", "message": "Followed student successfully"}

@router.post("/unfollow")
def unfollow_user(req: FriendRequestAction, current_user: UserResponse = Depends(get_current_user)):
    target_id = req.target_user_id
    if current_user.id in data_store.follows and target_id in data_store.follows[current_user.id]:
        data_store.follows[current_user.id].remove(target_id)
        
        target = data_store.users.get(target_id)
        if target:
            target["followers_count"] = max(0, target.get("followers_count", 1) - 1)
            
        user = data_store.users.get(current_user.id)
        if user:
            user["following_count"] = max(0, user.get("following_count", 1) - 1)
            
    return {"status": "success", "message": "Unfollowed student"}
