from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.coding import (
    CodingProblemResponse,
    CodeExecutionRequest,
    CodeExecutionResult,
    TestCase
)
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.data_store import data_store
from app.services.code_runner import code_runner
from datetime import datetime
import uuid

router = APIRouter(prefix="/coding", tags=["Coding Arena"])

@router.get("/problems", response_model=List[CodingProblemResponse])
def get_coding_problems(
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    search: Optional[str] = None
):
    results = []
    for p in data_store.coding_problems.values():
        if difficulty and p.get("difficulty") != difficulty:
            continue
        if topic and p.get("topic") != topic:
            continue
        if search and search.lower() not in p.get("title", "").lower():
            continue
        results.append(CodingProblemResponse(**p))
    return results

@router.get("/problems/{problem_id}", response_model=CodingProblemResponse)
def get_coding_problem_detail(problem_id: str):
    problem = data_store.coding_problems.get(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Coding problem not found")
    return CodingProblemResponse(**problem)

@router.post("/run", response_model=CodeExecutionResult)
def run_code_sample(req: CodeExecutionRequest):
    problem = data_store.coding_problems.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    test_cases = problem.get("sample_test_cases", [])
    if req.custom_input:
        test_cases = [{"input": req.custom_input, "expected_output": "", "is_hidden": False}]
        
    result = code_runner.run_code(
        language=req.language,
        code=req.code,
        test_cases=test_cases
    )
    return result

@router.post("/submit", response_model=CodeExecutionResult)
def submit_code_solution(req: CodeExecutionRequest, current_user: UserResponse = Depends(get_current_user)):
    problem = data_store.coding_problems.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    all_test_cases = problem.get("sample_test_cases", []) + problem.get("hidden_test_cases", [])
    result = code_runner.run_code(
        language=req.language,
        code=req.code,
        test_cases=all_test_cases
    )
    
    if result.status == "Accepted":
        problem["is_solved"] = True
        user = data_store.users.get(current_user.id)
        if user:
            user["coding_problems_solved"] = user.get("coding_problems_solved", 0) + 1
            user["total_points"] = user.get("total_points", 0) + result.points_awarded
            
    sub_id = f"sub_code_{uuid.uuid4().hex[:8]}"
    data_store.code_submissions[sub_id] = {
        "id": sub_id,
        "user_id": current_user.id,
        "problem_id": req.problem_id,
        "language": req.language,
        "status": result.status,
        "passed_cases": result.passed_test_cases,
        "total_cases": result.total_test_cases,
        "time_ms": result.execution_time_ms,
        "submitted_at": datetime.utcnow()
    }
    
    return result
