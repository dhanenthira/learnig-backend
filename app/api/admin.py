from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.schemas.question import QuestionCreate, QuestionAdminResponse
from app.schemas.coding import CodingProblemResponse
from app.schemas.test import AssessmentTest
from app.api.auth import get_current_admin_user
from app.core.database import get_db
from app.models.sql_models import UserModel, QuestionModel, CodingProblemModel, SubmissionModel, AssessmentTestModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get("/dashboard")
def get_admin_dashboard(
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    students = db.query(UserModel).filter(UserModel.role == "student").all()
    active_students_count = db.query(UserModel).filter(UserModel.role == "student", UserModel.is_active == True).count()
    aptitude_count = db.query(QuestionModel).filter(QuestionModel.category == "aptitude").count()
    technical_count = db.query(QuestionModel).filter(QuestionModel.category == "technical").count()
    coding_count = db.query(CodingProblemModel).count()
    submissions_count = db.query(SubmissionModel).count()
    
    total_submissions = sum(u.questions_solved or 0 for u in students) + submissions_count

    # Calculate average accuracy from students
    avg_accuracy = 0.0
    if students:
        acc_list = [s.overall_accuracy for s in students if s.overall_accuracy is not None]
        avg_accuracy = round(sum(acc_list) / len(acc_list), 1) if acc_list else 0.0

    recent_students = [UserResponse.model_validate(u, from_attributes=True) for u in students[:5]]

    # Get recent submissions strictly from DB (no fake data)
    recent_subs = db.query(SubmissionModel).order_by(SubmissionModel.submitted_at.desc()).limit(10).all()
    recent_submissions_list = []
    for s in recent_subs:
        sub_user = db.query(UserModel).filter(UserModel.id == s.user_id).first()
        recent_submissions_list.append({
            "id": s.id,
            "student_name": sub_user.name if sub_user else "Student",
            "student_id": sub_user.student_id if sub_user else s.user_id,
            "problem": s.problem_id,
            "status": s.status,
            "time": s.submitted_at.strftime("%H:%M") if s.submitted_at else "Recently"
        })

    return {
        "analytics": {
            "total_students": len(students),
            "active_students": active_students_count,
            "published_questions": aptitude_count + technical_count + coding_count,
            "total_submissions": total_submissions,
            "accuracy_rate": avg_accuracy
        },
        "recent_students": recent_students,
        "category_performance": [
            {"category": "Aptitude", "count": aptitude_count},
            {"category": "Technical", "count": technical_count},
            {"category": "Coding Arena", "count": coding_count}
        ],
        "recent_submissions": recent_submissions_list
    }

@router.get("/students", response_model=List[UserResponse])
def get_all_students(
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    students = db.query(UserModel).filter(UserModel.role == "student").all()
    return [UserResponse.model_validate(u, from_attributes=True) for u in students]

@router.patch("/students/{user_id}/status")
def toggle_student_status(
    user_id: str,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    student = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.is_active = not student.is_active
    db.commit()
    db.refresh(student)
    return {"status": "success", "is_active": student.is_active}

@router.post("/questions", response_model=QuestionAdminResponse)
def create_question(
    q_in: QuestionCreate,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    q_id = f"q_{uuid.uuid4().hex[:8]}"
    new_q = QuestionModel(
        id=q_id,
        title=q_in.title,
        content=q_in.content,
        category=q_in.category.value if hasattr(q_in.category, "value") else str(q_in.category).lower(),
        topic=q_in.topic,
        difficulty=q_in.difficulty.value if hasattr(q_in.difficulty, "value") else str(q_in.difficulty).lower(),
        question_type=q_in.question_type.value if hasattr(q_in.question_type, "value") else str(q_in.question_type),
        options=q_in.options,
        correct_answer=q_in.correct_answer,
        explanation=q_in.explanation or "",
        marks=q_in.marks,
        tags=q_in.tags or [],
        created_at=datetime.utcnow()
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return QuestionAdminResponse.model_validate(new_q, from_attributes=True)

@router.get("/questions", response_model=List[QuestionAdminResponse])
def get_admin_questions(
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    questions = db.query(QuestionModel).order_by(QuestionModel.created_at.desc()).all()
    return [QuestionAdminResponse.model_validate(q, from_attributes=True) for q in questions]

@router.delete("/questions/{question_id}")
def delete_question(
    question_id: str,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    q = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"status": "success", "message": f"Question {question_id} deleted successfully"}

# Coding Problem Endpoints for Admin
@router.post("/coding", response_model=CodingProblemResponse)
def create_coding_problem(
    payload: Dict[str, Any],
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    cp_id = f"cp_{uuid.uuid4().hex[:8]}"
    title = payload.get("title", "Untitled Problem")
    slug = payload.get("slug") or f"{title.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
    
    new_cp = CodingProblemModel(
        id=cp_id,
        title=title,
        slug=slug,
        difficulty=payload.get("difficulty", "Medium"),
        topic=payload.get("topic", "General"),
        description=payload.get("description", title),
        time_limit_seconds=float(payload.get("time_limit_seconds", 1.0)),
        memory_limit_mb=int(payload.get("memory_limit_mb", 256)),
        sample_test_cases=payload.get("sample_test_cases", []),
        hidden_test_cases=payload.get("hidden_test_cases", []),
        created_at=datetime.utcnow()
    )
    db.add(new_cp)
    db.commit()
    db.refresh(new_cp)
    return CodingProblemResponse.model_validate(new_cp, from_attributes=True)

@router.delete("/coding/{problem_id}")
def delete_coding_problem(
    problem_id: str,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    cp = db.query(CodingProblemModel).filter(CodingProblemModel.id == problem_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Coding problem not found")
    db.delete(cp)
    db.commit()
    return {"status": "success", "message": f"Coding problem {problem_id} deleted successfully"}

# Assessment Test Endpoints for Admin
@router.post("/tests", response_model=AssessmentTest)
def create_assessment_test(
    payload: Dict[str, Any],
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    t_id = f"test_{uuid.uuid4().hex[:8]}"
    new_t = AssessmentTestModel(
        id=t_id,
        title=payload.get("title", "Untitled Assessment"),
        description=payload.get("description", ""),
        category=payload.get("category", "mixed"),
        difficulty=payload.get("difficulty", "medium"),
        duration_minutes=int(payload.get("duration_minutes", 60)),
        total_marks=int(payload.get("total_marks", 100)),
        total_questions=int(payload.get("total_questions", 10)),
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        status=payload.get("status", "active"),
        question_ids=payload.get("question_ids", []),
        created_at=datetime.utcnow()
    )
    db.add(new_t)
    db.commit()
    db.refresh(new_t)
    return AssessmentTest.model_validate(new_t, from_attributes=True)

@router.delete("/tests/{test_id}")
def delete_assessment_test(
    test_id: str,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    t = db.query(AssessmentTestModel).filter(AssessmentTestModel.id == test_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Assessment not found")
    db.delete(t)
    db.commit()
    return {"status": "success", "message": f"Assessment {test_id} deleted successfully"}
