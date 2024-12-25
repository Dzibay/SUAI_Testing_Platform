from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import decode_token
from app.services.test_service import TestService

bp = Blueprint('sessions', __name__)


def extract_auth():
    """Helper function to extract token or public key."""
    auth_header = request.headers.get('Authorization')
    public_key = request.headers.get('Public-Key')  # Ожидаем публичный ключ в заголовке Public-Key

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
        try:
            decoded = decode_token(token)
            return {"token": token, "payload": decoded, "public_key": None}, None
        except Exception as e:
            return None, f"Invalid token: {str(e)}"

    return None, "Authorization header is missing or invalid"


@bp.route('/sessions', methods=['POST'])
def create_session():
    auth, error = extract_auth()
    if error:
        return jsonify({"error": error}), 401

    # Извлечение test_id из токена или аргументов
    test_id = None
    if auth["payload"]:
        test_id = auth["payload"].get("test_id")

    if not test_id:
        return jsonify({"error": "Test ID is missing"}), 400

    data = request.get_json()
    user_inputs = data.get('userInputs')

    sessionId = TestService.create_session(token=auth["token"], session_data={}, userInputs=user_inputs)

    return jsonify({
        "session_id": sessionId
    }), 201

@bp.route('/sessions/<string:session_id>', methods=['POST'])
def init_session(session_id):
    auth, error = extract_auth()
    if error:
        return jsonify({"error": error}), 401

    # Извлечение test_id из токена или аргументов
    test_id = None
    if auth["payload"]:
        test_id = auth["payload"].get("test_id")

    if not test_id:
        return jsonify({"error": "Test ID is missing"}), 400

    data = request.get_json()
    user_inputs = data.get('userInputs')

    sessionId = TestService.init_session(token=auth["token"], session_id=session_id)

    return jsonify({
        "session_id": sessionId
    }), 201

@bp.route('/sessions/<string:session_id>/start', methods=['POST'])
def start_test(session_id):
    auth, error = extract_auth()
    if error:
        return jsonify({"error": error}), 401
    print(session_id)
    question, error = TestService.start_test(token = auth['token'], session_id=session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(question), 200

@bp.route('/sessions/<string:session_id>/next', methods=['GET'])
def next_question(session_id):
    auth, error = extract_auth()
    if error:
        return jsonify({"error": error}), 401
    question, error = TestService.get_next_question(token = auth['token'], session_id=session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(question), 200

@bp.route('/sessions/<string:session_id>/submit_answer', methods=['POST'])
def submit_answer(session_id):
    auth, error = extract_auth()
    data = request.get_json()
    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    if error:
        return jsonify({"error": error}), 401
    TestService.submit_answer(session_id=session_id, question_id=question_id, answer_id=answer_id)
    return jsonify('Submitted successful'), 200


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

@bp.route('/sessions/<string:session_id>/complete', methods=['POST'])
def complete_test(session_id):
    error = TestService.complete_test(session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Test completed successfully"}), 200

@bp.route('/sessions/<string:session_id>/continue', methods=['POST'])
def continue_test(session_id):
    auth, error = extract_auth()
    session, error = TestService.continue_test(auth['token'], session_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"session": session}), 200