"""Pydantic models for request/response payloads."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScriptRequest(BaseModel):
    topic: str = Field(..., description="High-level topic to cover")
    duration_minutes: int = Field(1, ge=1, le=30)
    tone: str = Field("engaging", description="Overall narration tone")


class ScriptScene(BaseModel):
    scene_id: str = Field(..., description="Client-side stable identifier")
    title: str = Field(..., description="Scene heading the viewer sees")
    visual: str = Field(..., description="Brief description of on-screen visuals")
    narration: str = Field(..., description="Narration text for TTS")
    duration_seconds: int = Field(20, ge=5, le=120)


class Script(BaseModel):
    script_id: str
    topic: str
    duration_minutes: int
    scenes: list[ScriptScene]
    created_at: datetime


class SceneAudio(BaseModel):
    scene_id: str
    audio_url: str
    duration_seconds: Optional[float] = None


class SceneImage(BaseModel):
    scene_id: str
    image_url: str


class ScriptResponse(BaseModel):
    script: Script
    audio: list[SceneAudio]
    images: list[SceneImage] = []


class VideoMetadata(BaseModel):
    video_id: str
    script_id: str
    title: str
    status: str
    created_at: datetime
    storage_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
