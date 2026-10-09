"""Run with python app.py; local lab server on port 5000."""
import sqlite3
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from database import create_db_table, insert_user, get_users, get_user_by_id, update_user, delete_user, patch_user

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
create_db_table()


def validated_user(update=False):
    user = request.get_json()
    if not isinstance(user, dict):
        raise ValueError("The JSON body must be an object")
    fields = ("name", "email", "phone", "address", "country")
    for key in fields:
        if not isinstance(user.get(key), str) or not user[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    result = {key: user[key].strip() for key in fields}
    if update:
        if type(user.get("user_id")) is not int or user["user_id"] < 1:
            raise ValueError("user_id must be a positive integer")
        result["user_id"] = user["user_id"]
    return result


@app.errorhandler(ValueError)
def invalid_data(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(HTTPException)
def http_error(error):
    response = error.get_response()
    response.data = app.json.dumps({"error": error.description})
    response.content_type = "application/json"
    return response


@app.errorhandler(sqlite3.Error)
def database_error(error):
    app.logger.exception("Database operation failed")
    return jsonify(error="Database operation failed"), 500

@app.get("/")
def home():
    return redirect("/api/users")

@app.get("/api/users")
def api_get_users():
    return jsonify(get_users())


@app.get("/api/users/<int:user_id>")
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    return jsonify(user) if user else (jsonify(error="User not found"), 404)


@app.post("/api/users/add")
def api_add_user():
    return jsonify(insert_user(validated_user())), 201


@app.put("/api/users/update")
def api_update_user():
    user = update_user(validated_user(update=True))
    return jsonify(user) if user else (jsonify(error="User not found"), 404)


@app.delete("/api/users/delete/<int:user_id>")
def api_delete_user(user_id):
    if delete_user(user_id):
        return jsonify(status="User deleted successfully")
    return jsonify(error="User not found"), 404


@app.patch("/api/users/<int:user_id>")
def api_patch_user(user_id):
    changes = request.get_json()
    fields = {"name", "email", "phone", "address", "country"}
    if not isinstance(changes, dict) or not changes:
        raise ValueError("Provide a non-empty JSON object")
    if set(changes) - fields:
        raise ValueError("Only name, email, phone, address, and country can be patched")
    for key, value in changes.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
    user = patch_user(user_id, {key: value.strip() for key, value in changes.items()})
    return jsonify(user) if user else (jsonify(error="User not found"), 404)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
