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