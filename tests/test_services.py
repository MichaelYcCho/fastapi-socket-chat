import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import services
from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()
    # test.db 파일을 제거
    if os.path.exists("./test.db"):
        os.remove("./test.db")


def test_create_user(db):
    user = services.create_user(db, "127.0.0.1")
    assert user.ip_address == "127.0.0.1"


def test_get_user_by_ip(db):
    user = services.get_user_by_ip(db, "127.0.0.1")
    assert user is not None
    assert user.ip_address == "127.0.0.1"


def test_create_group(db):
    response = services.create_group(db, "TestGroup", 1, None)
    assert response == "Group 'TestGroup' created successfully."


def test_add_user_to_group(db):
    user_id = 1
    group_name = "TestGroup"
    services.add_user_to_group(db, user_id, group_name)
    group = services.get_group_by_name(db, group_name)
    user = services.get_user(db, user_id)
    assert user in group.users


def test_handle_personal_message(db):
    from connection_manager import ConnectionManager

    manager = ConnectionManager()
    message_data = {"type": "PERSONAL_MESSAGE", "to": 2, "message": "Hello"}
    user_id = 1
    services.handle_personal_message(db, manager, str(user_id), message_data)

    # Header와 Message가 제대로 생성되었는지 확인
    headers = services.get_headers(db, user_id)
    assert len(headers) > 0
    header = headers[-1]
    messages = services.get_messages(db, header.id)
    assert len(messages) > 0
    message = messages[-1]
    assert message.content == "Hello"
    assert message.is_from_sender is True


def test_handle_group_message(db):
    from connection_manager import ConnectionManager

    manager = ConnectionManager()
    message_data = {
        "type": "GROUP_MESSAGE",
        "group_name": "TestGroup",
        "message": "Hello Group",
    }
    user_id = 1
    services.handle_group_message(db, manager, str(user_id), message_data)

    # Header와 Message가 제대로 생성되었는지 확인
    headers = services.get_headers(db, user_id)
    assert len(headers) > 0
    header = headers[-1]
    messages = services.get_messages(db, header.id)
    assert len(messages) > 0
    message = messages[-1]
    assert message.content == "Hello Group"
    assert message.is_from_sender is True
