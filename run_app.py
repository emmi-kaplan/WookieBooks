from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, or_
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserModel, BookModel
import xml.etree.ElementTree as ET  # For XML generation
from create_app import create_app

# Create the app in dev mode for rapid development and debug
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)