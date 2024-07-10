from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    Boolean,
    Table,
    Text,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

group_user_association = Table(
    "group_user_relations",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("groups.id")),
    UniqueConstraint("user_id", "group_id", name="unique_user_group"),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=True)
    ip_address = Column(String, index=True)
    is_online = Column(Boolean, default=True)
    groups = relationship(
        "Group", secondary=group_user_association, back_populates="users"
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    user_count = Column(Integer, default=0)
    users = relationship(
        "User", secondary=group_user_association, back_populates="groups"
    )


class MessageType(enum.Enum):
    personal = "personal"
    group = "group"


class Header(Base):
    __tablename__ = "headers"

    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, ForeignKey("users.id"))
    to_id = Column(Integer)
    status = Column(Enum(MessageType))
    time = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    type = Column(Enum(MessageType))
    from_user = relationship("User", foreign_keys=[from_id])


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    header_id = Column(Integer, ForeignKey("headers.id"))
    is_from_sender = Column(Boolean)
    content = Column(Text)
    time = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    header = relationship("Header", back_populates="messages")


Header.messages = relationship("Message", order_by=Message.id, back_populates="header")
