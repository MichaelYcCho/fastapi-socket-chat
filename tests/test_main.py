import pytest
from fastapi.testclient import TestClient
from const import USER_STATUS
from main import app

client = TestClient(app)


def test_get_online_users():
    response = client.get("/api/online-users")
    assert response.status_code == 200
    assert "online_users" in response.json()


@pytest.mark.asyncio
async def test_websocket_chat():
    async with client.websocket_connect("/ws/chat") as websocket:
        data = {"type": USER_STATUS}
        await websocket.send_json(data)
        response = await websocket.receive_json()
        assert response["type"] == USER_STATUS
        assert "online_users" in response
