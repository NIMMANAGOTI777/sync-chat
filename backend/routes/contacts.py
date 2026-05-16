from flask import Blueprint, jsonify, g, request
from backend.database.db import get_db
from backend.utils.auth import require_session

bp = Blueprint("contacts", __name__, url_prefix="/api/contacts")


@bp.get("")
@require_session
def list_contacts():
    search = (request.args.get("q") or "").strip()
    db = get_db()
    rows = db.execute(
        """
        SELECT c.id, u.id AS user_id, u.phone, u.display_name, u.avatar_url, c.created_at
        FROM contacts c
        JOIN users u ON u.id = c.contact_user_id
        WHERE c.owner_user_id = ? AND (? = '' OR u.phone LIKE ? OR u.display_name LIKE ?)
        ORDER BY c.created_at DESC
        """,
        (g.user["user_id"], search, f"%{search}%", f"%{search}%"),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("")
@require_session
def add_contact():
    payload = request.get_json(silent=True) or {}
    phone = (payload.get("phone") or "").strip()
    if not phone:
        return jsonify({"error": "phone is required"}), 400

    db = get_db()
    contact = db.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
    if contact is None:
        return jsonify({"error": "Contact not found"}), 404
    if contact["id"] == g.user["user_id"]:
        return jsonify({"error": "You cannot add yourself"}), 400

    db.execute(
        "INSERT OR IGNORE INTO contacts(owner_user_id, contact_user_id) VALUES(?, ?)",
        (g.user["user_id"], contact["id"]),
    )
    db.commit()
    return jsonify({"ok": True})


@bp.delete("/<int:contact_id>")
@require_session
def delete_contact(contact_id: int):
    db = get_db()
    db.execute("DELETE FROM contacts WHERE id = ? AND owner_user_id = ?", (contact_id, g.user["user_id"]))
    db.commit()
    return jsonify({"ok": True})
