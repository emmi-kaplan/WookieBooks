from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET  # For XML generation

db = SQLAlchemy()

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Relationship with books
    user_books = db.relationship('BookModel', backref='author', lazy=True)
    # Optional pseudonym for the author
    author_pseudonym = db.Column(db.String(50), unique=True, nullable=True)

    @property
    def display_name(self):
        # use the author_pseudonym if provided (not null) else use the name property
        return self.author_pseudonym or self.username

    def serialize_json(self):
        # For user details, just return a list of titles the author has published
        published_titles = []
        for book in self.user_books:
            published_titles.append(book.title)
        return {
                'id': self.id,
                'username': self.username,
                'password': self.password,  # consider not showing this info for security reasons?
                'published books': published_titles,
                'pseudonym': self.author_pseudonym or "No pseudonym set"  # alert users they haven't defined a pseudonym
            }

    def serialize_xml(self):
        user_element = ET.Element('user')

        # Get all attributes of the User instance
        user_attributes = self.__dict__

        # For user details, just return a list of titles the author has published
        published_titles = []
        for book in self.user_books:
            published_titles.append(book.title)

        # Add user_books element
        user_books_element = ET.SubElement(user_element, 'user_books')
        user_books_element.text = str(published_titles)

        for attribute, value in user_attributes.items():
            # Exclude internal attributes and methods as well as author_id
            if not attribute.startswith('_') and not callable(value) and not attribute.startswith('user_books'):
                attribute_element = ET.SubElement(user_element, attribute)
                attribute_element.text = str(value)

        return user_element


class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Foreign key relationship
    author_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    cover_image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def serialize_json(self):
        return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'author': self.author.display_name,
                'cover_image_url': self.cover_image_url,
                'price': self.price
            }

    def serialize_xml(self):
        book_element = ET.Element('book')

        # Get all attributes of the Book instance
        book_attributes = self.__dict__

        # Add author element to check for pseudonym
        author_element = ET.SubElement(book_element, 'author')
        author_element.text = self.author.display_name

        for attribute, value in book_attributes.items():
            # Exclude internal attributes and methods as well as author_id
            if not attribute.startswith('_') and not callable(value) and not attribute.startswith('author'):
                attribute_element = ET.SubElement(book_element, attribute)
                attribute_element.text = str(value)

        return book_element
