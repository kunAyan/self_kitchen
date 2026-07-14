"""Flask application entry point."""

import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from config import config
from extensions import db, jwt
from models import User  # noqa: F401 - needed for JWT user lookup
from api import register_blueprints


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure all upload directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    for folder in ['UPLOAD_FOLDER', 'UPLOAD_DISHES', 'UPLOAD_AVATARS',
                   'UPLOAD_STORE', 'UPLOAD_DIARY']:
        os.makedirs(app.config.get(folder, app.config['UPLOAD_FOLDER']),
                    exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Serve uploaded images (supports subdirectories)
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # JWT user loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    # Register API blueprints
    register_blueprints(app)

    # Create tables on first request
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5099, debug=True)
