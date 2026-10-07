from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.coding import (
    CodingProblemResponse,
    CodeExecutionRequest,
    CodeExecutionResult,
)
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import CodingProblemModel, UserModel, SubmissionModel
from app.services.code_runner import code_runner
from datetime import datetime
import uuid

router = APIRouter(prefix="/coding", tags=["Coding Arena"])

@router.get("/problems", response_model=List[CodingProblemResponse])
def get_coding_problems(
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    query = db.query(CodingProblemModel)
    if difficulty:
        query = query.filter(CodingProblemModel.difficulty == difficulty)
    if topic:
        query = query.filter(CodingProblemModel.topic == topic)
    if search:
        query = query.filter(CodingProblemModel.title.ilike(f"%{search}%"))

    problems = query.all()
    return [CodingProblemResponse.model_validate(p, from_attributes=True) for p in problems]

@router.get("/problems/{problem_id}", response_model=CodingProblemResponse)
def get_coding_problem_detail(problem_id: str, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    problem = db.query(CodingProblemModel).filter(CodingProblemModel.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Coding problem not found")
    return CodingProblemResponse.model_validate(problem, from_attributes=True)

@router.post("/run", response_model=CodeExecutionResult)
def run_code_sample(req: CodeExecutionRequest, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    problem = db.query(CodingProblemModel).filter(CodingProblemModel.id == req.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    test_cases = problem.sample_test_cases or []
    if req.custom_input:
        test_cases = [{"input": req.custom_input, "expected_output": "", "is_hidden": False}]
        
    result = code_runner.run_code(
        language=req.language,
        code=req.code,
        test_cases=test_cases
    )
    return result

@router.post("/submit", response_model=CodeExecutionResult)
def submit_code_solution(
    req: CodeExecutionRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    problem = db.query(CodingProblemModel).filter(CodingProblemModel.id == req.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    all_test_cases = (problem.sample_test_cases or []) + (problem.hidden_test_cases or [])
    result = code_runner.run_code(
        language=req.language,
        code=req.code,
        test_cases=all_test_cases
    )
    
    # Update user points in MySQL if solved
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if result.status == "Accepted":
        problem.is_solved = True
        if db_user:
            db_user.coding_problems_solved = (db_user.coding_problems_solved or 0) + 1
            db_user.total_points = (db_user.total_points or 0) + result.points_awarded
            
    sub_id = f"sub_code_{uuid.uuid4().hex[:8]}"
    new_sub = SubmissionModel(
        id=sub_id,
        user_id=current_user.id,
        problem_id=req.problem_id,
        submission_type="code",
        code=req.code,
        language=req.language,
        status=result.status,
        passed_test_cases=result.passed_test_cases,
        total_test_cases=result.total_test_cases,
        execution_time_ms=result.execution_time_ms,
        memory_used_mb=result.memory_used_kb / 1024.0,
        score=float(result.points_awarded),
        submitted_at=datetime.utcnow()
    )
    db.add(new_sub)
    db.commit()
    
    return result
