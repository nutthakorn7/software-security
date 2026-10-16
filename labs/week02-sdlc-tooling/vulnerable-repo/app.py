"""
Week 2 Task 8 — remediated version of the deliberately insecure sample.
Five planted flaws fixed: CWE-89, CWE-78, CWE-798, CWE-327, CWE-489.
"""
import os
import sqlite3
import subprocess

import bcrypt
from flask import Flask, request

app = Flask(__name__)

# FIX 3 (CWE-798): secrets read from the environment, never hardcoded.
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

@app.route("/user")
def user():
    name = request.args.get("name", "")
    con = sqlite3.connect("app.db")
    # FIX 1 (CWE-89): parameterised query — the value is bound, never parsed as SQL.
    rows = con.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchall()
    con.close()
    return str(rows)

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # FIX 2 (CWE-78): no shell, argument list, and the host is allow-listed.
    if not all(c.isalnum() or c in ".-" for c in host) or not host:
        return {"error": "invalid host"}, 400
    return subprocess.check_output(["ping", "-c", "1", host])

def store_password(pw):
    # FIX 4 (CWE-327): bcrypt — salted and deliberately slow, unlike MD5.
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw, stored):
    return bcrypt.checkpw(pw.encode(), stored.encode())

if __name__ == "__main__":
    # FIX 5 (CWE-489): debug off by default; opt in only via the environment.
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")