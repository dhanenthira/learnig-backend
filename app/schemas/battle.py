from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class BattleRoomStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class BattleParticipant(BaseModel):
    user_id: str
    name: str
    avatar_url: Optional[str] = None
    is_host: bool = False
    is_ready: bool = False
    score: int = 0
    correct_answers: int = 0
    current_question_index: int = 0
    finished: bool = False
    finish_time_seconds: Optional[float] = None

class BattleRoomCreate(BaseModel):
    room_name: str
    category: str # aptitude, technical, coding
    difficulty: str # easy, medium, hard
    question_count: int = 5
    duration_minutes: int = 5
    max_players: int = 4
    is_private: bool = False

class BattleRoomResponse(BaseModel):
    id: str
    room_code: str
    room_name: str
    category: str
    difficulty: str
    question_count: int
    duration_minutes: int
    max_players: int
    is_private: bool
    status: BattleRoomStatus
    host_id: str
    host_name: str
    created_at: datetime
    participants: List[BattleParticipant] = []

class BattleQuestionAnswer(BaseModel):
    room_code: str
    question_index: int
    selected_option: str
    time_taken_ms: int

class BattleResultRank(BaseModel):
    rank: int
    user_id: str
    name: str
    score: int
    correct_answers: int
    accuracy: float
    avg_response_time_ms: float
    is_winner: bool

class BattleResultResponse(BaseModel):
    room_code: str
    room_name: str
    winner_name: str
    winner_avatar: Optional[str] = None
    rankings: List[BattleResultRank] = []
    total_questions: int
