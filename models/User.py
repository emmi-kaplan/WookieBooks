from dataclasses import dataclass
from typing import List
from models.Book import Book


@dataclass
class User:
    id: int
    username: str
    email: str
    password: str
    books: List[Book]
