from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, or_
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserModel, BookModel
import xml.etree.ElementTree as ET  # For XML generation

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # Enable automatic tracking of modifications
app.config['JWT_SECRET_KEY'] = 'use-the-force-luke'  # Set your secret key here

# Initialize the db with the app
db.init_app(app)

# Import and Register Blueprints
from auth import auth_bp
auth_bp.db = db
app.register_blueprint(auth_bp, url_prefix='/auth')

# Create the tables inside application context
with app.app_context():
    db.create_all()


'''Endpoint for returning all BookModels in db matching query parameters'''
@app.route('/books', methods=['GET'])
def get_books():
    # Get query parameters for search functionality
    title = request.args.get('title')
    author = request.args.get('author')

    # Query both tables based on search parameters, search for author in both username and psuedonym
    books_query = BookModel.query.join(UserModel).filter(
        or_(
            BookModel.title.ilike(f'%{title}%'),
            UserModel.username.ilike(f'%{author}%'),
            UserModel.author_pseudonym.ilike(f'%{author}%')
        )
    )

    books = books_query.all() # return all matching books

    # Check header to determine JSON or XML response
    accept_header = request.headers.get('Accept')

    # Convert queried books to JSON or XML and return
    if 'application/xml' in accept_header:
        # Return XML response
        root = ET.Element('books')
        for book in books:
            book_element = book.serialize_xml()
            root.append(book_element)

        xml_response = ET.tostring(root, encoding='utf-8')
        return Response(xml_response, mimetype='application/xml'), 200
    else:
        # Return JSON response by default
        serialized_books = [book.serialize_json() for book in books]
        return jsonify(serialized_books), 200


'''Endpoint for returning UserModel for currently authenticated user'''
@app.route('/user/details', methods=['GET'])
@jwt_required()  # Protect the endpoint requiring access token
def get_user_details():
    current_user_id = get_jwt_identity()  # Authenticated user_id

    # Get the user details using the user ID and serialize
    user = UserModel.query.filter_by(id=current_user_id).first()
    serialized_user = user.serialize_json()
    return jsonify(serialized_user), 200


'''Endpoint for returning all BookModels published by currently authenticated user'''
@app.route('/user/books', methods=['GET'])
@jwt_required()  # Protect the endpoint requiring access token
def get_user_books():
    current_user_id = get_jwt_identity()  # Authenticated user_id

    # Get the books published by the user using the user ID and serialize
    user = UserModel.query.filter_by(id=current_user_id).first()
    serialized_books = []
    for book in user.user_books:
        serialized_books.append(book.serialize_json())
    return jsonify(serialized_books), 200


'''Endpoint for posting a BookModel from the currently authenticated user'''
@app.route('/user/publish-book', methods=['POST'])
@jwt_required()  # Protect the endpoint requiring access token
def publish_book():
    current_user_id = get_jwt_identity()  # Authenticated user_id
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
        author_id = current_user_id  # From jwt token provided in POST
        cover_image_url = data.get('cover_image_url')
        price = data.get('price')

        new_book = BookModel(title=title, description=description, author_id=author_id, cover_image_url=cover_image_url,
                             price=price)
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': 'Book published successfully from JSON'}), 201

    else:
        return jsonify({'error': 'Unsupported Content-Type of POST request'})


# Create the tables inside application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
