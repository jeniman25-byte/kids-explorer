import asyncio
from collections.abc import Iterable
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Image

IMAGE_PROMPTS = {
    "food": lambda name, view: (
        f"a cute cartoon {name}, {view} view, pure white background, "
        "flat illustration for kids, bright vivid colors, educational food illustration style"
    ),
    "animal": lambda name, view: (
        f"a cute cartoon {name}, {view} view, pure white background, "
        "flat illustration for kids, friendly expression, bright colors, nature education style"
    ),
    "plant": lambda name, view: (
        f"a cute cartoon {name} flower or plant, {view} view, pure white background, "
        "flat illustration for kids, bright vivid colors, botanical education style"
    ),
}

FOUR_VIEWS = ["front", "back", "left side", "right side"]
EIGHT_EXTRA = [
    "front-left diagonal",
    "front-right diagonal",
    "back-left diagonal",
    "back-right diagonal",
]

FOUR_VIEW_SPECS = [
    ("front", "front", "正面"),
    ("back", "back", "背面"),
    ("left", "left side", "左面"),
    ("right", "right side", "右面"),
]

EIGHT_VIEW_SPECS = [
    ("front_left", "front-left diagonal", "左前"),
    ("front_right", "front-right diagonal", "右前"),
    ("back_left", "back-left diagonal", "左后"),
    ("back_right", "back-right diagonal", "右后"),
]

VIEW_LABELS = {
    "front": "正面",
    "back": "背面",
    "left": "左面",
    "right": "右面",
    "front_left": "左前",
    "front_right": "右前",
    "back_left": "左后",
    "back_right": "右后",
}

FOUR_VIEW_KEYS = {spec[0] for spec in FOUR_VIEW_SPECS}
EIGHT_VIEW_KEYS = {spec[0] for spec in EIGHT_VIEW_SPECS}

STATUS_STORE: dict[int, dict[str, Any]] = {}
RUNNING_SUBJECTS: set[int] = set()
STATUS_LOCK = asyncio.Lock()


def _calc_progress(done: int, total: int) -> int:
    if total <= 0:
        return 0
    return int(done * 100 / total)


def _fallback_image_url(subject_id: int, view_type: str, seed: int) -> str:
    return f"https://picsum.photos/seed/kids-{subject_id}-{view_type}-{seed}/1024/1024"


async def _generate_one_image_url(
    *,
    subject_id: int,
    name: str,
    category: str,
    view_text: str,
    view_type: str,
    seed: int,
) -> str:
    api_key = settings.openai_api_key
    if not api_key or "local-dev" in api_key:
        return _fallback_image_url(subject_id, view_type, seed)

    prompt = IMAGE_PROMPTS[category](name, view_text)

    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
        )
        data = response.data[0]
        if getattr(data, "url", None):
            return data.url
        if getattr(data, "b64_json", None):
            return f"data:image/png;base64,{data.b64_json}"
    except Exception:
        pass

    return _fallback_image_url(subject_id, view_type, seed)


async def _upsert_image(subject_id: int, view_type: str, image_url: str) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Image).where(Image.subject_id == subject_id, Image.view_type == view_type).limit(1)
        )
        row = result.scalar_one_or_none()

        if row is None:
            db.add(Image(subject_id=subject_id, view_type=view_type, image_url=image_url))
        else:
            row.image_url = image_url

        await db.commit()


async def _count_subject_views(subject_id: int) -> tuple[int, int]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Image).where(Image.subject_id == subject_id))
        rows = result.scalars().all()

    four_done = len({row.view_type for row in rows if row.view_type in FOUR_VIEW_KEYS})
    eight_done = len({row.view_type for row in rows if row.view_type in EIGHT_VIEW_KEYS})
    return four_done, eight_done


async def _sync_status_with_db(subject_id: int) -> dict[str, Any]:
    four_done, eight_done = await _count_subject_views(subject_id)

    async with STATUS_LOCK:
        current = STATUS_STORE.get(subject_id, {})

        status = current.get("status")
        if status is None:
            if four_done >= 4 and eight_done >= 4:
                status = "8view_done"
            elif four_done >= 4:
                status = "4view_done"
            elif four_done > 0:
                status = "generating_4view"
            else:
                status = "queued"

        STATUS_STORE[subject_id] = {
            "status": status,
            "four_done_count": four_done,
            "eight_done_count": eight_done,
            "four_progress": _calc_progress(four_done, 4),
            "eight_progress": _calc_progress(eight_done, 4),
            "four_done": four_done >= 4,
            "eight_done": eight_done >= 4,
            "error": current.get("error"),
        }

        return STATUS_STORE[subject_id].copy()


async def _set_status(subject_id: int, **patch: Any) -> dict[str, Any]:
    async with STATUS_LOCK:
        current = STATUS_STORE.get(subject_id, {})
        current.update(patch)
        STATUS_STORE[subject_id] = current
        return current.copy()


async def _generate_and_store_phase(
    *,
    subject_id: int,
    name: str,
    category: str,
    seed: int,
    specs: Iterable[tuple[str, str, str]],
) -> None:
    async def generate_one(index: int, spec: tuple[str, str, str]) -> None:
        view_type, view_text, _ = spec
        image_url = await _generate_one_image_url(
            subject_id=subject_id,
            name=name,
            category=category,
            view_text=view_text,
            view_type=view_type,
            seed=seed + index,
        )
        await _upsert_image(subject_id, view_type, image_url)
        await _sync_status_with_db(subject_id)

    tasks = [generate_one(index, spec) for index, spec in enumerate(specs)]
    await asyncio.gather(*tasks)


async def run_image_generation_pipeline(
    *,
    subject_id: int,
    name: str,
    category: str,
    seed: int,
    mode: str,
) -> None:
    if subject_id in RUNNING_SUBJECTS:
        return

    RUNNING_SUBJECTS.add(subject_id)

    try:
        await _sync_status_with_db(subject_id)
        await _set_status(subject_id, status="generating_4view", error=None)

        await _generate_and_store_phase(
            subject_id=subject_id,
            name=name,
            category=category,
            seed=seed,
            specs=FOUR_VIEW_SPECS,
        )
        await _set_status(subject_id, status="4view_done")

        if mode in {"4view", "8view"}:
            await _set_status(subject_id, status="generating_8view")
            await _generate_and_store_phase(
                subject_id=subject_id,
                name=name,
                category=category,
                seed=seed + 100,
                specs=EIGHT_VIEW_SPECS,
            )
            await _set_status(subject_id, status="8view_done")

        await _sync_status_with_db(subject_id)
    except Exception as exc:
        await _set_status(subject_id, status="error", error=str(exc))
    finally:
        RUNNING_SUBJECTS.discard(subject_id)


async def list_subject_images(subject_id: int) -> dict[str, list[dict[str, str]]]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Image).where(Image.subject_id == subject_id))
        rows = result.scalars().all()

    four_rows = sorted(
        [row for row in rows if row.view_type in FOUR_VIEW_KEYS],
        key=lambda row: ["front", "back", "left", "right"].index(row.view_type),
    )
    eight_rows = sorted(
        [row for row in rows if row.view_type in EIGHT_VIEW_KEYS],
        key=lambda row: ["front_left", "front_right", "back_left", "back_right"].index(row.view_type),
    )

    return {
        "four": [
            {"view": row.view_type, "url": row.image_url, "label": VIEW_LABELS[row.view_type]}
            for row in four_rows
        ],
        "eight": [
            {"view": row.view_type, "url": row.image_url, "label": VIEW_LABELS[row.view_type]}
            for row in eight_rows
        ],
    }


async def get_image_status(subject_id: int) -> dict[str, Any]:
    status = await _sync_status_with_db(subject_id)
    images = await list_subject_images(subject_id)

    return {
        "success": True,
        "subject_id": subject_id,
        "status": status.get("status", "queued"),
        "four_progress": status.get("four_progress", 0),
        "four_done": status.get("four_done", False),
        "eight_progress": status.get("eight_progress", 0),
        "eight_done": status.get("eight_done", False),
        "images": images,
    }
