from fastapi import APIRouter

from app.schemas.tts import TtsRequest, TtsResponse
from app.services.ai_tts import synthesize_tts

router = APIRouter(prefix="/api", tags=["tts"])


@router.post("/tts", response_model=TtsResponse)
async def create_tts(payload: TtsRequest):
    audio_base64 = await synthesize_tts(payload.text)
    return {
        "success": True,
        "audio_base64": audio_base64,
    }
