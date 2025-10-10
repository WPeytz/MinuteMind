"""Endpoints related to video rendering and retrieval."""
from fastapi import APIRouter, Depends

from .. import models
from ..services import stitch
from ..deps import get_db

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/render", response_model=models.VideoMetadata)
async def render_video(script: models.ScriptResponse, _=Depends(get_db)) -> models.VideoMetadata:
    """Kick off a video render for the provided script."""
    return await stitch.render_video(script)


@router.get("/", response_model=list[models.VideoMetadata])
async def list_videos(_=Depends(get_db)) -> list[models.VideoMetadata]:
    """List available generated videos."""
    return await stitch.list_videos()


@router.delete("/{video_id}")
async def delete_video(video_id: str, _=Depends(get_db)) -> dict[str, str]:
    """Delete a video and its metadata."""
    await stitch.delete_video(video_id)
    return {"message": "Video deleted successfully"}
