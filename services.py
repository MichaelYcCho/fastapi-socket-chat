from sqlalchemy.orm import Session
from connection_manager import ConnectionManager
from const import GROUP_EXCEED, USER_ALREADY_JOIN_GROUP

import models


def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, name: str) -> models.User:
    return db.query(models.User).filter(models.User.name == name).first()


def get_user_by_ip(db: Session, ip_address: str) -> models.User:
    return db.query(models.User).filter(models.User.ip_address == ip_address).first()


def create_user(db: Session, ip_address: str) -> models.User:
    db_user = models.User(ip_address=ip_address)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_group_member_id(db: Session, group_name: str) -> list[int]:
    group = db.query(models.Group).filter(models.Group.name == group_name).first()
    return [user.id for user in group.users]


def get_group_by_name(db: Session, name: str) -> models.Group:
    return db.query(models.Group).filter(models.Group.name == name).first()


def create_group(db: Session, group_name: str, user_id: int, manager) -> str:
    existing_group = (
        db.query(models.Group).filter(models.Group.name == group_name).first()
    )
    if existing_group:
        return "Group creation failed: Group name already exists."
    else:
        new_group = models.Group(name=group_name)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        add_user_to_group(db, user_id, group_name)
        return f"Group '{group_name}' created successfully."


def add_user_to_group(db: Session, user_id: int, group_name: str) -> str:
    group = db.query(models.Group).filter(models.Group.name == group_name).first()
    if not group:
        return "Group addition failed: Group not found."
    result = _add_user_to_group_logic(db, user_id, group)
    return result


def _add_user_to_group_logic(db: Session, user_id: int, group: models.Group) -> str:
    if group.user_count >= 100:
        return GROUP_EXCEED
    if any(user.id == user_id for user in group.users):
        return USER_ALREADY_JOIN_GROUP
    group.users.append(db.query(models.User).get(user_id))
    group.user_count += 1
    db.commit()
    return f"User '{user_id}' added to group '{group.name}'."


def handle_personal_message(
    db: Session, manager: ConnectionManager, user_id: str, message_data: dict
) -> None:
    if len(message_data["message"]) > 1000:
        return manager.send_personal_message(
            "Message length exceeds the limit of 1000 characters.", user_id
        )
    header = create_header(db, user_id, message_data["to"], models.MessageType.personal)
    create_message(db, header.id, True, message_data["message"])
    return manager.send_personal_message(message_data["message"], message_data["to"])


def handle_group_message(
    db: Session, manager: ConnectionManager, user_id: str, message_data: dict
) -> None:
    if len(message_data["message"]) > 1000:
        return manager.send_personal_message(
            "Message length exceeds the limit of 1000 characters.", user_id
        )
    group = get_group_by_name(db, message_data["group_name"])
    if not group:
        return manager.send_personal_message(
            "Group not found. Please create the group first.", user_id
        )
    header = create_header(db, user_id, group.id, models.MessageType.group)
    create_message(db, header.id, True, message_data["message"])
    group_member_id_list = get_group_member_id(db, message_data["group_name"])
    return manager.broadcast_to_group(
        message_data["message"], group_member_id_list, user_id
    )


def create_header(
    db: Session, from_id: int, to_id: int, type: models.MessageType
) -> models.Header:
    db_header = models.Header(from_id=from_id, to_id=to_id, type=type)
    db.add(db_header)
    db.commit()
    db.refresh(db_header)
    return db_header


def create_message(
    db: Session, header_id: int, is_from_sender: bool, content: str
) -> models.Message:
    db_message = models.Message(
        header_id=header_id, is_from_sender=is_from_sender, content=content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_headers(db: Session, user_id: int) -> list[models.Header]:
    return (
        db.query(models.Header)
        .filter((models.Header.from_id == user_id) | (models.Header.to_id == user_id))
        .all()
    )


def get_messages(db: Session, header_id: int) -> list[models.Message]:
    return db.query(models.Message).filter(models.Message.header_id == header_id).all()
