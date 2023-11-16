from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import xml.etree.ElementTree as ET  # For XML generation
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth import auth_bp  # Import Auth Blueprint


app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')  # URL prefix for all routes in the Blueprint

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # Enable automatic tracking of modifications
db = SQLAlchemy(app)


class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Foreign key relationship
    author_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    cover_image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Method to fetch BookModel instance as a dictionary for generating XML response
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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


# Create the tables inside application context
with app.app_context():
    db.create_all()

@app.route('/books', methods=['GET'])
def get_books():
    books = BookModel.query.all()
    book_list = []

    accept_header = request.headers.get('Accept')

    if 'application/xml' in accept_header:
        # Return XML response
        xml_books = ET.Element('books')
        for book in books:
            book_data = book.as_dict()
            xml_book = ET.SubElement(xml_books, 'book')
            for key, value in book_data.items():
                ET.SubElement(xml_book, key).text = str(value)
        xml_response = ET.tostring(xml_books, encoding='utf-8', method='xml')
        return Response(xml_response, content_type='application/xml')

    else:
        # Return JSON response by default
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
@jwt_required()  # Protect the endpoint requiring access token
def publish_book():
    current_user = get_jwt_identity()

    if current_user == "_Darth Vader_":
        security_alerted = alert_wookie_security()
        return jsonify({'error': f'Darth Vader is not allowed to publish books. Wookie security alerted of an attempted data breech'}), 400  # Return error for invalid user

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
        return jsonify({'error': 'Unsupported Content-Type of POST request'})

def alert_wookie_security():
    # theoretical next steps for security breech
    security_alerted = True
    return security_alerted



# Create the tables inside application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
