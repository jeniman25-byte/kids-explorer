from pydantic import BaseModel


class TtsRequest(BaseModel):
    text: str


class TtsResponse(BaseModel):
    success: bool
    audio_base64: str
