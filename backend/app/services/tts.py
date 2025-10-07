"""Text-to-speech helpers."""
from __future__ import annotations

import asyncio
import io
import wave
import struct
import os

from .. import models
from ..settings import get_settings
from . import storage


def _fake_audio_payload(text: str) -> bytes:
    """Return a small valid WAV payload (1s silence), so ffmpeg/moviepy can read it in tests."""
    sample_rate = 22050  # Hz
    duration_s = 1.0
    n_samples = int(sample_rate * duration_s)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)          # mono
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(sample_rate)
        silence_frame = struct.pack("<h", 0)
        wf.writeframes(silence_frame * n_samples)
    return buf.getvalue()


def _render_with_openai_wav(text: str) -> bytes:
    """Return WAV/PCM bytes from OpenAI TTS API."""
    settings = get_settings()
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - dependency optional
        raise RuntimeError("openai package is required for live TTS") from exc

    if not settings.openai_api_key:  # pragma: no cover
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.openai_api_key)

    # NOTE:
    # The current OpenAI Python SDK `audio.speech.create` does not accept a `format=` kwarg.
    # We therefore omit it and read raw bytes from the response.
    # If the SDK is streaming-enabled, `.read()` is available; otherwise fall back to `.content` or bytes.
    response = client.audio.speech.create(  # type: ignore[attr-defined]
        model=settings.tts_model,
        voice=settings.tts_voice,
        input=text,
    )

    # Prefer stream-like `.read()`; else use `.content` or raw bytes.
    if hasattr(response, "read"):  # pragma: no cover - integrates with real API
        return response.read()  # type: ignore[return-value]
    if hasattr(response, "content") and isinstance(response.content, (bytes, bytearray)):  # pragma: no cover
        return bytes(response.content)
    if isinstance(response, (bytes, bytearray)):  # pragma: no cover
        return bytes(response)

    raise RuntimeError("Unexpected response type from OpenAI TTS API")


async def _synthesize_scene_audio(scene: models.ScriptScene, script_id: str, settings) -> models.SceneAudio:
    """Generate audio for a single scene."""
    if settings.use_mock_tts or not settings.openai_api_key:
        audio_bytes = _fake_audio_payload(scene.narration)
        suffix = ".wav"
    else:  # pragma: no cover - requires live API
        audio_bytes = await asyncio.to_thread(_render_with_openai_wav, scene.narration)
        suffix = ".mp3"
    # Persist using a suffix that matches the underlying payload so MoviePy can decode it.
    stored = await storage.save_bytes(
        name=f"{script_id}-{scene.scene_id}",
        payload=audio_bytes,
        suffix=suffix,
    )
    return models.SceneAudio(
        scene_id=scene.scene_id,
        audio_url=stored.url,
        duration_seconds=None,
    )


async def synthesize_voice(script: models.Script) -> list[models.SceneAudio]:
    """Convert script text to audio bytes per scene."""
    settings = get_settings()
    # Generate all audio in parallel for faster processing
    tasks = [_synthesize_scene_audio(scene, script.script_id, settings) for scene in script.scenes]
    scene_audios = await asyncio.gather(*tasks)
    return list(scene_audios)
