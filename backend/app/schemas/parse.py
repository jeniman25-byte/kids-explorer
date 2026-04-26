from pydantic import BaseModel


class ParseRequest(BaseModel):
    text: str


class ParseResponse(BaseModel):
    success: bool
    name: str
    name_en: str
    emoji: str
    category: str
    sub_category: str
