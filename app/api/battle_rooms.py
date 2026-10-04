from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
from app.schemas.battle import (
    BattleRoomCreate,
    BattleRoomResponse,
    BattleResultResponse,
    BattleResultRank,
    BattleQuestionAnswer
)
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.services.battle_manager import battle_manager
from app.services.data_store import data_store

router = APIRouter(prefix="/battle", tags=["Multiplayer Battle Rooms"])

@router.get("/rooms", response_model=List[BattleRoomResponse])
def list_active_rooms():
    return [BattleRoomResponse(**r) for r in battle_manager.rooms.values() if not r.get("is_private", False)]

@router.post("/create", response_model=BattleRoomResponse)
def create_room(req: BattleRoomCreate, current_user: UserResponse = Depends(get_current_user)):
    room = battle_manager.create_room(
        host_id=current_user.id,
        host_name=current_user.name,
        room_name=req.room_name,
        category=req.category,
        difficulty=req.difficulty,
        question_count=req.question_count,
        duration_minutes=req.duration_minutes,
        max_players=req.max_players,
        is_private=req.is_private
    )
    return BattleRoomResponse(**room)

@router.post("/join/{room_code}", response_model=BattleRoomResponse)
def join_room(room_code: str, current_user: UserResponse = Depends(get_current_user)):
    room = battle_manager.join_room(
        room_code=room_code.upper().strip(),
        user_id=current_user.id,
        user_name=current_user.name
    )
    if not room:
        raise HTTPException(status_code=400, detail="Room not found or full/already started")
    return BattleRoomResponse(**room)

@router.get("/room/{room_code}", response_model=BattleRoomResponse)
def get_room_details(room_code: str):
    room = battle_manager.rooms.get(room_code.upper().strip())
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return BattleRoomResponse(**room)

@router.get("/result/{room_code}", response_model=BattleResultResponse)
def get_battle_result(room_code: str):
    room = battle_manager.rooms.get(room_code.upper().strip())
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    sorted_participants = sorted(room.get("participants", []), key=lambda x: x.get("score", 0), reverse=True)
    rankings = []
    
    for idx, p in enumerate(sorted_participants, start=1):
        q_count = room.get("question_count", 5)
        corr = p.get("correct_answers", 0)
        acc = round((corr / max(1, q_count)) * 100, 1)
        rankings.append(BattleResultRank(
            rank=idx,
            user_id=p["user_id"],
            name=p["name"],
            score=p.get("score", 0),
            correct_answers=corr,
            accuracy=acc,
            avg_response_time_ms=2800.0,
            is_winner=(idx == 1)
        ))
        
    winner = sorted_participants[0] if sorted_participants else {"name": "None", "avatar_url": ""}
    return BattleResultResponse(
        room_code=room_code,
        room_name=room.get("room_name", "Battle Room"),
        winner_name=winner["name"],
        winner_avatar=winner.get("avatar_url"),
        rankings=rankings,
        total_questions=room.get("question_count", 5)
    )

@router.websocket("/ws/{room_code}/{user_id}")
async def battle_websocket(websocket: WebSocket, room_code: str, user_id: str):
    code = room_code.upper().strip()
    await battle_manager.connect(code, user_id, websocket)
    try:
        # Notify others
        await battle_manager.broadcast_to_room(code, {
            "event": "user_connected",
            "user_id": user_id,
            "room": battle_manager.rooms.get(code)
        })
        
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            
            if event == "toggle_ready":
                ready_state = data.get("ready", True)
                room = battle_manager.toggle_ready(code, user_id, ready_state)
                await battle_manager.broadcast_to_room(code, {
                    "event": "room_state_update",
                    "room": room
                })
                
            elif event == "start_match":
                questions = list(data_store.questions.values())[:5]
                room = battle_manager.start_battle(code, user_id, questions)
                await battle_manager.broadcast_to_room(code, {
                    "event": "match_started",
                    "room": room,
                    "questions": questions
                })
                
            elif event == "submit_answer":
                q_idx = data.get("question_index", 0)
                is_corr = data.get("is_correct", False)
                t_ms = data.get("time_taken_ms", 3000)
                room = battle_manager.record_answer(code, user_id, q_idx, is_corr, t_ms)
                await battle_manager.broadcast_to_room(code, {
                    "event": "score_update",
                    "room": room
                })
                
    except WebSocketDisconnect:
        battle_manager.disconnect(code, user_id)
        await battle_manager.broadcast_to_room(code, {
            "event": "user_disconnected",
            "user_id": user_id
        })
