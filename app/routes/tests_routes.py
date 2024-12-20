from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.test_service import TestService
from app.schemas.test_schema import TestSchema

bp = Blueprint('tests', __name__)

@bp.route('/tests', methods=['POST'])
@jwt_required()
def create_test():
    data = request.get_json()
    try:
        validated_data = TestSchema().load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user_id = get_jwt_identity()
    new_test = TestService.create_test(user_id, validated_data)
    return jsonify({"message": "Test created successfully", "id": new_test.id}), 201

@bp.route('/tests/<string:test_id>', methods=['PUT'])
@jwt_required()
def update_test(test_id):
    data = request.get_json()
    schema = TestSchema(partial=True)  # Allow partial updates
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user_id = get_jwt_identity()
    updated_test = TestService.update_test(test_id, validated_data, user_id)
    return jsonify({"message": "Test updated successfully", "id": updated_test.id}), 200

@bp.route('/tests/<string:test_id>', methods=['DELETE'])
@jwt_required()
def delete_test(test_id):
    TestService.delete_test(test_id)
    return jsonify({"message": "Test deleted successfully"}), 200

@bp.route('/tests', methods=['GET'])
@jwt_required()
def get_all_tests():
    token_user_id = get_jwt_identity()
    tests = TestService.get_all_tests(token_user_id)
    return jsonify(tests), 200

@bp.route('/tests/<string:test_id>', methods=['GET'])
@jwt_required()
def get_test_by_id(test_id):
    user_id = get_jwt_identity()
    test_data = TestService.get_test_by_id(test_id, user_id)
    return jsonify(test_data), 200

@bp.route('/tests/with_questions_and_answers', methods=['POST'])
@jwt_required()
def create_test_with_questions_and_answers():
    data = request.get_json()
    # try:
    #     validated_data = TestSchema().load(data)
    # except ValidationError as err:
    #     return jsonify({"errors": err.messages}), 400

    user_id = get_jwt_identity()
    questions_data = data.get('questions', [])
    data['user_id'] = user_id
    new_test = TestService.create_test_with_questions_and_answers(data, questions_data)
    return jsonify({"message": "Test with questions and answers created successfully", "id": new_test.id}), 201

@bp.route('/tests/<string:test_id>/with_questions_and_answers', methods=['PUT'])
@jwt_required()
def update_test_with_questions_and_answers(test_id):
    data = request.get_json()
    # schema = TestSchema(partial=True)  # Allow partial updates
    # try:
    #     validated_data = schema.load(data)
    # except ValidationError as err:
    #     return jsonify({"errors": err.messages}), 400

    user_id = get_jwt_identity()
    questions_data = data.get('questions', [])
    data['user_id'] = user_id
    print('Here')
    updated_test = TestService.update_test_with_questions_and_answers(test_id, data, questions_data)
    return jsonify({"message": "Test with questions and answers updated successfully", "id": updated_test.id}), 200
