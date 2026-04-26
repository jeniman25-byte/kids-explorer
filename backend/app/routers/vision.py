from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.vision import VisionRequest, VisionResponse
from app.services.ai_vision import analyze_and_save_vision

router = APIRouter(prefix="/api", tags=["vision"])


@router.post("/vision", response_model=VisionResponse)
async def parse_vision(payload: VisionRequest, db: AsyncSession = Depends(get_db)):
    return await analyze_and_save_vision(
        db=db,
        image_url=payload.image_url,
        name=payload.name,
        name_en=payload.name_en,
        category=payload.category,
        view=payload.view,
        subject_id=payload.subject_id,
    )
