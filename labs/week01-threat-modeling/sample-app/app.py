"""
Tiny sample web app for Week 1 threat modeling.
You will NOT exploit this in Week 1 — you will draw a data-flow diagram
and apply STRIDE to its components (web client, app, SQLite DB, /upload).
"""
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024      # 5 MB request-body cap
ALLOWED_EXTENSIONS = {".txt", ".md", ".png", ".jpg", ".jpeg", ".pdf"}
DB = "notes.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    con.commit(); con.close()

@app.route("/notes", methods=["GET", "POST"])
def notes():
    con = sqlite3.connect(DB)
    if request.method == "POST":
        owner = request.json.get("owner", "anon")
        body = request.json.get("body", "")
        con.execute("INSERT INTO notes (owner, body) VALUES (?, ?)", (owner, body))
        con.commit()
    rows = con.execute("SELECT id, owner, body FROM notes").fetchall()
    con.close()
    return jsonify(rows)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if f is None or not f.filename:
        return {"error": "no file"}, 400

    raw = f.filename

    # 1. strip any path the client tried to smuggle in; keep only a safe bare name
    name = secure_filename(raw)
    ext = os.path.splitext(name)[1].lower()
    if not name or ext not in ALLOWED_EXTENSIONS:
        app.logger.warning("upload rejected: name=%r ext=%r from %s",
                           raw, ext, request.remote_addr)
        return {"error": "unsupported file type"}, 400

    # 2. the server chooses the stored name, not the client
    stored = "%s%s" % (uuid.uuid4().hex, ext)

    # 3. containment: the resolved path must stay inside UPLOAD_DIR
    root = os.path.realpath(UPLOAD_DIR)
    dest = os.path.realpath(os.path.join(root, stored))
    if os.path.commonpath([dest, root]) != root:
        return {"error": "invalid destination"}, 400

    f.save(dest)
    app.logger.info("upload stored=%s submitted=%r from=%s", stored, raw, request.remote_addr)
    return {"saved": stored}

@app.route("/files/<name>")
def files(name):
    return send_from_directory(UPLOAD_DIR, name)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)