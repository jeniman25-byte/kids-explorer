import asyncio
import base64
from functools import lru_cache

from openai import OpenAI

from app.config import settings

FALLBACK_AUDIO_BASE64 = "data:audio/mp3;base64,bW9jay10dHMtYXVkaW8="


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


@lru_cache(maxsize=256)
def _tts_base64_cached(text: str) -> str:
    if not text:
        return FALLBACK_AUDIO_BASE64

    api_key = settings.openai_api_key
    if not api_key or "local-dev" in api_key:
        return FALLBACK_AUDIO_BASE64

    try:
        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            format="mp3",
        )

        audio_bytes: bytes | None = None
        if hasattr(response, "read"):
            audio_bytes = response.read()
        elif hasattr(response, "content"):
            audio_bytes = response.content

        if not audio_bytes:
            return FALLBACK_AUDIO_BASE64

        encoded = base64.b64encode(audio_bytes).decode("utf-8")
        return f"data:audio/mp3;base64,{encoded}"
    except Exception:
        return FALLBACK_AUDIO_BASE64


async def synthesize_tts(text: str) -> str:
    normalized_text = _normalize_text(text)
    return await asyncio.to_thread(_tts_base64_cached, normalized_text)
