from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Text, Index,
    JSON, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Meal(Base):
    """Meals table - stores all user meals"""
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(50), nullable=False, index=True)
    dish = Column(String(255), nullable=False)
    grams = Column(Integer, nullable=False)
    kcal = Column(Integer, nullable=False)
    prot = Column(Integer, nullable=False)
    fat = Column(Integer, nullable=False)
    carb = Column(Integer, nullable=False)
    eaten_at = Column(DateTime, nullable=False, index=True)
    deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_chat_eaten', 'chat_id', 'eaten_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'dish': self.dish,
            'grams': self.grams,
            'kcal': self.kcal,
            'prot': self.prot,
            'fat': self.fat,
            'carb': self.carb,
            'eaten_at': self.eaten_at.isoformat() if self.eaten_at else None,
            'deleted': self.deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MealDraft(Base):
    """Meals draft table - temporary storage for FSM states"""
    __tablename__ = "meals_draft"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(50), nullable=False)
    message_id = Column(Integer, nullable=False)
    photo_file_id = Column(String(255))
    candidates = Column(JSON)  # Array of dish candidates from Vision API
    grams_pred = Column(Integer)  # Predicted grams
    chosen_name = Column(String(255))
    status = Column(String(50), nullable=False)  # await_dish, await_alt, await_weight, done
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('chat_id', 'message_id', name='uq_chat_message'),
        Index('idx_chat_status', 'chat_id', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'message_id': self.message_id,
            'photo_file_id': self.photo_file_id,
            'candidates': self.candidates,
            'grams_pred': self.grams_pred,
            'chosen_name': self.chosen_name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Digest(Base):
    """Daily digests table"""
    __tablename__ = "digest"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(50), nullable=False)
    for_date = Column(Date, nullable=False)
    kcal = Column(Integer, nullable=False)
    prot = Column(Integer, nullable=False)
    fat = Column(Integer, nullable=False)
    carb = Column(Integer, nullable=False)
    meals_json = Column(JSON)  # Array of meals for the day
    summary_md = Column(Text)  # Markdown summary from GPT
    msg_id = Column(Integer)  # Telegram message ID
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('chat_id', 'for_date', name='uq_chat_date'),
        Index('idx_chat_date', 'chat_id', 'for_date'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'for_date': self.for_date.isoformat() if self.for_date else None,
            'kcal': self.kcal,
            'prot': self.prot,
            'fat': self.fat,
            'carb': self.carb,
            'meals_json': self.meals_json,
            'summary_md': self.summary_md,
            'msg_id': self.msg_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatLog(Base):
    """Chat logs table - stores AI consultant conversation history"""
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(50), nullable=False)
    session_id = Column(String(100))
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)

    __table_args__ = (
        Index('idx_chat_session', 'chat_id', 'session_id'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'username': self.username,
            'first_name': self.first_name,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
