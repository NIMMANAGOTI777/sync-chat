from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from backend.database.db import close_db, init_db
from backend.routes.auth import bp as auth_bp
from backend.routes.contacts import bp as contacts_bp
from backend.routes.messages import bp as messages_bp
from backend.routes.profile import bp as profile_bp
from backend.sockets.events import register_socket_events

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")


def create_app(test_config=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.update(
        SECRET_KEY="dev",
        DATABASE=str(Path(__file__).resolve().parent / "database" / "chat.db"),
    )
    if test_config:
        app.config.update(test_config)

    CORS(app, supports_credentials=True)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(profile_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    socketio.init_app(app)
    register_socket_events(socketio)
    return app


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
