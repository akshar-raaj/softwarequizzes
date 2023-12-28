from typing import List
from typing import Optional
import enum
from datetime import datetime

from sqlalchemy import DateTime, Text, ForeignKey, func, Enum, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from enums import DifficultyLevel


class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    snippet: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    subdomain: Mapped[str] = mapped_column(String(20))
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[enum.Enum] = mapped_column(Enum(DifficultyLevel))
    choices: Mapped[List["Choice"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class Choice(Base):
    __tablename__ = 'choices'

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_answer: Mapped[bool]
    question: Mapped["Question"] = relationship(back_populates="choices")


class User(Base):
    __tablename__ = "auth_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"User: {self.email}"


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    choice_id: Mapped[int] = mapped_column(ForeignKey("choices.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
