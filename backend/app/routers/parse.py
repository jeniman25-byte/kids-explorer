import random

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import History, Subject
from app.schemas.parse import ParseRequest, ParseResponse
from app.services.ai_parse import parse_subject_from_text

router = APIRouter(prefix="/api", tags=["parse"])


@router.post("/parse", response_model=ParseResponse)
async def parse_text(payload: ParseRequest, db: AsyncSession = Depends(get_db)):
    parsed = await parse_subject_from_text(payload.text)

    subject_name = parsed["name"]
    category = parsed["category"]

    if category in {"food", "animal", "plant"}:
        result = await db.execute(select(Subject).where(Subject.name == subject_name).limit(1))
        subject = result.scalar_one_or_none()

        if subject is None:
            subject = Subject(
                name=parsed["name"],
                name_en=parsed["name_en"],
                emoji=parsed["emoji"],
                category=parsed["category"],
                sub_category=parsed["sub_category"],
                seed=random.randint(10000, 99999),
            )
            db.add(subject)
            await db.flush()

        db.add(
            History(
                subject_id=subject.id,
                category=subject.category,
            )
        )
        await db.commit()

    return {
        "success": True,
        "name": parsed["name"],
        "name_en": parsed["name_en"],
        "emoji": parsed["emoji"],
        "category": parsed["category"],
        "sub_category": parsed["sub_category"],
    }
