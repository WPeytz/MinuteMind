"""Endpoints for script generation workflows."""
from fastapi import APIRouter, Depends, HTTPException

from .. import models
from ..deps import get_db
from ..services import llm, tts, images

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/generate", response_model=models.ScriptResponse)
async def generate_script(payload: models.ScriptRequest, _=Depends(get_db)) -> models.ScriptResponse:
    """Generate a narrated script for the requested topic."""
    script = await llm.generate_script(payload)
    try:
        audio_segments = await tts.synthesize_voice(script)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Generate images for each scene
    try:
        image_map = await images.generate_images_for_script(script)
        scene_images = [
            models.SceneImage(scene_id=scene_id, image_url=image_url)
            for scene_id, image_url in image_map.items()
        ]
    except Exception as exc:
        print(f"Image generation failed: {exc}")
        scene_images = []

    return models.ScriptResponse(script=script, audio=audio_segments, images=scene_images)
