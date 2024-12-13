from flask import jsonify

from models.auth import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError, TokenExpiredError, \
    InvalidTokenError


def register_error_handlers(app):
    @app.errorhandler(InvalidCredentialsError)
    def handle_invalid_credentials(error):
        return jsonify({"error": str(error)}), 401

    @app.errorhandler(UserAlreadyExistsError)
    def handle_user_already_exists(error):
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(UserNotFoundError)
    def handle_user_not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(TokenExpiredError)
    def handle_token_expired(error):
        return jsonify({"error": str(error)}), 401

    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        app.logger.error(f"Unhandled error: {error}")
        return jsonify({"error": "Internal server error"}), 500
