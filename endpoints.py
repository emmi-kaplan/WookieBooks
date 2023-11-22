from flask import Flask, jsonify, request, Response, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, or_
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserModel, BookModel
import xml.etree.ElementTree as ET  # For XML generation
from create_app import create_app

books_bp = Blueprint('books', __name__)

'''Endpoint for returning all BookModels in db matching query parameters'''
@books_bp.route('/view', methods=['GET'])
def get_books():
    # Get query parameters for search functionality
    title = request.args.get('title') or ''
    author = request.args.get('author') or ''

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
    xml_format = request.headers.get('Accept') == 'application/xml'

    # Convert queried books to JSON or XML and return
    if xml_format:
        # Return XML response
        root = ET.Element('books')
        for book in books:
            book_element = book.serialize_xml()
            root.append(book_element)

        xml_response = ET.tostring(root, encoding='utf-8')
        return Response(xml_response, mimetype='application/xml'), 200

    # Return JSON response by default
    serialized_books = [book.serialize_json() for book in books]
    return jsonify(serialized_books), 200


user_bp = Blueprint('user', __name__)


'''Endpoint for returning UserModel for currently authenticated user'''
@user_bp.route('/details', methods=['GET'])
@jwt_required()  # Protect the endpoint requiring access token
def get_user_details():
    # Check header to determine JSON or XML response
    xml_format = request.headers.get('Accept') == 'application/xml'
    user = get_user_from_jwt()

    if xml_format:
        serialized_user = user.serialize_xml()
        return create_xml_response(serialized_user, 200)

    # Default return json
    serialized_user = user.serialize_json()
    return jsonify(serialized_user), 200


'''Endpoint for returning all BookModels published by currently authenticated user'''
@user_bp.route('/books', methods=['GET'])
@jwt_required()  # Protect the endpoint requiring access token
def get_user_books():
    # Check header to determine JSON or XML response
    xml_format = request.headers.get('Accept') == 'application/xml'

    # Get the books published by the user using the user ID and serialize
    user = get_user_from_jwt()
    serialized_books = []

    if xml_format:
        for book in user.user_books:
            serialized_books.append(book.serialize_xml())
        return create_xml_response(serialized_books, 200)

    # Default return json
    for book in user.user_books:
        serialized_books.append(book.serialize_json())
    return jsonify(serialized_books), 200


'''Endpoint for editing a BookModel previously published by currently authenticated user'''
@user_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()  # Protect the endpoint requiring access token
def update_book(book_id):
    # Check content type to determine JSON or XML response
    xml_format = request.headers.get('Content-Type') == 'application/xml'

    user = get_user_from_jwt()
    book = BookModel.query.get_or_404(book_id)  # Retrieve the book or return a 404 error if not found
    changed_fields = []

    if not book.author_id == user.id: # Check that the book to be modified was written by the logged-in user
        # Return error for invalid user
        if xml_format:
            return create_xml_message(build_invalid_user_message(user.username), 400)
        # Return json as default
        return jsonify({'error': build_invalid_user_message(user.username)}), 400

    # Get updated data from the request
    if xml_format:
        xml_data = request.data  # Get the XML data from the request
        xml_root = ET.fromstring(xml_data)

        # Define editable fields for BookModel
        editable_fields = ['title', 'description', 'cover_image_url', 'price']

        for elem in xml_root:
            tag = elem.tag.lower()
            if tag in editable_fields:  # Check if the attribute exists in the Book model
                setattr(book, tag, elem.text)  # Set the attribute value
                changed_fields.append(tag)
            else:
                return create_xml_message(f'Invalid element in XML: {tag}', 400)  # Return error for invalid element

        # Commit the changes to the database
        db.session.commit()
        changed_fields = ', '.join(changed_fields)
        return create_xml_message(f'Book fields {changed_fields} updated successfully', 200)

    # Default to json
    data = request.get_json()

    # Update the book attributes based on the request data
    if 'title' in data:
        book.title = data['title']
        changed_fields.append('title')
    if 'description' in data:
        book.description = data['description']
        changed_fields.append('description')
    if 'cover_image_url' in data:
        book.cover_image_url = data['cover_image_url']
        changed_fields.append('cover_image_url')
    if 'price' in data:
        book.price = data['price']
        changed_fields.append('price')

    # Commit the changes to the database
    db.session.commit()
    changed_fields = ', '.join(changed_fields)
    return jsonify({'message': f'Book fields {changed_fields} updated successfully'}), 200


'''Endpoint for deleting a BookModel previously published by currently authenticated user'''
@user_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    # Check content type to determine JSON or XML response
    xml_format = request.headers.get('Content-Type') == 'application/xml'

    user = get_user_from_jwt()
    book = BookModel.query.get_or_404(book_id)  # Retrieve the book or return a 404 error if not found

    if not book.author_id == user.id:  # Check that the book to be modified was written by the logged-in user
        # Return error for invalid user
        if xml_format:
            return create_xml_message(build_invalid_user_message(user.username), 400)
        # Return json as default
        return jsonify({'error': build_invalid_user_message(user.username)}), 400

    db.session.delete(book)  # Delete the book from the database
    db.session.commit()

    if xml_format:
        return create_xml_message(f'Book {book.title} deleted successfully', 200)
    return jsonify({'message': f'Book {book.title} deleted successfully'}), 200


'''Endpoint for posting a BookModel from the currently authenticated user'''
@user_bp.route('/publish-book', methods=['POST'])
@jwt_required()  # Protect the endpoint requiring access token
def publish_book():
    # Check content type to determine JSON or XML response
    xml_format = request.headers.get('Content-Type') == 'application/xml'

    user = get_user_from_jwt()

    new_book = BookModel()
    # Define required fields for BookModel
    required_fields = ['title', 'description', 'cover_image_url', 'price']

    if xml_format:
        xml_data = request.data  # Get the XML data from the request
        xml_root = ET.fromstring(xml_data)

        # Check for missing fields
        extracted_data = {elem.tag: elem.text for elem in xml_root}
        missing = validate_fields(extracted_data, required_fields)
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        # add author id
        setattr(new_book, 'author_id', user.id)

        for elem in xml_root:
            tag = elem.tag.lower()
            if tag in required_fields:  # Check if the attribute exists in the Book model
                setattr(new_book, tag, elem.text)  # Set the attribute value
            else:
                return create_xml_message(f'Invalid element in XML: {tag}',400)  # Return error for invalid element

        db.session.add(new_book)
        db.session.commit()

        return create_xml_message('Book published successfully', 201)

    # Assume json content type by default
    data = request.get_json()

    # Check for missing fields
    missing = validate_fields(data, required_fields)
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    title = data.get('title')
    description = data.get('description')
    author_id = user.id  # From jwt token provided in POST
    cover_image_url = data.get('cover_image_url')
    price = data.get('price')

    try:
        new_book = BookModel(title=title, description=description, author_id=author_id, cover_image_url=cover_image_url,
                         price=price)
    except Exception as e:
        return jsonify({'error': f'Invalid JSON body: {e}'}), 400

    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book published successfully'}), 201


'''Check that all fields are valid before creating model.'''
def validate_fields(data, required_fields):
    missing_fields = [field for field in required_fields if data.get(field) is None]
    return missing_fields


'''Get user model from jwt authentication in request.'''
def get_user_from_jwt():
    current_user_id = get_jwt_identity()  # Authenticated user_id
    return UserModel.query.filter_by(id=current_user_id).first()


'''Get invalid user message from user'''
def build_invalid_user_message(username):
    return f'Logged in user {username} does not match book author. Only the original author can edit or delete this book.'


'''Build xml response from serialized xml body'''
def create_xml_response(response_body, status):
    root = ET.Element("response")
    for chunk in response_body:
        root.append(chunk)
    xml_response = ET.tostring(root, encoding='utf-8')
    return Response(xml_response, mimetype='application/xml'), status


'''Build xml message or error message from message text'''
def create_xml_message(response_txt, status):
    root = ET.Element("response")
    if status == 400:
        error = ET.SubElement(root, "error")
        error.text = response_txt
    else:
        message = ET.SubElement(root, "message")
        message.text = response_txt

    xml_response = ET.tostring(root, encoding='utf-8')
    return Response(xml_response, mimetype='application/xml'), status

