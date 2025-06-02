import functools
from flask import jsonify

def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Optional: log the error here (using logging or print)
            print(f"Unhandled exception in {func.__name__}: {e}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
    return wrapper
