"""
Remediated Sample Code for Week 2 Lab.
Vulnerabilities remediated:
- CWE-798: Loaded credentials from environment variables.
- CWE-89: Parameterized SQL query with sqlite3 tuple placeholders.
- CWE-78: Passed command arguments as a list with shell=False.
- CWE-327: Replaced MD5 with salted bcrypt hashing.
- CWE-489: Controlled debug mode via FLASK_DEBUG environment variable.
"""
import os
import sqlite3
import subprocess
import bcrypt
from flask import Flask, request

app = Flask(__name__)

# Fix CWE-798: Read secrets from system environment variables
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

@app.route("/user")
def user():
    name = request.args.get("name", "")
    con = sqlite3.connect("app.db")
    # Fix CWE-89: Parameterized query using '?' placeholder
    q = "SELECT * FROM users WHERE name = ?"
    return str(con.execute(q, (name,)).fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # Fix CWE-78: Pass arguments as list array without shell=True
    return subprocess.check_output(["ping", "-c", "1", host], shell=False)

def store_password(pw):
    # Fix CWE-327: Replace weak MD5 hash with salted bcrypt
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

if __name__ == "__main__":
    # Fix CWE-489: Dynamic debug flag configuration
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")