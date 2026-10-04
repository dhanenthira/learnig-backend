import asyncio
import json
import random
import string
from typing import Dict, List, Any, Optional
from fastapi import WebSocket
from datetime import datetime

class BattleManager:
    def __init__(self):
        # room_code -> Dict of room state
        self.rooms: Dict[str, Dict[str, Any]] = {}
        # room_code -> Dict[user_id, WebSocket]
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    def generate_room_code(self) -> str:
        while True:
            code = "CA-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if code not in self.rooms:
                return code

    def create_room(self, host_id: str, host_name: str, room_name: str, category: str, difficulty: str, question_count: int, duration_minutes: int, max_players: int, is_private: bool) -> Dict[str, Any]:
        room_code = self.generate_room_code()
        room = {
            "id": f"room_{room_code}",
            "room_code": room_code,
            "room_name": room_name,
            "category": category,
            "difficulty": difficulty,
            "question_count": question_count,
            "duration_minutes": duration_minutes,
            "max_players": max_players,
            "is_private": is_private,
            "status": "waiting", # waiting, in_progress, finished
            "host_id": host_id,
            "host_name": host_name,
            "created_at": datetime.utcnow(),
            "participants": [
                {
                    "user_id": host_id,
                    "name": host_name,
                    "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={host_name}",
                    "is_host": True,
                    "is_ready": True,
                    "score": 0,
                    "correct_answers": 0,
                    "current_question_index": 0,
                    "finished": False,
                    "finish_time_seconds": None
                }
            ],
            "questions": []
        }
        self.rooms[room_code] = room
        self.active_connections[room_code] = {}
        return room

    async def connect(self, room_code: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = {}
        self.active_connections[room_code][user_id] = websocket

    def disconnect(self, room_code: str, user_id: str):
        if room_code in self.active_connections and user_id in self.active_connections[room_code]:
            del self.active_connections[room_code][user_id]

    async def broadcast_to_room(self, room_code: str, message: Dict[str, Any]):
        if room_code in self.active_connections:
            dead_connections = []
            for user_id, ws in self.active_connections[room_code].items():
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.append(user_id)
            for user_id in dead_connections:
                del self.active_connections[room_code][user_id]

    def join_room(self, room_code: str, user_id: str, user_name: str) -> Optional[Dict[str, Any]]:
        room = self.rooms.get(room_code)
        if not room:
            return None
        if room["status"] != "waiting":
            return None
        
        # Check if already joined
        for p in room["participants"]:
            if p["user_id"] == user_id:
                return room

        if len(room["participants"]) >= room["max_players"]:
            return None

        participant = {
            "user_id": user_id,
            "name": user_name,
            "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_name}",
            "is_host": False,
            "is_ready": False,
            "score": 0,
            "correct_answers": 0,
            "current_question_index": 0,
            "finished": False,
            "finish_time_seconds": None
        }
        room["participants"].append(participant)
        return room

    def toggle_ready(self, room_code: str, user_id: str, ready: bool) -> Optional[Dict[str, Any]]:
        room = self.rooms.get(room_code)
        if not room:
            return None
        for p in room["participants"]:
            if p["user_id"] == user_id:
                p["is_ready"] = ready
                break
        return room

    def start_battle(self, room_code: str, host_id: str, questions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        room = self.rooms.get(room_code)
        if not room or room["host_id"] != host_id:
            return None
        room["status"] = "in_progress"
        room["questions"] = questions
        room["start_time"] = datetime.utcnow()
        return room

    def record_answer(self, room_code: str, user_id: str, question_index: int, is_correct: bool, time_taken_ms: int) -> Optional[Dict[str, Any]]:
        room = self.rooms.get(room_code)
        if not room:
            return None
        for p in room["participants"]:
            if p["user_id"] == user_id:
                p["current_question_index"] = question_index + 1
                if is_correct:
                    # Faster answers earn more points (100 base + speed bonus)
                    speed_bonus = max(0, 50 - int(time_taken_ms / 1000) * 5)
                    p["score"] += (100 + speed_bonus)
                    p["correct_answers"] += 1
                if p["current_question_index"] >= room["question_count"]:
                    p["finished"] = True
                break
        
        # Check if all finished
        if all(p.get("finished", False) for p in room["participants"]):
            room["status"] = "finished"

        return room

battle_manager = BattleManager()
