from datetime import datetime, timezone
from .database import db
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    user_info_id = Column(UUID(as_uuid=True), ForeignKey("user_info.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("UserInfo", back_populates="sessions")

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_info_id': self.user_info_id,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id"), nullable=False)
    sender = Column(String(10), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'sender': self.sender,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

class UserInfo(db.Model):
    __tablename__ = 'user_info'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    country = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    sessions = relationship("ChatSession", back_populates="user")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'country': self.country,
            'created_at': self.created_at.isoformat()
        }

class FAQIntent(db.Model):
    __tablename__ = 'faq_intents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intent_name = Column(String(100), nullable=False, unique=True)

    training_phrases = Column(JSON, nullable=False)

    response_text = Column(Text, nullable=False)
    response_type = Column(String(50), default="text")

    topic = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)

    source = Column(String(50), default="manual")
    language = Column(String(10), default="en")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'intent_name': self.intent_name,
            'training_phrases': self.training_phrases,
            'response_text': self.response_text,
            'response_type': self.response_type,
            'topic': self.topic,
            'tags': self.tags,
            'source': self.source,
            'language': self.language,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'topic': self.topic,
            'created_at': self.created_at.isoformat()
        }
