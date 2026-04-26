from collections import defaultdict
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import History, Image, Part, Subject
from app.schemas.subject import SubjectListResponse

router = APIRouter(prefix="/api", tags=["subjects"])


@router.get("/subjects", response_model=SubjectListResponse)
async def list_subjects(
    category: Literal["food", "animal", "plant"] = Query(...),
    db: AsyncSession = Depends(get_db),
):
    subject_result = await db.execute(
        select(Subject).where(Subject.category == category).order_by(desc(Subject.created_at))
    )
    subjects = subject_result.scalars().all()
    if not subjects:
        return {"success": True, "items": []}

    subject_ids = [subject.id for subject in subjects]

    history_result = await db.execute(select(History.subject_id).where(History.subject_id.in_(subject_ids)))
    explored_ids = {row[0] for row in history_result.all()}

    image_result = await db.execute(
        select(Image).where(Image.subject_id.in_(subject_ids)).order_by(desc(Image.created_at))
    )
    cover_map: dict[int, str] = {}
    for image in image_result.scalars().all():
        if image.subject_id not in cover_map:
            cover_map[image.subject_id] = image.image_url
        if image.view_type == "front":
            cover_map[image.subject_id] = image.image_url

    part_result = await db.execute(select(Part).where(Part.subject_id.in_(subject_ids)))
    parts_map: dict[int, list[str]] = defaultdict(list)
    for part in part_result.scalars().all():
        if part.name not in parts_map[part.subject_id]:
            parts_map[part.subject_id].append(part.name)

    items = [
        {
            "id": subject.id,
            "name": subject.name,
            "name_en": subject.name_en,
            "emoji": subject.emoji,
            "category": subject.category,
            "sub_category": subject.sub_category,
            "explored": subject.id in explored_ids,
            "image_url": cover_map.get(subject.id, ""),
            "parts_preview": parts_map.get(subject.id, [])[:3],
        }
        for subject in subjects
    ]
    return {"success": True, "items": items}
