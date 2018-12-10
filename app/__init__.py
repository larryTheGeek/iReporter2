import os
from flask_jwt_extended import JWTManager
from instance.config import Config
import datetime
from flask import Flask, Blueprint, request, jsonify
from instance.config import app_config
from db_config import create_tables
from app.api.v2 import version_two as v2

jwt = JWTManager()
timeout = datetime.timedelta(4000)


def create_app(config_name='testing'):
    app = Flask(__name__, instance_relative_config=True)
    app.url_map.strict_slashes = False
    app.config.from_object(app_config['testing'])
    app.config.from_pyfile('config.py')
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timeout
    jwt.init_app(app)
    create_tables()
    app.register_blueprint(v2)

    @app.errorhandler(404)
    def invalid_endpoint(error=None):
        """Handle wrong endpoints """
        return jsonify({
            'Message': '{} is not a valid url'.format(request.url)
        }), 404

    @app.errorhandler(405)
    def wrong_method(error=None):
        """Handle wrong methods for an endpoint """
        request_method = request.method
        return jsonify({
            'Message': 'The {} method is not allowed for this endpoint'
            .format(request_method)}), 405

    @app.errorhandler(400)
    def wrong_request(error=None):
        """Handle wrong requests for an endpoint """
        return jsonify({
            'Message': 'This endpoint supports JSON requests only.'}), 400

    @app.errorhandler(500)
    def server_error(error=None):
        """Handle internal server error for an endpoint """
        return jsonify({
            'Message': 'Verify if the request causes a server error'}), 500

    return app
