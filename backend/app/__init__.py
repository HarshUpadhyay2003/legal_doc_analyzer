from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.routes.routes import main  # ✅ Make sure this works
from app.database import init_db
import os

jwt = JWTManager()

def create_app(config=None):
    app = Flask(__name__)

    # Default configuration
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to something secure
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Optional: Tokens don't expire for now
    
    # Update with provided configuration
    if config:
        app.config.update(config)

    # 🔧 Optional: Enable CORS if frontend is on another origin
    CORS(app)

    # 🧱 Initialize DB
    init_db()

    # 🔐 Initialize JWT
    jwt.init_app(app)

    # 📦 Register routes
    app.register_blueprint(main)

    return app
