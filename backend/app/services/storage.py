"""Object storage integrations (GCS, Supabase, etc.)."""
from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from ..settings import get_settings


@dataclass(frozen=True)
class StoredMedia:
    url: str
    path: str


@dataclass(frozen=True)
class _GCSConfig:
    bucket: str
    prefix: str
    public_host: str


def _ensure_media_root() -> Path:
    settings = get_settings()
    media_root = Path(settings.media_root)
    media_root.mkdir(parents=True, exist_ok=True)
    return media_root


def _build_url(filename: str) -> str:
    settings = get_settings()
    base = settings.storage_base_url.rstrip("/")
    return f"{base}/{filename}"


@lru_cache(maxsize=1)
def _get_gcs_config() -> _GCSConfig | None:
    base = (get_settings().storage_base_url or "").strip()
    if not base:
        return None

    parsed = urlparse(base)
    if parsed.scheme == "gs":
        if not parsed.netloc:
            raise RuntimeError("MINUTEMIND_STORAGE_BASE gs:// URL must include a bucket name")
        return _GCSConfig(
            bucket=parsed.netloc,
            prefix=parsed.path.strip("/"),
            public_host="https://storage.googleapis.com",
        )

    if parsed.scheme in {"http", "https"} and parsed.netloc.endswith("storage.googleapis.com"):
        path_parts = [segment for segment in parsed.path.strip("/").split("/") if segment]
        if not path_parts:
            raise RuntimeError(
                "MINUTEMIND_STORAGE_BASE must include the bucket path, e.g. "
                "https://storage.googleapis.com/<bucket>"
            )
        bucket = path_parts[0]
        prefix = "/".join(path_parts[1:])
        return _GCSConfig(
            bucket=bucket,
            prefix=prefix,
            public_host=f"{parsed.scheme}://{parsed.netloc}",
        )

    return None


def _guess_content_type(suffix: str) -> str:
    mapping = {
        ".mp4": "video/mp4",
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
    }
    return mapping.get(suffix.lower(), "application/octet-stream")


def _build_gcs_blob_name(config: _GCSConfig, filename: str) -> str:
    return "/".join(filter(None, [config.prefix, filename]))


def _build_gcs_public_url(config: _GCSConfig, filename: str) -> str:
    segments = [config.public_host.rstrip("/"), config.bucket]
    if config.prefix:
        segments.append(config.prefix)
    segments.append(filename)
    return "/".join(segments)


def _upload_to_gcs(config: _GCSConfig, filename: str, payload: bytes, content_type: str) -> StoredMedia:
    try:
        from google.cloud import storage  # type: ignore import-not-found
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "google-cloud-storage is required when MINUTEMIND_STORAGE_BASE points to a GCS bucket"
        ) from exc

    client = storage.Client()
    bucket = client.bucket(config.bucket)
    blob_name = _build_gcs_blob_name(config, filename)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(payload, content_type=content_type)
    with contextlib.suppress(Exception):
        blob.make_public()
    public_url = _build_gcs_public_url(config, filename)
    return StoredMedia(url=public_url, path=f"gs://{config.bucket}/{blob_name}")


async def save_bytes(name: str, payload: bytes, *, suffix: str) -> StoredMedia:
    """Persist raw bytes and return a storage descriptor."""
    media_root = _ensure_media_root()
    filename = f"{name}{suffix}"
    file_path = media_root / filename

    def _write() -> None:
        file_path.write_bytes(payload)

    await asyncio.to_thread(_write)
    return StoredMedia(url=_build_url(filename), path=str(file_path))


async def save_render(name: str, payload: bytes) -> StoredMedia:
    """Persist rendered assets (video) and return storage descriptor."""
    config = _get_gcs_config()
    if config:
        filename = f"{name}.mp4"
        return await asyncio.to_thread(
            _upload_to_gcs,
            config,
            filename,
            payload,
            _guess_content_type(".mp4"),
        )
    return await save_bytes(name, payload, suffix=".mp4")


def resolve_url(url: str) -> Path:
    """Convert a storage URL back into a filesystem path."""
    filename = url.rstrip("/").split("/")[-1]
    return _ensure_media_root() / filename
