from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-not-secret-override-in-prod"
socketio = SocketIO(app, async_mode="eventlet")


@app.route("/")
def index():
    return "Live Quiz — under construction"


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
