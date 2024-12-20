from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.test_service import TestService

bp = Blueprint('sessions', __name__)

@bp.route('/tests/<string:test_id>/generate_link', methods=['POST'])
@jwt_required()
def generate_test_link(test_id):
    data = request.get_json()
    link_type = data.get('link_type')
    lifetime = data.get('lifetime')
    link = TestService.generate_test_link(test_id, link_type, lifetime)
    if link:
        return jsonify({"link": link}), 200
    else:
        return jsonify({"message": "Invalid link type"}), 400

@bp.route('/tests/<string:test_id>/close_link', methods=['POST'])
@jwt_required()
def close_test_link(test_id):
    data = request.get_json()
    link_type = data.get('link_type')
    TestService.close_test_link(test_id, link_type)
    return jsonify(), 204

@bp.route('/tests/token', methods=['GET'])
def get_test_by_token():
    token = request.args.get('token')
    test, error = TestService.get_test_by_token(token)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(test), 200

@bp.route('/tests/token/summary', methods=['GET'])
def get_test_summary_by_token():
    token = request.args.get('token')
    summary, error = TestService.get_test_summary_by_token(token)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(summary), 200

@bp.route('/tests/token/start', methods=['POST'])
def start_test():
    data = request.get_json()
    token = data.get('token')
    session_id = data.get('session_id')
    session_id, error = TestService.start_test(token, session_id=session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"session_id": session_id}), 200

@bp.route('/tests/token/continue', methods=['POST'])
def continue_test():
    data = request.get_json()
    token = data.get('token')
    session_id = data.get('session_id')
    session, error = TestService.continue_test(token, session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"session": session}), 200

@bp.route('/sessions/<string:session_id>/next_question', methods=['GET'])
def get_next_question(session_id):
    token = request.args.get('token')
    question, error = TestService.get_next_question(session_id, token)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(question), 200

@bp.route('/sessions/<string:session_id>', methods=['GET'])
def get_session(session_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header is missing or invalid"}), 401

    token = auth_header.split('Bearer ')[1]
    session, error = TestService.get_session(token, session_id)

    if error:
        return jsonify({"error": error}), 400

    if session:
        session_data = {
            "id": session.id,
            "test_id": session.test_id,
            "status": session.status,
            "current_question": session.current_question_id,
            "pass_time": str(session.time_spent)
        }
        return jsonify(session_data), 200
    else:
        return jsonify({"error": "Session not found"}), 404

@bp.route('/sessions', methods=['POST'])
def create_session():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header is missing or invalid"}), 401

    token = auth_header.split('Bearer ')[1]
    data = request.get_json()
    userInputs = data.get('userInputs')
    session_id, error = TestService.create_session(token, data, userInputs)

    if error:
        return jsonify({"error": error}), 400

    if session_id:
        return jsonify({"session_id": session_id}), 201
    else:
        return jsonify({"error": "Session not found"}), 404

@bp.route('/sessions/<string:session_id>/submit_answer', methods=['POST'])
def submit_answer(session_id):
    data = request.get_json()
    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    error = TestService.submit_answer(session_id, question_id, answer_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Answer submitted successfully"}), 200

@bp.route('/sessions/<string:session_id>/complete', methods=['POST'])
def complete_test(session_id):
    error = TestService.complete_test(session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Test completed successfully"}), 200
