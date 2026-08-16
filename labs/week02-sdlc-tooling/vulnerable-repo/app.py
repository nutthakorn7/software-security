"""
REMEDIATED sample for Week 2 scanning practice.
Secure implementation using parameterized queries, safe subprocess calls, env vars, and bcrypt hashing.
"""
import sqlite3, os, subprocess, bcrypt
from flask import Flask, request

app = Flask(__name__)

# CWE-798 Fix: Retrieve secrets securely from environment variables
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

@app.route("/user")
def user():
    name = request.args.get("name", "")
    con = sqlite3.connect("app.db")
    # CWE-89 Fix: Parameterized query using ? placeholder
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
    return str(cur.fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # CWE-78 Fix: Pass arguments as a list and disable shell=True
    return subprocess.check_output(["ping", "-c", "1", host])

def store_password(pw):
    # CWE-327 Fix: Use bcrypt for strong password hashing with salt
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

if __name__ == "__main__":
    # CWE-489 Fix: Disable debug mode in production
    app.run(debug=False)

