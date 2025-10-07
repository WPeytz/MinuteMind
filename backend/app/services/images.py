"""Image generation helpers using OpenAI DALL-E."""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Optional

from .. import models
from ..settings import get_settings
from . import storage


def _generate_with_dalle(prompt: str, size: str = "1024x1024") -> bytes:
    """Generate an image using OpenAI DALL-E and return the image bytes."""
    settings = get_settings()
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is required for image generation") from exc

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.openai_api_key)

    # Generate image using DALL-E
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )

    # Get the image URL from response
    image_url = response.data[0].url
    if not image_url:
        raise RuntimeError("No image URL in DALL-E response")

    # Download the image
    import urllib.request
    with urllib.request.urlopen(image_url) as response_data:
        return response_data.read()


def _create_placeholder_image(width: int = 1280, height: int = 720) -> bytes:
    """Create a simple placeholder image using PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
    except ImportError as exc:
        raise RuntimeError("Pillow is required for placeholder images") from exc

    # Create a dark blue background
    img = Image.new('RGB', (width, height), color=(22, 28, 45))
    draw = ImageDraw.Draw(img)

    # Add simple text
    text = "Generated Image"
    # Use default font
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=(200, 200, 200))

    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


async def generate_scene_image(scene: models.ScriptScene, script_id: str, use_mock: bool = False) -> str:
    """Generate an image for a scene and return the storage URL."""
    settings = get_settings()

    if use_mock or not settings.openai_api_key:
        # Create placeholder image
        image_bytes = await asyncio.to_thread(_create_placeholder_image)
        suffix = ".png"
    else:
        # Generate with DALL-E
        # Create a detailed prompt from the scene visual description
        prompt = f"{scene.visual}. Cinematic, professional, high quality."
        try:
            image_bytes = await asyncio.to_thread(_generate_with_dalle, prompt)
            suffix = ".png"
        except Exception as exc:
            # Fallback to placeholder on error
            print(f"DALL-E generation failed: {exc}, using placeholder")
            image_bytes = await asyncio.to_thread(_create_placeholder_image)
            suffix = ".png"

    # Save to storage
    stored = await storage.save_bytes(
        name=f"{script_id}-{scene.scene_id}-image",
        payload=image_bytes,
        suffix=suffix,
    )

    return stored.url


async def generate_images_for_script(script: models.Script) -> dict[str, str]:
    """Generate images for all scenes in a script. Returns scene_id -> image_url mapping."""
    settings = get_settings()
    use_mock = getattr(settings, 'use_mock_images', False)

    # Generate all images in parallel for faster processing
    tasks = [generate_scene_image(scene, script.script_id, use_mock) for scene in script.scenes]
    image_urls = await asyncio.gather(*tasks)

    # Map scene IDs to their image URLs
    image_map = {scene.scene_id: url for scene, url in zip(script.scenes, image_urls)}
    return image_map
