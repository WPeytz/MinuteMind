"""Database models defined with SQLModel."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Script(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    script_id: str = Field(index=True, unique=True)
    topic: str
    tone: str
    duration_minutes: int
    scenes: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str = Field(index=True, unique=True)
    script_id: str = Field(foreign_key="script.script_id")
    title: str
    storage_path: str
    status: str = Field(default="pending")
    thumbnail_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
