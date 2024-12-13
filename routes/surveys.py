from flask import request, jsonify
from flask_cors import CORS

from models.surveys import create_survey, get_surveys, delete_survey, update_survey
from utils.jwt_helpers import get_jwt_token

def register_survey_routes(app, mysql, config):
    @app.before_request
    def log_request():
        print(f"Received {request.method} request for {request.path}")
        print(f"Headers: {request.headers}")

    @app.route('/api/v1/surveys', methods=['POST'])
    def create_survey_route():
        try:
            token = get_jwt_token(request)
            if not token:
                return jsonify({"error": "Token is required"}), 401
            return jsonify(create_survey(mysql, token, request.json, config))
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @app.route('/api/v1/surveys', methods=['GET'])
    def get_all_surveys():
        try:
            token = get_jwt_token(request)
            if not token:
                return jsonify({"error": "Token is required"}), 401
            return jsonify(get_surveys(mysql, token, config))
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @app.route('/api/v1/surveys/<survey_id>', methods=['DELETE'])
    def delete_survey_route(survey_id):
        try:
            token = get_jwt_token(request)
            if not token:
                return jsonify({"error": "Token is required"}), 401
            return jsonify(delete_survey(mysql, token, survey_id, config))
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @app.route('/api/v1/surveys/<survey_id>', methods=['PUT'])
    def update_survey_route(survey_id):
        try:
            token = get_jwt_token(request)
            if not token:
                return jsonify({"error": "Token is required"}), 401
            return jsonify(update_survey(mysql, token, request.json, config))
        except Exception as e:
            return jsonify({"error": str(e)}), 401

