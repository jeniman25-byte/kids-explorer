import json
import re
from typing import Any

from anthropic import AsyncAnthropic

from app.config import settings

PARSE_PROMPT = """
从用户语音文字中提取探索目标，返回严格 JSON，不含任何多余文字：
{
  "name": "中文名",
  "name_en": "英文名",
  "emoji": "最合适的单个emoji",
  "category": "food | animal | plant",
  "sub_category": "对应子分类"
}
子分类对照：
  food   → 水果 | 蔬菜 | 主食 | 甜品
  animal → 陆地 | 海洋 | 天空 | 昆虫
  plant  → 花朵 | 树木 | 叶子 | 草本
若无法识别则 category 为 "unknown"
"""

VALID_CATEGORIES = {"food", "animal", "plant", "unknown"}
DEFAULT_SUB_CATEGORY = {
    "food": "水果",
    "animal": "陆地",
    "plant": "花朵",
    "unknown": "未知",
}

FALLBACK_PRESETS = {
    "熊猫": {
        "name": "熊猫",
        "name_en": "giant panda",
        "emoji": "🐼",
        "category": "animal",
        "sub_category": "陆地",
    },
    "香蕉": {
        "name": "香蕉",
        "name_en": "banana",
        "emoji": "🍌",
        "category": "food",
        "sub_category": "水果",
    },
    "樱花": {
        "name": "樱花",
        "name_en": "cherry blossom",
        "emoji": "🌸",
        "category": "plant",
        "sub_category": "花朵",
    },
}


def _extract_json_block(text: str) -> dict[str, Any]:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("Claude response does not contain JSON object")
    return json.loads(match.group(0))


def _normalize_result(raw: dict[str, Any], original_text: str) -> dict[str, str]:
    category = str(raw.get("category", "unknown")).strip().lower()
    if category not in VALID_CATEGORIES:
        category = "unknown"

    name = str(raw.get("name", "")).strip() or original_text.strip() or "未知对象"
    name_en = str(raw.get("name_en", "")).strip() or "unknown"
    emoji = str(raw.get("emoji", "")).strip() or "❓"
    sub_category = str(raw.get("sub_category", "")).strip() or DEFAULT_SUB_CATEGORY[category]

    return {
        "name": name,
        "name_en": name_en,
        "emoji": emoji,
        "category": category,
        "sub_category": sub_category,
    }


def _fallback_parse(text: str) -> dict[str, str]:
    for key, value in FALLBACK_PRESETS.items():
        if key in text:
            return value

    plain_text = text.strip()
    return {
        "name": plain_text or "未知对象",
        "name_en": "unknown",
        "emoji": "❓",
        "category": "unknown",
        "sub_category": "未知",
    }


async def parse_subject_from_text(text: str) -> dict[str, str]:
    api_key = settings.claude_api_key
    if not api_key or "sk-ant-" not in api_key:
        return _fallback_parse(text)

    client = AsyncAnthropic(api_key=api_key)

    try:
        response = await client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=300,
            temperature=0,
            system=PARSE_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"用户语音文字：{text}",
                }
            ],
        )
        raw_text = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )
        parsed = _extract_json_block(raw_text)
        return _normalize_result(parsed, text)
    except Exception:
        return _fallback_parse(text)
