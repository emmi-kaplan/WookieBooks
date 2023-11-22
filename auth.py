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
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username"}), 400

    if not password:
        return jsonify({"msg": "Missing password"}), 400

    # Check user for dark side affiliation
    if username in sith_member_usernames:
        security_alerted = alert_wookie_security()
        # Return error for invalid user
        return jsonify({'error': f'Sith members are not allowed to publish or edit books. '
                                 f'Wookie security alerted of an attempted data breech'}), 400

    user = UserModel.query.filter_by(username=username).first()

    if user and user.password == password:  # Validate password (consider using hashing)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid credentials"}), 401

def alert_wookie_security():
    # theoretical next steps for security breech
    security_alerted = True
    return security_alerted

# if we find other members of the sith, add them here
sith_member_usernames = ["_Darth Vader_"]


