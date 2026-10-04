from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from app.schemas.question import DifficultyEnum

class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    explanation: Optional[str] = ""

class StarterCode(BaseModel):
    language: str # python, javascript, cpp, java, c
    code: str

class CodingProblemBase(BaseModel):
    title: str
    slug: str
    difficulty: DifficultyEnum
    topic: str
    description: str
    constraints: List[str] = []
    examples: List[Dict[str, Any]] = []
    input_format: str
    output_format: str
    hints: List[str] = []
    time_limit_seconds: float = 2.0
    memory_limit_mb: int = 128
    starter_codes: List[StarterCode] = []
    tags: List[str] = []

class CodingProblemResponse(CodingProblemBase):
    id: str
    sample_test_cases: List[TestCase] = []
    is_solved: bool = False
    total_submissions: int = 0
    acceptance_rate: float = 0.0

class CodeExecutionRequest(BaseModel):
    problem_id: str
    language: str
    code: str
    custom_input: Optional[str] = None

class TestCaseEvaluation(BaseModel):
    test_case_number: int
    is_hidden: bool
    status: str # Passed, Failed, Time Limit Exceeded, Runtime Error
    input: Optional[str] = None
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0

class CodeExecutionResult(BaseModel):
    status: str # Accepted, Wrong Answer, Compilation Error, Runtime Error, Time Limit Exceeded
    total_test_cases: int
    passed_test_cases: int
    execution_time_ms: float
    memory_used_kb: float
    evaluations: List[TestCaseEvaluation] = []
    stdout: Optional[str] = ""
    stderr: Optional[str] = ""
    points_awarded: int = 0
