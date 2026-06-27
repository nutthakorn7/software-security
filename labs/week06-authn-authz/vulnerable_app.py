"""Deliberately INSECURE — Week 6 Authentication & Access Control. Sandbox only; for authorized lab use."""
import jwt  # pip install pyjwt
from flask import Flask, request, jsonify

app = Flask(__name__)

# CWE-321/798: weak, hardcoded HMAC secret — trivially guessable / brute-forceable.
SECRET = "secret"

USERS = {"alice": "alicepw", "bob": "bobpw"}
# Orders keyed by id; each belongs to an owner.
ORDERS = {
    1: {"owner": "alice", "item": "Laptop", "total": 1200},
    2: {"owner": "bob", "item": "Phone", "total": 800},
}


@app.route("/login", methods=["POST"])
def login():
    user = request.json.get("user")
    pw = request.json.get("pw")
    if USERS.get(user) != pw:
        return jsonify(error="bad credentials"), 401
    # Token signed with the weak secret; no expiry/audience.
    token = jwt.encode({"sub": user}, SECRET, algorithm="HS256")
    return jsonify(token=token)


def current_user():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "")
    # CWE-347: improper signature verification.
    #   - 'none' is in the allowed algorithms -> an attacker can submit an UNSIGNED token.
    #   - the secret is the weak string "secret".
    data = jwt.decode(token, SECRET, algorithms=["HS256", "none"])
    return data.get("sub")


@app.route("/api/orders/<int:oid>")
def get_order(oid):
    current_user()  # authenticated, but result is ignored...
    order = ORDERS.get(oid)
    if not order:
        return jsonify(error="not found"), 404
    # CWE-639: IDOR — any logged-in user can read ANY order; no ownership check.
    return jsonify(order)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
