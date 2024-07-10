from typing import Dict, List
from fastapi import WebSocket

from const import OFFLINE, ONLINE
from models import User


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.groups: Dict[str, List[str]] = {}
        self.user_status: Dict[str, str] = {}  # ("ONLINE" / "OFFLINE")

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_status[user_id] = ONLINE

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        self.user_status[user_id] = OFFLINE

    async def send_personal_message(self, message: str, user_id: str):
        connection = self.active_connections.get(user_id)
        if connection:
            await connection.send_text(message)

    async def broadcast_to_group(
        self, message: str, group_members: List[User], sender: str
    ):
        for user_id in group_members:
            await self.send_personal_message(message, str(user_id))

    def get_online_users(self):
        return [
            user_id for user_id, status in self.user_status.items() if status == ONLINE
        ]


manager = ConnectionManager()
