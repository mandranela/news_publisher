"""
Contains pydantic models
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ArticleDetail(BaseModel):
    title: str
    paragraphs: list[str]
    photo_url: Optional[str]


class Article(BaseModel):
    title: str
    published_time: datetime
    link: str
