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
