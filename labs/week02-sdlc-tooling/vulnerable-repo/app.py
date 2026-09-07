"""
Deliberately INSECURE sample for Week 2 scanning practice.
Do NOT copy these patterns into real code. Find them with SAST + secret scanning.

Task 8 (defend/fix): all five planted flaws remediated below, each still
commented with its CWE so the before/after mapping stays clear.
"""
import os, sqlite3, hashlib, subprocess
from flask import Flask, request

app = Flask(__name__)

# CWE-798 fix: read secrets from the environment instead of hardcoding them —
# nothing sensitive lives in the source file or git history anymore. Set
# AWS_SECRET_ACCESS_KEY and DB_PASSWORD in the environment before running.
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

@app.route("/user")
def user():
    name = request.args.get("name", "")
    con = sqlite3.connect("app.db")
    # CWE-89 fix: parameterized query — the "?" placeholder keeps user input
    # as pure data, so it can never be interpreted as part of the SQL command.
    q = "SELECT * FROM users WHERE name = ?"
    return str(con.execute(q, (name,)).fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # CWE-78 fix: no shell=True, argument list instead of a concatenated
    # string — the shell never re-parses `host`, so it can't inject commands.
    return subprocess.check_output(["ping", "-c", "1", host])

def store_password(pw):
    # CWE-327 fix: hashlib.scrypt (slow, salted) instead of fast, unsalted md5.
    # Store the salt alongside the hash — it's needed again to verify a login.
    salt = os.urandom(16)
    digest = hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)
    return salt.hex() + ":" + digest.hex()

if __name__ == "__main__":
    app.run(debug=False)  # CWE-489 fix: never run the debugger in production
