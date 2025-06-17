import functools
from flask import jsonify
import logging

def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Unhandled exception in {func.__name__}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
    return wrapper
