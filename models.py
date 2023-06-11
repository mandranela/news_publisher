from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ArticleDetail(BaseModel):
    title: str
    paragraphs: List[str]
    photo_url: Optional[str]


class Article(BaseModel):
    title: str
    published_time: datetime
    link: str
