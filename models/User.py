from dataclasses import dataclass
from typing import List, Optional
from models.Book import Book


@dataclass
class User:
    id: int
    name: str
    password: str
    books: List[Book]
    author_pseudonym: Optional[str] = None
