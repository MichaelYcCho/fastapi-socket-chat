from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
from services import (
    get_user_by_ip,
    get_user_by_name,
    create_user,
    handle_personal_message,
    handle_group_message,
    create_group,
    add_user_to_group,
)
from database import SessionLocal
from connection_manager import manager
from const import (
    PERSONAL_MESSAGE,
    GROUP_MESSAGE,
    GROUP_CREATE,
    GROUP_ADD_USER,
    USER_STATUS,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def websocket_endpoint(websocket: WebSocket):
    db = next(get_db())
    try:
        # 실제 서비스에서는 주석 처리된 부분을 사용
        ip_address = websocket.client.host
        # ip_address = "159.12.3.1"
        # print("ip_address", ip_address)

        user = get_user_by_ip(db, ip_address)
        if not user:
            user = create_user(db, ip_address)
        user_id = str(user.id)
        print("user_id", user_id)

        await manager.connect(websocket, user_id)
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                if message_data["type"] == PERSONAL_MESSAGE:
                    await handle_personal_message(db, manager, user_id, message_data)
                elif message_data["type"] == GROUP_MESSAGE:
                    await handle_group_message(db, manager, user_id, message_data)
                elif message_data["type"] == GROUP_CREATE:
                    response = create_group(
                        db, message_data["group_name"], user_id, manager
                    )
                    await manager.send_personal_message(response, user_id)
                elif message_data["type"] == GROUP_ADD_USER:
                    response = add_user_to_group(
                        db, user_id, message_data["group_name"]
                    )
                    await manager.send_personal_message(response, user_id)
                elif message_data["type"] == USER_STATUS:
                    online_users = manager.get_online_users()
                    response = {"type": USER_STATUS, "online_users": online_users}
                    await websocket.send_text(json.dumps(response))
        except WebSocketDisconnect:
            manager.disconnect(user_id)
    finally:
        db.close()


def get_online_users_api():
    online_users = manager.get_online_users()
    return {"online_users": online_users}
