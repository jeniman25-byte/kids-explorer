from typing import Literal

from pydantic import BaseModel


class SubjectListItem(BaseModel):
    id: int
    name: str
    name_en: str
    emoji: str
    category: Literal["food", "animal", "plant"]
    sub_category: str
    explored: bool
    image_url: str
    parts_preview: list[str]


class SubjectListResponse(BaseModel):
    success: bool
    items: list[SubjectListItem]
