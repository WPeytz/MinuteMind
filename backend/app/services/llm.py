"""Large language model helpers for script generation."""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from .. import models
from ..settings import get_settings
from ..utils import prompts


def _extract_json_block(raw: str) -> str:
    """Return the JSON object embedded in a raw LLM response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\\s*", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned.strip())
    cleaned = cleaned.strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("LLM response did not contain a JSON object")
    return match.group(0)


def _parse_script(raw: str, request: models.ScriptRequest) -> models.Script:
    payload = json.loads(_extract_json_block(raw))
    if "script" not in payload:
        raise ValueError("JSON payload missing 'script' root key")

    script_payload = payload["script"]
    script = models.Script(
        script_id=str(uuid4()),
        topic=script_payload.get("topic", request.topic),
        duration_minutes=script_payload.get("duration_minutes", request.duration_minutes),
        scenes=[models.ScriptScene.model_validate(scene) for scene in script_payload.get("scenes", [])],
        created_at=datetime.utcnow(),
    )
    if not script.scenes:
        raise ValueError("Parsed script contained no scenes")
    return script


def _fake_script(request: models.ScriptRequest) -> models.Script:
    """Offline fallback used during tests or when LLM is unavailable."""
    now = datetime.utcnow()
    scenes = [
        models.ScriptScene(
            scene_id="scene-1",
            title="Hook",
            visual="Animated focus timer counting down",
            narration="Picture your attention like a muscle. Let's warm it up with a one-minute focus sprint.",
            duration_seconds=20,
        ),
        models.ScriptScene(
            scene_id="scene-2",
            title="Core Idea",
            visual="Whiteboard sketches explaining the topic",
            narration=f"Here are the three essentials of {request.topic}: break work into sprints, remove distractions, and celebrate small wins.",
            duration_seconds=35,
        ),
        models.ScriptScene(
            scene_id="scene-3",
            title="Takeaway",
            visual="Calm background with checklist overlay",
            narration="Try a two-minute timer, mute notifications, and note a single win when you finish. Your brain loves quick victories!",
            duration_seconds=25,
        ),
    ]
    return models.Script(
        script_id=str(uuid4()),
        topic=request.topic,
        duration_minutes=request.duration_minutes,
        scenes=scenes,
        created_at=now,
    )


def _call_openai_llm(prompt: str) -> str:
    settings = get_settings()
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - dependency optional
        raise RuntimeError("openai package is required for live LLM calls") from exc

    if not settings.openai_api_key:  # pragma: no cover
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(  # type: ignore[attr-defined]
        model=settings.llm_model,
        input=[
            {"role": "system", "content": prompts.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    # openai>=1.3 returns aggregated text in output[0]
    if hasattr(response, "output"):  # pragma: no cover - exercised in integration only
        for item in response.output:  # type: ignore[attr-defined]
            content = getattr(item, "content", None)
            if not content:
                continue
            for block in content:
                if getattr(block, "type", "text") == "text":
                    return block.text  # type: ignore[return-value]
    # Fallback for azure/openai beta APIs
    if hasattr(response, "output_text"):
        return response.output_text  # type: ignore[return-value]
    raise RuntimeError("Unexpected response structure from OpenAI Responses API")


async def generate_script(request: models.ScriptRequest) -> models.Script:
    """Generate a structured script from the provided topic."""
    settings = get_settings()
    if settings.use_mock_llm:
        return _fake_script(request)

    prompt = prompts.build_script_prompt(request)

    if settings.openai_api_key:
        raw = await asyncio.to_thread(_call_openai_llm, prompt)
        try:
            return _parse_script(raw, request)
        except (ValueError, json.JSONDecodeError, ValidationError) as exc:
            raise RuntimeError("Failed to parse LLM script response") from exc

    return _fake_script(request)
