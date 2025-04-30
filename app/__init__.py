# app/__init__.py
from flask import Flask, jsonify
import logging
from marshmallow import ValidationError

from .business import business_bp
from .owner import owner_bp
from .user import user_bp
from .review import review_bp
from .db_connector import init_db, create_tables


logger = logging.getLogger()

def create_app(config=None):
    logger.info("Starting the Flask application")

    # Create and configure the Flask application
    app = Flask(__name__)

    # Load configuration if provided
    if config:
        app.config.from_mapping(config)

    # Set up logging
    level = app.config.get("LOG_LEVEL", logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    logger.debug("Initializing the SQL database connection pool")

    # Initialize the SQL database connection pool and create tables
    init_db()
    create_tables()

    # Register route blueprints
    app.register_blueprint(business_bp, url_prefix='/businesses')
    app.register_blueprint(owner_bp, url_prefix='/owners')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(review_bp, url_prefix='/reviews')

    # Error handling for marshmallow validation errors
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        logger.error(f"Validation error: {err.messages}")
        msg = "The request body is missing at least one of the required attributes"
        return jsonify({"Error": msg}), 400
    
    # Error handling for 400 Bad Request
    @app.errorhandler(400)
    def handle_400(err):
        logger.warning(f"Bad request: {err.description}")
        msg = err.description if err.description else "Bad Request"
        return {"Error": msg}, 400
    
    # Error handling for 401 Unauthorized
    @app.errorhandler(401)
    def handle_401(err):
        logger.warning(f"Unauthorized access: {err.description}")
        msg = err.description if err.description else "Unauthorized"
        return {"Error": msg}, 401
    
    # Error handling for 403 Forbidden
    @app.errorhandler(403)
    def handle_403(err):
        logger.warning(f"Forbidden access: {err.description}")
        msg = err.description if err.description else "Forbidden"
        return {"Error": msg}, 403
    
    # Error handling for 404 Not Found
    @app.errorhandler(404)
    def handle_404(err):
        logger.warning(f"Resource not found: {err.description}")
        msg = err.description if err.description else "Not Found"
        return {"Error": msg}, 404
    
    # Error handling for 409 Conflict
    @app.errorhandler(409)
    def handle_409(err):
        logger.warning(f"Conflict error: {err.description}")
        msg = err.description if err.description else "Conflict"
        return {"Error": msg}, 409
    
    # Error handling for 500 Internal Server Error
    @app.errorhandler(500)
    def handle_500(err):
        logger.error("Internal server error")
        msg = err.description if err.description else "Internal Server Error"
        return {"Error": msg}, 500
    
    # All other errors
    @app.errorhandler(Exception)
    def handle_exception(err):
        logger.exception(f"Unexpected error: {err}")
        msg = err.description if err.description else "An unexpected error occurred"
        return {"Error": msg}, Exception.status_code if hasattr(err, 'status_code') else 500
    
    logger.info("Flask application initialized successfully")   

    return app
