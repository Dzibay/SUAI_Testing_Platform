from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.user_service import UserService
from app.schemas.user_schema import UserSchema

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    schema = UserSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = UserService.get_user_by_email(validated_data['email'])
    if user:
        return jsonify({"message": "User already exists"}), 400

    new_user = UserService.create_user(validated_data)
    access_token = UserService.create_access_token(new_user)
    return jsonify({"access_token": access_token}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    schema = UserSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = UserService.get_user_by_email(validated_data['email'])
    if not user or not UserService.check_password(user, validated_data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = UserService.create_access_token(user)
    return jsonify({"access_token": access_token}), 200

@bp.route('/authenticate', methods=['GET'])
@jwt_required()
def authenticate():
    current_user_id = get_jwt_identity()
    user = UserService.get_user_by_id(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"message": "Token is valid", "user": {"id": user.id, "email": user.email}}), 200
