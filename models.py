from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Genre(str, Enum):
    fiction = "fiction"
    nonfiction = "nonfiction"
    fantasy = "fantasy"
    science_fiction = "science_fiction"
    biography = "biography"

class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=13)
    genre: Genre
    published_year: int = Field(..., ge=1800, le=2100)
    available: bool

class UpdateBookDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[Genre] = None
    published_year: Optional[int] = Field(None, ge=1800, le=2100)
    available: Optional[bool] = None
