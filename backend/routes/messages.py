from flask import Blueprint, jsonify, g, request
from backend.database.db import get_db
from backend.utils.auth import require_session

bp = Blueprint("messages", __name__, url_prefix="/api/messages")


@bp.get("/<int:contact_user_id>")
@require_session
def get_messages(contact_user_id: int):
    db = get_db()
    rows = db.execute(
        """
        SELECT id, sender_user_id, receiver_user_id, body, delivered_at, seen_at, created_at
        FROM messages
        WHERE (sender_user_id = ? AND receiver_user_id = ?)
           OR (sender_user_id = ? AND receiver_user_id = ?)
        ORDER BY created_at ASC
        """,
        (g.user["user_id"], contact_user_id, contact_user_id, g.user["user_id"]),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("")
@require_session
def send_message():
    payload = request.get_json(silent=True) or {}
    receiver_user_id = payload.get("receiverUserId")
    body = (payload.get("body") or "").strip()
    if not receiver_user_id or not body:
        return jsonify({"error": "receiverUserId and body are required"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO messages(sender_user_id, receiver_user_id, body, delivered_at) VALUES(?, ?, ?, CURRENT_TIMESTAMP)",
        (g.user["user_id"], receiver_user_id, body),
    )
    message_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    db.commit()
    row = db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    return jsonify(dict(row)), 201


@bp.delete("/<int:message_id>")
@require_session
def delete_message(message_id: int):
    db = get_db()
    db.execute(
        "DELETE FROM messages WHERE id = ? AND sender_user_id = ?",
        (message_id, g.user["user_id"]),
    )
    db.commit()
    return jsonify({"ok": True})
