from flask import jsonify
from MySQLdb import OperationalError


def register_health_routes(app, mysql, logger, config):
    @app.route('/server/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "message": "Server is running!"})

    @app.route('/server/test_db', methods=['GET'])
    def test_db_connection():
        try:
            print(config.MYSQL_HOST)
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            cur.close()
            return jsonify({'status': 'success', 'result': result}), 200
        except OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            return jsonify(
                {'status': 'error', 'message': str(e), 'host': config.MYSQL_HOST, 'user': config.MYSQL_USER}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
