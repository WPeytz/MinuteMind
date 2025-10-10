"""Video stitching helpers using MoviePy or FFmpeg."""
from __future__ import annotations

import asyncio
import json
import tempfile
import contextlib
from datetime import datetime
from pathlib import Path
from typing import Sequence
from uuid import uuid4

from .. import models
from ..settings import get_settings
from . import storage


def _fake_video_payload(script: models.Script, audio_segments: Sequence[models.SceneAudio]) -> bytes:
    lines = [f"Topic: {script.topic}"]
    for scene in script.scenes:
        lines.append(f"Scene {scene.scene_id}: {scene.title}")
        lines.append(f"Visual: {scene.visual}")
        lines.append(f"Narration: {scene.narration}")
    for audio in audio_segments:
        lines.append(f"Audio stored at: {audio.audio_url}")
    return "\n".join(lines).encode("utf-8")


def _render_with_moviepy(script: models.Script, audio_segments: Sequence[models.SceneAudio], image_urls: dict[str, str] | None = None) -> bytes:
    try:
        from moviepy.editor import (
            AudioFileClip,
            ColorClip,
            CompositeVideoClip,
            ImageClip,
            concatenate_videoclips,
        )
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("moviepy is required for real video rendering") from exc

    image_urls = image_urls or {}
    clips = []
    for scene, audio in zip(script.scenes, audio_segments):
        # Resolve the audio path from the URL; tolerate relative or malformed inputs.
        audio_path = storage.resolve_url(audio.audio_url)
        if not audio_path.exists():
            # Fallback to /tmp/media/<basename> (where TTS writes .wav files)
            candidate = Path("/tmp/media") / Path(audio.audio_url).name
            if candidate.exists():
                audio_path = candidate
            else:
                raise FileNotFoundError(f"Audio payload missing at {audio_path}")

        # Load audio; MoviePy reads WAV/MP3/AAC via ffmpeg. Explicitly set fps via format to avoid misdetection.
        audio_clip = AudioFileClip(str(audio_path))

        # Use exact audio duration to avoid unnatural pauses between scenes
        duration = float(audio_clip.duration)

        # Try to load image for this scene
        visual_clip = None
        if scene.scene_id in image_urls:
            image_url = image_urls[scene.scene_id]
            try:
                image_path = storage.resolve_url(image_url)
                if image_path.exists():
                    # Resize image using PIL before creating clip
                    from PIL import Image
                    img = Image.open(str(image_path))
                    # Resize to fit 1280x720 maintaining aspect ratio using faster algorithm
                    img.thumbnail((1280, 720), Image.Resampling.BILINEAR)  # Faster than LANCZOS
                    # Create a 1280x720 black background
                    background = Image.new('RGB', (1280, 720), (22, 28, 45))
                    # Paste resized image centered
                    offset = ((1280 - img.width) // 2, (720 - img.height) // 2)
                    background.paste(img, offset)
                    # Create clip directly from PIL Image to avoid temp file I/O
                    import numpy as np
                    img_array = np.array(background)
                    visual_clip = ImageClip(img_array).set_duration(duration)
            except Exception as e:
                print(f"Failed to load image for scene {scene.scene_id}: {e}")

        # Fallback to solid color background if no image
        if visual_clip is None:
            visual_clip = ColorClip(size=(1280, 720), color=(22, 28, 45)).set_duration(duration)

        # Compose video with audio
        composite = CompositeVideoClip([visual_clip]).set_audio(audio_clip)
        clips.append(composite)

    final = concatenate_videoclips(clips)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        out_path = Path(tmp.name)

    # Get optimal thread count (use all available cores)
    import multiprocessing
    thread_count = multiprocessing.cpu_count()

    # Prefer H.264 + AAC for wide compatibility; optimized for speed
    final.write_videofile(
        str(out_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="veryfast",  # Slightly better quality than ultrafast with minimal speed impact
        threads=thread_count,
        verbose=False,
        logger=None,
        # Additional optimizations for faster encoding
        ffmpeg_params=["-crf", "28", "-movflags", "+faststart"],
    )
    # Clean up clips to release file handles
    with contextlib.suppress(Exception):
        for c in clips:
            c.close()
        final.close()
    payload = out_path.read_bytes()
    out_path.unlink(missing_ok=True)
    return payload


async def render_video(response: models.ScriptResponse) -> models.VideoMetadata:
    """Perform text-to-speech and video compositing."""
    script = response.script
    audio_segments = response.audio
    settings = get_settings()

    # Build image URL mapping from response
    image_map = {img.scene_id: img.image_url for img in response.images}

    if settings.use_mock_video:
        video_bytes = _fake_video_payload(script, audio_segments)
    else:  # pragma: no cover - requires moviepy & codecs
        try:
            video_bytes = await asyncio.to_thread(_render_with_moviepy, script, audio_segments, image_map)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Failed to stitch video") from exc

    video_id = uuid4().hex
    stored = await storage.save_render(video_id, video_bytes)

    metadata = models.VideoMetadata(
        video_id=video_id,
        script_id=script.script_id,
        title=script.topic,
        status="completed",
        created_at=datetime.utcnow(),
        storage_path=stored.url,
    )

    # Save metadata to GCS
    await _save_video_metadata(metadata)

    return metadata


async def _save_video_metadata(metadata: models.VideoMetadata) -> None:
    """Save video metadata to GCS or local storage."""
    metadata_json = json.dumps({
        "video_id": metadata.video_id,
        "script_id": metadata.script_id,
        "title": metadata.title,
        "status": metadata.status,
        "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
        "storage_path": metadata.storage_path,
        "thumbnail_url": metadata.thumbnail_url,
    })

    filename = f"metadata-{metadata.video_id}.json"
    await storage.save_bytes(
        name=f"metadata-{metadata.video_id}",
        payload=metadata_json.encode("utf-8"),
        suffix=".json",
    )


async def list_videos() -> list[models.VideoMetadata]:
    """Retrieve stored video metadata from GCS."""
    settings = get_settings()
    config = storage._get_gcs_config()

    def _load_from_gcs() -> list[models.VideoMetadata]:
        """Load video metadata from GCS bucket."""
        try:
            from google.cloud import storage as gcs_storage
        except ImportError:
            return []

        if not config:
            return []

        try:
            client = gcs_storage.Client()
            bucket = client.bucket(config.bucket)

            # List all metadata files
            blobs = bucket.list_blobs(prefix=config.prefix if config.prefix else None)

            videos: list[models.VideoMetadata] = []
            for blob in blobs:
                if blob.name.endswith(".json") and "metadata-" in blob.name:
                    try:
                        content = blob.download_as_text()
                        data = json.loads(content)
                        # Parse ISO format datetime
                        if data.get("created_at"):
                            data["created_at"] = datetime.fromisoformat(data["created_at"])
                        videos.append(models.VideoMetadata(**data))
                    except Exception as e:
                        print(f"Failed to load metadata from {blob.name}: {e}")
                        continue

            videos.sort(key=lambda v: v.created_at if v.created_at else datetime.min, reverse=True)
            return videos
        except Exception as e:
            print(f"Failed to list videos from GCS: {e}")
            return []

    # If using GCS, load from there
    if config:
        return await asyncio.to_thread(_load_from_gcs)

    # Fallback to local file-based storage
    index_path = Path(settings.media_root) / "videos.json"

    def _load_local() -> list[models.VideoMetadata]:
        if not index_path.exists():
            return []

        try:
            payload = json.loads(index_path.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError:
            return []

        if not isinstance(payload, list):
            return []

        videos: list[models.VideoMetadata] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                videos.append(models.VideoMetadata(**item))
            except Exception:
                continue

        videos.sort(key=lambda video: video.created_at if video.created_at else datetime.min, reverse=True)
        return videos

    return await asyncio.to_thread(_load_local)
