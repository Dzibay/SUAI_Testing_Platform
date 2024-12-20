import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from pytz import utc

from app.services.answer_service import AnswerService
from app.schemas.answer_schema import AnswerSchema
from app.models import Test, Question

bp = Blueprint('answers', __name__)

@bp.route('/questions/<string:question_id>/answers', methods=['POST'])
@jwt_required()
def create_answer(question_id):
    data = request.get_json()
    try:
        validated_data = AnswerSchema().load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    new_answer = AnswerService.create_answer(question_id, validated_data)
    return jsonify({"message": "Answer created successfully", "id": new_answer.id}), 201

@bp.route('/answers/<string:test_id>', methods=['GET'])
@jwt_required()
def get_answers(test_id):
    try:
        sessions = AnswerService.get_test_answers(test_id)
        if not sessions:
            return jsonify({"message": "No sessions found for the given test_id"}), 404
        sessions_data = [
            {
                "id": session.id,
                "status": session.status,
                "answers": session.answers,
                "time_spent": str(session.time_spent),
                "created_at": session.created_at,
                "user_inputs": session.user_inputs
            }
            for session in sessions
        ]

        return jsonify({"answers": sessions_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/answers/<string:answer_id>', methods=['DELETE'])
@jwt_required()
def delete_answer(answer_id):
    AnswerService.delete_answer(answer_id)
    return jsonify({"message": "Answer deleted successfully"}), 200
