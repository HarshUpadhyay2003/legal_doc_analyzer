import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes.routes import main  # ✅ Make sure this works
import logging

jwt = JWTManager()

def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object) # Use from_object to load config from the class instance

    # Configure logging
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # 🔐 Initialize JWT
    jwt.init_app(app)

    # 🔧 Enable CORS for all origins and all methods (development only)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # 📦 Register routes
    app.register_blueprint(main)

    return app
