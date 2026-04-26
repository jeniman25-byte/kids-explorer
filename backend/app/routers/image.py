import random

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Subject
from app.schemas.image import ImageRequest, ImageResponse, ImageStatusResponse
from app.services.ai_image import get_image_status, list_subject_images, run_image_generation_pipeline

router = APIRouter(prefix="/api", tags=["image"])


@router.post("/image", response_model=ImageResponse)
async def generate_images(
    payload: ImageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subject)
        .where(Subject.name == payload.name, Subject.category == payload.category)
        .limit(1)
    )
    subject = result.scalar_one_or_none()

    if subject is None:
        subject = Subject(
            name=payload.name,
            name_en=payload.name_en,
            emoji="❓",
            category=payload.category,
            sub_category="未知",
            seed=payload.seed or random.randint(10000, 99999),
        )
        db.add(subject)
        await db.flush()
        await db.commit()

    background_tasks.add_task(
        run_image_generation_pipeline,
        subject_id=subject.id,
        name=subject.name_en or subject.name,
        category=subject.category,
        seed=payload.seed,
        mode=payload.mode,
    )

    images = await list_subject_images(subject.id)
    return {
        "success": True,
        "subject_id": subject.id,
        "images": images["four"],
    }


@router.get("/image/status/{subject_id}", response_model=ImageStatusResponse)
async def image_status(subject_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).where(Subject.id == subject_id).limit(1))
    subject = result.scalar_one_or_none()
    if subject is None:
        raise HTTPException(status_code=404, detail="subject not found")

    return await get_image_status(subject_id)
