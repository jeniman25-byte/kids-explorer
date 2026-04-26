from fastapi import APIRouter

from app.schemas.tts import TtsRequest, TtsResponse

router = APIRouter(prefix="/api", tags=["tts"])


@router.post("/tts", response_model=TtsResponse)
async def create_tts(payload: TtsRequest):
    _ = payload
    return {
        "success": True,
        "audio_base64": "data:audio/mp3;base64,bW9jay10dHMtYXVkaW8=",
    }
