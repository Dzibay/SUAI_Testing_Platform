from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.services.question_service import QuestionService
from app.schemas.question_schema import QuestionSchema

bp = Blueprint('questions', __name__)

@bp.route('/tests/<string:test_id>/questions', methods=['POST'])
@jwt_required()
def create_question(test_id):
    data = request.get_json()
    try:
        validated_data = QuestionSchema().load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    validated_data['test_id'] = test_id
    new_question = QuestionService.create_question(validated_data)
    return jsonify({"message": "Question created successfully", "id": new_question.id}), 201

@bp.route('/questions/<string:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    data = request.get_json()
    schema = QuestionSchema(partial=True)  # Allow partial updates
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    updated_question = QuestionService.update_question(question_id, validated_data)
    return jsonify({"message": "Question updated successfully", "id": updated_question.id}), 200

@bp.route('/questions/<string:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    QuestionService.delete_question(question_id)
    return jsonify({"message": "Question deleted successfully"}), 200
