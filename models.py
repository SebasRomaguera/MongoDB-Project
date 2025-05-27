# models.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Genre(str, Enum):
    fiction = "fiction"
    nonfiction = "nonfiction"
    fantasy = "fantasy"
    science_fiction = "science_fiction"
    biography = "biography"

class Book(BaseModel):
    title: str
    author: str
    isbn: str
    genre: Genre
    published_year: int
    available: bool

class UpdateBookDTO(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[Genre] = None
    published_year: Optional[int] = None
    available: Optional[bool] = None
