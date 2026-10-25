# Setup & Operations Guide

## 1. Prerequisites

- Python 3.10+ and pip
- Node.js 22+ and npm
- (Production) PostgreSQL 15+, Redis 7+

## 2. Backend setup

```bash
cd backend
cp ../.env.example .env
# Edit .env: set DATABASE_URL, APP_SECRET_KEY, TELEPHONY_*, VOICE_*,
# GOOGLE_OAUTH_*, and limits.
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

## 3. Frontend setup

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## 4. Running with Docker

```bash
cp .env.example .env
# Edit .env values
docker compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## 5. Migrations

```bash
cd backend
python -m alembic revision --autogenerate -m "message"
python -m alembic upgrade head
```

## 6. Tests

```bash
cd backend
python -m pytest -q
```

Tests use mock telephony/voice providers and a throwaway SQLite test database.
No real calls or provider API calls are made.

## 7. First real call (when credentials are available)

1. Provision a telephony account (e.g. Twilio) with outbound voice enabled.
2. Verify your destination mobile number in the provider console.
3. Fill `TELEPHONY_ACCOUNT_ID`, `TELEPHONY_AUTH_SECRET`, `TELEPHONY_PHONE_NUMBER`,
   `TELEPHONY_WEBHOOK_SECRET`, `VERIFIED_DESTINATION_NUMBER` in `.env`.
4. Set `TELEPHONY_PROVIDER=twilio` and `APPLICATION_ENV=production`.
5. Provide a publicly reachable webhook URL (set `PUBLIC_BASE_URL`) so the
   provider can deliver status callbacks.
6. Set `VOICE_PROVIDER` and `VOICE_API_KEY` to a real-time voice provider.
7. Deploy to a cloud server with TLS; the dashboard "Call Me Now" button will
   place a real outbound call.

## 8. Security notes

- Never commit `.env` or real credentials.
- Rotate `APP_SECRET_KEY` and `ENCRYPTION_KEY` in production.
- Use TLS in front of the backend; webhook endpoints must be HTTPS.
- OAuth tokens are encrypted at rest; passwords are never stored.
- High-risk actions (sending email) require explicit confirmation.
