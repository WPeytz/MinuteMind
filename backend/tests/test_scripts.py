from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi.testclient import TestClient

from backend.app import models
from backend.app.main import app
from backend.app.services import llm, stitch


def test_generate_script_returns_mock_payload() -> None:
    request = models.ScriptRequest(topic="Deep focus", duration_minutes=5, tone="calm")
    script = asyncio.run(llm.generate_script(request))

    assert script.topic == "Deep focus"
    assert script.duration_minutes == 5
    assert len(script.scenes) >= 1
    assert all(scene.narration for scene in script.scenes)


def test_scripts_generate_endpoint_returns_audio() -> None:
    client = TestClient(app)
    response = client.post(
        "/scripts/generate",
        json={"topic": "Neuroplasticity", "duration_minutes": 4, "tone": "engaging"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "script" in payload
    assert "audio" in payload
    assert len(payload["audio"]) == len(payload["script"]["scenes"])
    assert payload["audio"][0]["audio_url"].startswith("http://test/media/")


def test_stitch_render_video_uses_mock_pipeline() -> None:
    script = models.Script(
        script_id="script-1",
        topic="Memory palace",
        duration_minutes=5,
        scenes=[
            models.ScriptScene(
                scene_id="scene-1",
                title="Intro",
                visual="Animated brain",
                narration="Imagine storing memories like rooms in a palace",
                duration_seconds=20,
            )
        ],
        created_at=datetime.utcnow(),
    )
    audio = [
        models.SceneAudio(
            scene_id="scene-1",
            audio_url="http://test/media/script-1-scene-1.mp3",
            duration_seconds=None,
        )
    ]
    metadata = asyncio.run(stitch.render_video(models.ScriptResponse(script=script, audio=audio)))

    assert metadata.status == "completed"
    assert metadata.storage_path is not None
    assert metadata.storage_path.startswith("http://test/media/")
