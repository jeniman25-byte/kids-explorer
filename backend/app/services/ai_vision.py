import json
import re
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Image, Part

FACTS_KEYS = {
    "food": ["颜色", "口感", "吃法"],
    "animal": ["颜色", "习性", "趣味"],
    "plant": ["颜色", "气味", "特征"],
}

PART_COLORS = ["#FFB347", "#4FC3F7", "#66BB6A", "#F06292"]

FALLBACK_PARTS = {
    "food": [
        {"id": "peel", "name": "外皮", "short_name": "皮", "x": 0.32, "y": 0.24},
        {"id": "flesh", "name": "果肉", "short_name": "肉", "x": 0.58, "y": 0.42},
        {"id": "stem", "name": "果柄", "short_name": "柄", "x": 0.28, "y": 0.74},
        {"id": "tip", "name": "果尖", "short_name": "尖", "x": 0.72, "y": 0.40},
    ],
    "animal": [
        {"id": "ear", "name": "耳朵", "short_name": "耳", "x": 0.34, "y": 0.20},
        {"id": "eye", "name": "眼睛", "short_name": "眼", "x": 0.55, "y": 0.34},
        {"id": "paw", "name": "爪子", "short_name": "爪", "x": 0.30, "y": 0.72},
        {"id": "tail", "name": "尾巴", "short_name": "尾", "x": 0.70, "y": 0.70},
    ],
    "plant": [
        {"id": "petal", "name": "花瓣", "short_name": "瓣", "x": 0.44, "y": 0.20},
        {"id": "stamen", "name": "花蕊", "short_name": "蕊", "x": 0.60, "y": 0.36},
        {"id": "leaf", "name": "叶子", "short_name": "叶", "x": 0.30, "y": 0.76},
        {"id": "branch", "name": "花枝", "short_name": "枝", "x": 0.74, "y": 0.68},
    ],
}


def _safe_category(category: str) -> str:
    if category in FACTS_KEYS:
        return category
    return "animal"


def _extract_json_block(text: str) -> dict[str, Any]:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("Vision response does not contain JSON")
    return json.loads(match.group(0))


def _normalize_part(part: dict[str, Any], category: str, idx: int) -> dict[str, Any]:
    safe_category = _safe_category(category)
    keys = FACTS_KEYS[safe_category]

    facts_obj: dict[str, str] = {}
    raw_facts = part.get("facts", {})
    for key in keys:
        value = str(raw_facts.get(key, "")).strip() if isinstance(raw_facts, dict) else ""
        facts_obj[key] = value or f"{part.get('name', '该部位')}的{key}信息"

    x = float(part.get("x", 0.5))
    y = float(part.get("y", 0.5))
    x = max(0.05, min(0.95, x))
    y = max(0.05, min(0.95, y))

    name = str(part.get("name", "未知部位")).strip() or "未知部位"
    short_name = str(part.get("short_name", name[:1] or "?")).strip()[:1] or "?"

    return {
        "id": str(part.get("id", f"part_{idx + 1}")),
        "name": name,
        "short_name": short_name,
        "color": PART_COLORS[idx % len(PART_COLORS)],
        "x": round(x, 3),
        "y": round(y, 3),
        "description": str(part.get("description", f"这是{name}，我们可以从这里观察到很多特点。")),
        "facts": facts_obj,
    }


def _fallback_vision(name: str, category: str, view: str) -> dict[str, Any]:
    safe_category = _safe_category(category)
    parts = []
    for idx, seed_part in enumerate(FALLBACK_PARTS.get(safe_category, FALLBACK_PARTS["animal"])):
        keys = FACTS_KEYS[safe_category]
        parts.append(
            {
                "id": seed_part["id"],
                "name": seed_part["name"],
                "short_name": seed_part["short_name"],
                "color": PART_COLORS[idx % len(PART_COLORS)],
                "x": seed_part["x"],
                "y": seed_part["y"],
                "description": f"{name}的{seed_part['name']}是很有代表性的部位，观察它可以了解更多知识。",
                "facts": {
                    keys[0]: f"{name}常见{keys[0]}特征",
                    keys[1]: f"与{keys[1]}相关的有趣知识",
                    keys[2]: f"{keys[2]}方面值得继续探索",
                },
            }
        )

    return {
        "parts": parts,
        "view_description": f"从{view}视角观察{name}，可以清楚看到它的关键部位。",
        "info_row": {key: parts[0]["facts"][key] for key in FACTS_KEYS[safe_category]},
    }


async def _call_gpt4o_vision(
    *, image_url: str, name: str, name_en: str, category: str, view: str
) -> dict[str, Any]:
    safe_category = _safe_category(category)
    api_key = settings.openai_api_key
    if not api_key or "local-dev" in api_key:
        return _fallback_vision(name, safe_category, view)

    keys = FACTS_KEYS[safe_category]
    prompt = f"""
你是儿童科普插画拆解助手。请分析图中对象，并严格返回 JSON：
{{
  "parts": [
    {{
      "id": "part_key",
      "name": "中文部位名",
      "short_name": "1字简称",
      "x": 0.42,
      "y": 0.35,
      "description": "中文介绍",
      "facts": {{"{keys[0]}": "...", "{keys[1]}": "...", "{keys[2]}": "..."}}
    }}
  ],
  "view_description": "当前视角描述",
  "info_row": {{"{keys[0]}": "...", "{keys[1]}": "...", "{keys[2]}": "..."}}
}}
要求：
1) 只输出 JSON，无其他文本。
2) parts 返回 4 个部位。
3) x/y 是 0~1 的比例坐标。
4) 对象：{name} ({name_en})，分类：{category}，视角：{view}。
"""

    client = AsyncOpenAI(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        raw = _extract_json_block(content)

        raw_parts = raw.get("parts", []) if isinstance(raw.get("parts", []), list) else []
        parts = [_normalize_part(part, safe_category, idx) for idx, part in enumerate(raw_parts[:4])]
        if not parts:
            return _fallback_vision(name, safe_category, view)

        while len(parts) < 4:
            parts.append(parts[-1] | {"id": f"{parts[-1]['id']}_{len(parts)}"})

        info_row = raw.get("info_row", {}) if isinstance(raw.get("info_row"), dict) else {}
        normalized_info = {}
        for key in keys:
            normalized_info[key] = str(info_row.get(key, "")).strip() or parts[0]["facts"][key]

        view_description = str(raw.get("view_description", "")).strip() or f"从{view}视角观察{name}。"

        return {
            "parts": parts,
            "view_description": view_description,
            "info_row": normalized_info,
        }
    except Exception:
        return _fallback_vision(name, safe_category, view)


async def _resolve_image_id(db: AsyncSession, subject_id: int, view: str, image_url: str) -> int:
    result = await db.execute(
        select(Image).where(Image.subject_id == subject_id, Image.view_type == view).limit(1)
    )
    image = result.scalar_one_or_none()
    if image:
        return image.id

    image = Image(subject_id=subject_id, view_type=view if view else "single", image_url=image_url)
    db.add(image)
    await db.flush()
    return image.id


async def analyze_and_save_vision(
    *,
    db: AsyncSession,
    image_url: str,
    name: str,
    name_en: str,
    category: str,
    view: str,
    subject_id: int,
) -> dict[str, Any]:
    safe_category = _safe_category(category)
    vision = await _call_gpt4o_vision(
        image_url=image_url,
        name=name,
        name_en=name_en,
        category=safe_category,
        view=view,
    )

    image_id = await _resolve_image_id(db, subject_id, view, image_url)

    await db.execute(delete(Part).where(Part.subject_id == subject_id, Part.image_id == image_id))

    for part in vision["parts"]:
        db.add(
            Part(
                subject_id=subject_id,
                image_id=image_id,
                part_key=part["id"],
                name=part["name"],
                short_name=part["short_name"],
                color=part["color"],
                pos_x=part["x"],
                pos_y=part["y"],
                description=part["description"],
                facts=part["facts"],
            )
        )

    await db.commit()

    return {
        "success": True,
        "parts": [
            {
                "id": part["id"],
                "name": part["name"],
                "short_name": part["short_name"],
                "color": part["color"],
                "x": part["x"],
                "y": part["y"],
                "description": part["description"],
                "facts": part["facts"],
            }
            for part in vision["parts"]
        ],
        "view_description": vision["view_description"],
        "info_row": vision["info_row"],
    }
