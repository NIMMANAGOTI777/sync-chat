from datetime import datetime, timezone
from functools import wraps
from flask import jsonify, g, request
from backend.database.db import get_db


def require_session(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        token = request.headers.get("X-Session-Token")
        if not token:
            return jsonify({"error": "Missing session token"}), 401
        db = get_db()
        row = db.execute(
            """
            SELECT s.user_id, s.expires_at, u.phone, u.display_name, u.avatar_url
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
        if row is None or datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
            return jsonify({"error": "Invalid or expired session"}), 401
        g.user = dict(row)
        return handler(*args, **kwargs)

    return wrapped
