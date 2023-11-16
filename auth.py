from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import JWTManager, create_access_token
from models import db, UserModel

auth_bp = Blueprint('auth', __name__)

# Initialize JWTManager within the app context
jwt = JWTManager()

@auth_bp.record_once
def on_load(state):
    app = state.app
    jwt.init_app(app)

@auth_bp.route('/login', methods=['POST'])
def login():
    #db = auth_bp.db  # Access the db instance from auth_bp

    #from app import UserModel  # Import UserModel here to avoid circular import and multiple instances of db

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username"}), 400

    if not password:
        return jsonify({"msg": "Missing password"}), 400

    user = UserModel.query.filter_by(username=username).first()

    if user and user.password == password:  # Validate password (consider using hashing)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid credentials"}), 401




