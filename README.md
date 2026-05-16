# Sync Chat

A full-stack real-time chat app with a modern glassmorphism interface.

## Structure

- `/backend`: Flask + Flask-SocketIO + SQLite APIs
- `/frontend`: React + Socket.IO client + Firebase phone auth flow

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.app
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Set these frontend env vars for Firebase OTP:

- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_API_URL` (optional, defaults to `http://localhost:5000`)

## Testing

```bash
cd backend
PYTHONPATH=.. pytest -q
```
