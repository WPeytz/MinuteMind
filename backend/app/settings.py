"""Application settings pulled from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    llm_model: str
    tts_model: str
    tts_voice: str
    storage_base_url: str
    media_root: str
    use_mock_llm: bool
    use_mock_tts: bool
    use_mock_video: bool


def _as_bool(value: str | None) -> bool:
    return value == "1"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        llm_model=os.getenv("MINUTEMIND_LLM_MODEL", "gpt-4o-mini"),
        tts_model=os.getenv("MINUTEMIND_TTS_MODEL", "gpt-4o-mini-tts"),
        tts_voice=os.getenv("MINUTEMIND_TTS_VOICE", "alloy"),
        storage_base_url=os.getenv("MINUTEMIND_STORAGE_BASE", "http://localhost:8000/media"),
        media_root=os.getenv("MINUTEMIND_MEDIA_ROOT", "./tmp"),
        use_mock_llm=_as_bool(os.getenv("MINUTEMIND_FAKE_LLM")),
        use_mock_tts=_as_bool(os.getenv("MINUTEMIND_FAKE_TTS")),
        use_mock_video=_as_bool(os.getenv("MINUTEMIND_FAKE_VIDEO")),
    )
