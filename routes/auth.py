from flask import request, jsonify
from models.auth import login_user, register_user, authenticate_user, InvalidCredentialsError, UserAlreadyExistsError, \
    UserNotFoundError, TokenExpiredError, InvalidTokenError
from utils.jwt_helpers import get_jwt_token


def register_auth_routes(app, mysql, config):
    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        try:
            email = request.json.get('email')
            password = request.json.get('password')
            if not email or not password:
                return jsonify({"error": "Email and password are required"}), 400
            return jsonify(login_user(mysql, config, email, password))
        except InvalidCredentialsError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error(f"Error during login: {e}")
            return jsonify({"error": "An error occurred during login"}), 500

    @app.route('/api/v1/auth/register', methods=['POST'])
    def register():
        try:
            email = request.json.get('email')
            password = request.json.get('password')
            if not email or not password:
                return jsonify({"error": "Email and password are required"}), 400
            return jsonify(register_user(mysql, config, email, password))
        except UserAlreadyExistsError as e:
            return jsonify({"error": str(e)}), 409
        except Exception as e:
            app.logger.error(f"Error during registration: {e}")
            return jsonify({"error": "An error occurred during registration"}), 500

    @app.route('/api/v1/auth/authentication', methods=['POST'])
    def authentication():
        try:
            token = get_jwt_token(request)
            if not token:
                return jsonify({"error": "Token is required"}), 400
            return jsonify(authenticate_user(mysql, config, token))
        except UserNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except TokenExpiredError as e:
            return jsonify({"error": str(e)}), 401
        except InvalidTokenError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error(f"Error during authentication: {e}")
            return jsonify({"error": "An error occurred during authentication"}), 500


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500
