from .auth import register_auth_routes
from .errorHandlers import register_error_handlers
from .surveys import register_survey_routes
from .health import register_health_routes

def register_routes(app, mysql, logger, config):
    register_auth_routes(app, mysql, config)
    register_survey_routes(app, mysql, config)
    register_health_routes(app, mysql, logger, config)
    register_error_handlers(app)
