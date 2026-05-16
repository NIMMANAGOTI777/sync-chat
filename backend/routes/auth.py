from datetime import datetime, timedelta, timezone
import secrets
from flask import Blueprint, jsonify, request
from backend.database.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    phone = payload.get("phone", "").strip()
    firebase_uid = payload.get("firebaseUid", "").strip()
    display_name = payload.get("displayName", "").strip() or "New User"

    if not phone or not firebase_uid:
        return jsonify({"error": "phone and firebaseUid are required"}), 400

    db = get_db()
    user = db.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
    if user is None:
        db.execute(
            "INSERT INTO users(phone, firebase_uid, display_name) VALUES(?, ?, ?)",
            (phone, firebase_uid, display_name),
        )
        user_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    else:
        user_id = user["id"]
        db.execute(
            "UPDATE users SET firebase_uid = ?, display_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (firebase_uid, display_name, user_id),
        )

    token = secrets.token_urlsafe(32)
    # Expire sessions after 7 days with an explicit UTC timestamp.
    expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(timespec="seconds")
    db.execute("INSERT INTO sessions(user_id, token, expires_at) VALUES(?, ?, ?)", (user_id, token, expires_at))
    db.commit()

    return jsonify({"sessionToken": token, "userId": user_id, "expiresAt": expires_at})


@bp.post("/logout")
def logout():
    payload = request.get_json(silent=True) or {}
    token = payload.get("sessionToken")
    if not token:
        return jsonify({"error": "sessionToken is required"}), 400
    db = get_db()
    db.execute("DELETE FROM sessions WHERE token = ?", (token,))
    db.commit()
    return jsonify({"ok": True})
