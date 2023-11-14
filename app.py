from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from models.Book import Book
from models.User import User
import xml.etree.ElementTree as ET  # For XML generation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Foreign key relationship
    author_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    cover_image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    #author = db.relationship('UserModel', backref='books', lazy=True)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Relationship with books
    user_books = db.relationship('BookModel', backref='author', lazy=True)
    # Optional pseudonym for the author
    author_pseudonym = db.Column(db.String(50), unique=True, nullable=True)

    @property
    def display_name(self):
        # use the author_pseudonym if provided (not null) else use the name property
        return self.author_pseudonym or self.name


# Create the tables inside application context
with app.app_context():
    db.create_all()

books = ["Name of the Wind", "A Clash of Kings"]  # Placeholder for storing books

@app.route('/books', methods=['GET'])
def get_books():
    books = BookModel.query.all()
    book_list = []

    for book in books:
        book_data = {
            'id': book.id,
            'title': book.title,
            'description': book.description,
            'author_id': book.author_id,
            'cover_image_url': book.cover_image_url,
            'price': book.price
        }
        book_list.append(book_data)

    return jsonify(book_list)

@app.route('/user/publish-book', methods=['POST'])
def publish_book():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/xml':
        xml_data = request.data  # Get the XML data from the request
        xml_root = ET.fromstring(xml_data)

        new_book = BookModel()
        book_attributes = [prop.key for prop in inspect(BookModel).attrs]  # Get attributes of the Book model

        for elem in xml_root:
            tag = elem.tag.lower()
            if tag in book_attributes:  # Check if the attribute exists in the Book model
                setattr(new_book, tag, elem.text)  # Set the attribute value
            else:
                return jsonify({'error': f'Invalid element in XML: {tag}'}), 400  # Return error for invalid element

        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': 'Book added successfully from XML'}), 201

    elif content_type == 'application/json':
        data = request.get_json()

        title = data.get('title')
        description = data.get('description')
        author_id = data.get('author_id')  # Assuming you provide the author's ID
        cover_image_url = data.get('cover_image_url')
        price = data.get('price')

        new_book = BookModel(title=title, description=description, author_id=author_id, cover_image_url=cover_image_url,
                             price=price)
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': 'Book published successfully from JSON'}), 201

    else:
        return jsonify({'error': 'Unsupported Content-Type'})



if __name__ == '__main__':
    app.run(debug=True)
