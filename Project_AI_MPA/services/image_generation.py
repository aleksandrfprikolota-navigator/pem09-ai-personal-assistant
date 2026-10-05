"""
Image Generation Service.
Uses OpenAI DALL-E API to generate images from text prompts.
"""

import base64
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json

from config import OPENAI_API_KEY, OPENAI_BASE_URL, DATA_DIR, DALLE_MODEL
from utils.logging import logger


# Create temp directory for generated images
GENERATED_IMAGES_DIR = DATA_DIR / "generated_images"
GENERATED_IMAGES_DIR.mkdir(exist_ok=True)


async def detect_image_generation_intent(text: str, conversation_history: list = None) -> Dict[str, Any]:
    """
    Detect if user wants to generate an image using GPT.
    
    Args:
        text: User's message text
        conversation_history: Recent conversation history for context
    
    Returns:
        Dictionary with 'needs_generation' (bool) and 'prompt' (str) if detected
    """
    from services.openai_client import openai_client
    
    # Keywords that strongly suggest image generation
    strong_keywords = [
        'нарисуй', 'сгенерируй изображение', 'создай картинку', 'сделай изображение',
        'покажи как выглядит', 'визуализируй', 'нарисовать', 'создать изображение',
        'generate image', 'draw', 'create picture', 'make image', 'show me what',
        'сгенерируй картинку', 'создай изображение', 'сделай картинку'
    ]
    
    # Quick check for strong keywords
    text_lower = text.lower()
    has_strong_keyword = any(keyword in text_lower for keyword in strong_keywords)
    
    # Build detection prompt
    detection_prompt = f"""Определи, хочет ли пользователь сгенерировать изображение.

Пользовательский запрос: "{text}"

Если пользователь просит:
- нарисовать что-то
- создать/сгенерировать изображение или картинку
- визуализировать что-то
- показать как что-то выглядит

То это запрос на генерацию изображения.

Ответь СТРОГО в формате JSON:
{{
    "needs_generation": true/false,
    "prompt": "улучшенный промпт для DALL-E на английском языке (если needs_generation=true)",
    "confidence": 0.0-1.0
}}

Если это НЕ запрос на генерацию изображения (например, просто вопрос или обычный диалог), верни needs_generation: false.
"""

    try:
        # Get AI decision
        messages = [{"role": "user", "content": detection_prompt}]
        response = await openai_client.generate_text_response(messages, temperature=0.3)
        
        # Parse JSON response
        # Remove markdown code blocks if present
        response_clean = response.strip()
        if response_clean.startswith('```'):
            # Remove ```json or ``` at start and ``` at end
            lines = response_clean.split('\n')
            response_clean = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_clean
        
        result = json.loads(response_clean)
        
        # If strong keyword found but AI said no, trust the keyword
        if has_strong_keyword and not result.get('needs_generation'):
            result['needs_generation'] = True
            # If no prompt provided, use original text
            if not result.get('prompt'):
                result['prompt'] = text
        
        logger.info(f"Image generation detection: {result.get('needs_generation')} (confidence: {result.get('confidence', 0)})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error detecting image generation intent: {e}")
        
        # Fallback: use keyword detection
        if has_strong_keyword:
            return {
                "needs_generation": True,
                "prompt": text,
                "confidence": 0.8
            }
        
        return {
            "needs_generation": False,
            "confidence": 0.0
        }


async def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = "vivid"
) -> Dict[str, Any]:
    """
    Generate an image using DALL-E API.
    
    Args:
        prompt: Text description of the image to generate
        size: Image size (256x256, 512x512, 1024x1024, 1024x1792, 1792x1024)
        quality: Image quality (standard, hd)
        style: Image style (vivid, natural)
    
    Returns:
        Dictionary with 'image_path', 'revised_prompt', and 'url'
    """
    try:
        logger.info(f"Generating image with {DALLE_MODEL}: {prompt[:100]}...")
        logger.debug(f"Requested style '{style}' is kept in the prompt only")

        from services.openai_client import openai_client

        quality_map = {"standard": "auto", "hd": "high"}
        size_map = {"1024x1792": "1024x1536", "1792x1024": "1536x1024"}
        # style есть только у DALL-E 3. gpt-image-2 отклоняет это поле.
        result = await openai_client.client.images.generate(
            model=DALLE_MODEL,
            prompt=prompt,
            n=1,
            size=size_map.get(size, size),
            quality=quality_map.get(quality, quality),
            output_format="png",
        )

        image_data = result.data[0]
        revised_prompt = image_data.revised_prompt or prompt
        image_url = getattr(image_data, "url", None)

        logger.info(f"Image generated successfully. Revised prompt: {revised_prompt[:100]}...")

        if getattr(image_data, "b64_json", None):
            image_path = _save_image_bytes(base64.b64decode(image_data.b64_json))
        elif image_url:
            image_path = await download_image(image_url)
        else:
            raise RuntimeError("OpenAI не вернул изображение")
        
        return {
            "image_path": image_path,
            "revised_prompt": revised_prompt,
            "url": image_url,
            "original_prompt": prompt
        }
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise


def _save_image_bytes(content: bytes) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = GENERATED_IMAGES_DIR / f"generated_{timestamp}.png"
    filepath.write_bytes(content)
    logger.info(f"Image saved to: {filepath}")
    return filepath


async def download_image(url: str) -> Path:
    """
    Download image from URL and save to local file.
    
    Args:
        url: Image URL
    
    Returns:
        Path to downloaded image
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
        filepath = GENERATED_IMAGES_DIR / filename
        
        # Download image
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                
                # Save to file
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(await response.read())
        
        logger.info(f"Image downloaded to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        raise


async def generate_image_variations(
    image_path: Path,
    n: int = 1,
    size: str = "1024x1024"
) -> list:
    """
    Generate variations of an existing image.
    
    Args:
        image_path: Path to source image
        n: Number of variations to generate (1-10)
        size: Image size
    
    Returns:
        List of paths to generated variations
    """
    try:
        logger.info(f"Generating {n} variations of image: {image_path}")
        
        # Prepare multipart form data
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        data = aiohttp.FormData()
        data.add_field('image', 
                      open(image_path, 'rb'),
                      filename=image_path.name,
                      content_type='image/png')
        data.add_field('n', str(n))
        data.add_field('size', size)
        
        api_url = f"{OPENAI_BASE_URL}/images/variations"
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                headers=headers,
                data=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"DALL-E variations API error: {error_text}")
                    raise Exception(f"API error: {response.status}")
                
                result = await response.json()
        
        # Download all variations
        variation_paths = []
        for i, image_data in enumerate(result['data']):
            url = image_data['url']
            path = await download_image(url)
            variation_paths.append(path)
        
        logger.info(f"Generated {len(variation_paths)} variations successfully")
        return variation_paths
        
    except Exception as e:
        logger.error(f"Error generating variations: {e}")
        raise

