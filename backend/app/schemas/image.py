from typing import Literal

from pydantic import BaseModel


class ImageRequest(BaseModel):
    name: str
    name_en: str
    category: Literal["food", "animal", "plant"]
    mode: Literal["4view", "8view"]
    seed: int


class ViewImage(BaseModel):
    view: str
    url: str
    label: str


class ImageResponse(BaseModel):
    success: bool
    subject_id: int
    images: list[ViewImage]


class ImageStatusImages(BaseModel):
    four: list[ViewImage]
    eight: list[ViewImage]


class ImageStatusResponse(BaseModel):
    success: bool
    subject_id: int
    status: str
    four_progress: int
    four_done: bool
    eight_progress: int
    eight_done: bool
    images: ImageStatusImages
