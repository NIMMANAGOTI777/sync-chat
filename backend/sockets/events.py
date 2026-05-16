from datetime import datetime, timezone
from flask import request
from flask_socketio import emit, join_room
from backend.database.db import get_db

ONLINE_USERS = set()


def register_socket_events(socketio):
    @socketio.on("connect")
    def on_connect():
        pass

    @socketio.on("presence:join")
    def on_presence_join(data):
        user_id = str(data.get("userId", ""))
        if not user_id:
            return
        join_room(user_id)
        ONLINE_USERS.add(user_id)
        emit("presence:update", {"userId": user_id, "online": True}, broadcast=True)

    @socketio.on("typing")
    def on_typing(data):
        emit("typing", data, room=str(data.get("toUserId")), include_self=False)

    @socketio.on("message:send")
    def on_message_send(data):
        sender = int(data.get("senderUserId"))
        receiver = int(data.get("receiverUserId"))
        body = (data.get("body") or "").strip()
        if not body:
            return
        db = get_db()
        db.execute(
            "INSERT INTO messages(sender_user_id, receiver_user_id, body, delivered_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (sender, receiver, body),
        )
        message_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        db.commit()
        message = db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
        payload = dict(message)
        emit("message:new", payload, room=str(receiver))
        emit("message:new", payload, room=str(sender))

    @socketio.on("message:seen")
    def on_message_seen(data):
        message_id = int(data.get("messageId"))
        seen_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        db = get_db()
        db.execute("UPDATE messages SET seen_at = ? WHERE id = ?", (seen_at, message_id))
        db.commit()
        emit("message:seen", {"messageId": message_id, "seenAt": seen_at}, broadcast=True)

    @socketio.on("disconnect")
    def on_disconnect():
        user_id = request.args.get("userId")
        if user_id and user_id in ONLINE_USERS:
            ONLINE_USERS.discard(user_id)
            emit("presence:update", {"userId": user_id, "online": False}, broadcast=True)
