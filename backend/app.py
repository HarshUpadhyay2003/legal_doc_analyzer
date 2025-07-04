import os
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app
from config import config

# Get environment from environment variable
env = os.environ.get('FLASK_ENV', 'development')
flask_app = create_app(config[env])

app = FastAPI()
app.mount("/", WSGIMiddleware(flask_app))