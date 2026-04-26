from pydantic import BaseModel


class VisionRequest(BaseModel):
    image_url: str
    name: str
    name_en: str
    category: str
    view: str
    subject_id: int


class VisionPart(BaseModel):
    id: str
    name: str
    short_name: str
    color: str
    x: float
    y: float
    description: str
    facts: dict[str, str]


class VisionResponse(BaseModel):
    success: bool
    parts: list[VisionPart]
    view_description: str
    info_row: dict[str, str]
