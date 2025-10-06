"""Prompt building utilities for LLM calls."""
from __future__ import annotations

from textwrap import dedent

from .. import models

SYSTEM_PROMPT = dedent(
    """
    You are an educational video script writer. Always respond with a single JSON object that
    conforms to this JSON schema:

    {
      "script": {
        "topic": string,
        "duration_minutes": integer,
        "scenes": [
          {
            "scene_id": string,
            "title": string,
            "visual": string,
            "narration": string,
            "duration_seconds": integer
          }, ...
        ]
      }
    }

    Do not include any markdown fencing or additional commentary.
    """
)


def build_script_prompt(request: models.ScriptRequest) -> str:
    """Create a detailed prompt to produce a structured script."""
    return dedent(
        f"""
        Create a concise explainer video script about "{request.topic}".
        Target duration: {request.duration_minutes} minutes.
        Tone: {request.tone}.
        Use 3-5 scenes with meaningful visuals and crisp narration.
        Each narration block must stay under 90 words.
        """
    ).strip()
