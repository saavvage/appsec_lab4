import os
import json
from functools import wraps
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

load_dotenv() 
SECRET_KEY = os.environ.get("SECRET_KEY", None)
DATABASE_URL = os.environ.get("DATABASE_URL", None)

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in environment variables")

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 

import logging
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


@app.errorhandler(Exception)
def handle_exception(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    app.logger.exception("Unhandled exception: %s", str(e))
    return jsonify({"error": "Internal Server Error"}), code

def require_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Invalid content type, application/json required"}), 415
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400
        request.parsed_json = data
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Secure HTTP server running"}), 200

@app.route("/info")
def info():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "features": ["safe-json", "no-debug", "env-secrets"]
    })

ALLOWED_ACTIONS = {"echo", "sum_numbers"}

@app.route("/deserialize", methods=["POST"])
@require_json
def deserialize_safe():
    data = request.parsed_json
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400
    action = data.get("action")
    payload = data.get("payload")
    if action not in ALLOWED_ACTIONS:
        return jsonify({"error": "Unsupported action"}), 400
    if action == "echo":
        if not isinstance(payload, dict) or "text" not in payload:
            return jsonify({"error": "payload.text required"}), 400
        text = payload["text"]
        if not isinstance(text, str) or len(text) > 1000:
            return jsonify({"error": "payload.text must be a string <=1000 chars"}), 400
        return jsonify({"result": text}), 200
    if action == "sum_numbers":
        if not isinstance(payload, dict) or "numbers" not in payload:
            return jsonify({"error": "payload.numbers required"}), 400
        numbers = payload["numbers"]
        if not isinstance(numbers, list) or not all(isinstance(n, (int, float)) for n in numbers):
            return jsonify({"error": "payload.numbers must be a list of numbers"}), 400
        return jsonify({"result": sum(numbers)}), 200
    return jsonify({"error": "Bad request"}), 400

@app.route("/auth-check")
def auth_check():
    return jsonify({"secret_configured": True}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
