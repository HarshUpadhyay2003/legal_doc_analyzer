import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes.routes import main  # ✅ Make sure this works
from app.database import init_db
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

    # 🧱 Initialize DB
    init_db()

    # 🔐 Initialize JWT
    jwt.init_app(app)

    # 🔧 Enable CORS for specific origin
    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080"]}}, supports_credentials=True)

    # 📦 Register routes
    app.register_blueprint(main)

    return app
