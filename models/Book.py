from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    description: str
    author_id: int  # Using the User model for the author
    cover_image_url: str  # Assume a URL for simplicity
    price: float

