from flask import Blueprint, jsonify, request, g
from backend.database.db import get_db
from backend.utils.auth import require_session

bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@bp.get("")
@require_session
def get_profile():
    return jsonify(g.user)


@bp.patch("")
@require_session
def update_profile():
    payload = request.get_json(silent=True) or {}
    display_name = (payload.get("displayName") or "").strip()
    avatar_url = (payload.get("avatarUrl") or "").strip()
    db = get_db()
    db.execute(
        "UPDATE users SET display_name = ?, avatar_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (display_name or g.user["display_name"], avatar_url, g.user["user_id"]),
    )
    db.commit()
    row = db.execute("SELECT id AS user_id, phone, display_name, avatar_url FROM users WHERE id = ?", (g.user["user_id"],)).fetchone()
    return jsonify(dict(row))
