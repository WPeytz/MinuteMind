from __future__ import annotations

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.settings import get_settings


@pytest.fixture(autouse=True)
def configure_env(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    monkeypatch.setenv("MINUTEMIND_FAKE_LLM", "1")
    monkeypatch.setenv("MINUTEMIND_FAKE_TTS", "1")
    monkeypatch.setenv("MINUTEMIND_FAKE_VIDEO", "1")
    monkeypatch.setenv("MINUTEMIND_MEDIA_ROOT", str(tmp_path))
    monkeypatch.setenv("MINUTEMIND_STORAGE_BASE", "http://test/media")
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()
