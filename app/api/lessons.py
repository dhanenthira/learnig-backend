from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.lesson import ModuleSummary, LessonDetail, LessonProgressUpdate
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store

router = APIRouter(prefix="/lessons", tags=["Learning Module"])

@router.get("/modules", response_model=List[ModuleSummary])
def get_all_modules():
    return [ModuleSummary(**m) for m in data_store.modules.values()]

@router.get("/{lesson_id}", response_model=LessonDetail)
def get_lesson_detail(lesson_id: str):
    lesson = data_store.lessons.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonDetail(**lesson)

@router.post("/progress")
def update_lesson_progress(progress: LessonProgressUpdate, current_user: UserResponse = Depends(get_current_user)):
    lesson = data_store.lessons.get(progress.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    lesson["is_completed"] = progress.completed
    
    # Update user points if newly completed
    if progress.completed:
        user = data_store.users.get(current_user.id)
        if user:
            user["total_points"] = user.get("total_points", 0) + 15
            
    return {"status": "success", "lesson_id": progress.lesson_id, "is_completed": progress.completed}
