from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from app import UserModel, db

auth_bp = Blueprint('auth', __name__)

auth_bp.config = {
    'JWT_SECRET_KEY': 'super-secret'  # Change this to a secure secret key
}

jwt = JWTManager(auth_bp)

@auth_bp.route('/login', methods=['POST'])
def login():
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




