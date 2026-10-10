
import os
import time
from collections import defaultdict
from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Use an environment variable for the signing secret.
secret = os.environ.get("FLASK_SECRET_KEY")
if not secret:
    raise RuntimeError("FLASK_SECRET_KEY must be configured")

app.config.update(
    SECRET_KEY=secret,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Local HTTP lab only; True in production HTTPS
)

USERS = {
    1: {
        "id": 1,
        "username": "alice",
        "password_hash": generate_password_hash("alice123"),
        "balance": 100,
        "is_admin": False,
    },
    2: {
        "id": 2,
        "username": "bob",
        "password_hash": generate_password_hash("bob123"),
        "balance": 50,
        "is_admin": False,
    },
    3: {
        "id": 3,
        "username": "carol",
        "password_hash": generate_password_hash("carol123"),
        "balance": 9999,
        "is_admin": True,
    },
}

ORDERS = {
    1: [{"order_id": "A-1", "item": "Keyboard", "total": 30}],
    2: [{"order_id": "B-1", "item": "Mouse", "total": 15}],
    3: [{"order_id": "C-1", "item": "Server rack", "total": 5000}],
}

ALLOWED_CREATE_FIELDS = {"username", "password"}
_next_id = 4

RATE_LIMIT = 5
RATE_WINDOW = 60
_attempts = defaultdict(list)


def current_user():
    # Do not trust X-User-Id.
    user_id = session.get("user_id")
    if not isinstance(user_id, int):
        return None
    return USERS.get(user_id)


def rate_limited(ip):
    now = time.time()
    _attempts[ip] = [
        t for t in _attempts[ip]
        if now - t < RATE_WINDOW
    ]
    if len(_attempts[ip]) >= RATE_LIMIT:
        return True
    _attempts[ip].append(now)
    return False


@app.post("/api/login")
def login():
    if rate_limited(request.remote_addr or "unknown"):
        return jsonify({"error": "too many requests"}), 429

    body = request.get_json(silent=True) or {}
    for user in USERS.values():
        if (
            user["username"] == body.get("username")
            and check_password_hash(
                user["password_hash"],
                str(body.get("password", ""))
            )
        ):
            session.clear()
            session["user_id"] = user["id"]
            return jsonify({
                "ok": True,
                "user_id": user["id"]
            }), 200

    return jsonify({"ok": False}), 401


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True}), 200


@app.get("/api/users/<int:uid>/orders")
def get_orders(uid):
    caller = current_user()

    if caller is None:
        return jsonify({
            "error": "authentication required"
        }), 401

    if caller["id"] != uid and not caller["is_admin"]:
        return jsonify({
            "error": "forbidden"
        }), 403

    return jsonify(ORDERS.get(uid, [])), 200


@app.post("/api/users")
def create_user():
    global _next_id

    body = request.get_json(silent=True) or {}
    user = {
        k: body[k]
        for k in ALLOWED_CREATE_FIELDS
        if k in body
    }

    if not isinstance(user.get("username"), str) or not isinstance(
        user.get("password"), str
    ):
        return jsonify({
            "error": "username and password required"
        }), 400

    new_user = {
        "id": _next_id,
        "username": user["username"],
        "password_hash": generate_password_hash(user["password"]),
        "balance": 0,
        "is_admin": False,
    }

    USERS[_next_id] = new_user
    _next_id += 1

    return jsonify({
        "id": new_user["id"],
        "username": new_user["username"],
        "balance": new_user["balance"],
        "is_admin": new_user["is_admin"],
    }), 201


@app.get("/")
def index():
    return "Week 10 SESSION-BASED SECURE API", 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002)
