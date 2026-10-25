# AI Voice Agent

Production-grade autonomous AI voice agent that initiates outbound phone calls,
conducts two-way voice conversations, executes authorized real-world tasks, and
reports verified results through the call.

## Architecture

- **Backend**: Python FastAPI, SQLAlchemy 2.0 (async), Alembic migrations, Pydantic
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Database**: PostgreSQL (production) / SQLite (dev)
- **Cache/Queue**: Redis
- **Telephony**: provider abstraction (Twilio Programmable Voice + mock dev mode)
- **Voice**: provider-independent STT / LLM / TTS pipeline (mock dev mode)
- **Agent**: typed task state machine, tool registry, risk-based authorization

## Repository structure

```
backend/
  app/
    api/routers      # FastAPI route modules (auth, calls, tasks, integrations, health)
    auth/            # JWT, password hashing, dependencies
    config/          # Pydantic settings
    database/        # SQLAlchemy base, session, models, Alembic migrations
    integrations/    # Gmail, Calendar, web-research clients
    memory/          # (placeholder)
    observability/   # structured JSON logging
    security/        # audit logging, rate limiting
    scheduler/       # (placeholder)
    telephony/       # provider base, Twilio, mock, adapter
    tools/           # tool registry + default tool implementations
    voice/           # STT/TTS/LLM interfaces + mock providers + session manager
  tests/             # pytest unit + integration tests
frontend/            # Next.js dashboard
docker/              # deployment configs
docs/                # documentation
.env.example         # environment variable template
docker-compose.yml   # local dev stack
```

## Provider and model choices

| Layer | Dev (mock) | Production option |
|-------|-----------|-------------------|
| Telephony | MockTelephonyProvider | Twilio Programmable Voice |
| Voice/STT/TTS/LLM | Mock providers | OpenAI Realtime / Azure Speech / etc. (configure via env) |
| Database | SQLite | PostgreSQL + asyncpg |
| Cache | (in-memory) | Redis |

Twilio was selected as the primary real telephony provider because it supports
outbound Programmable Voice with signed webhook verification and international
termination. Indian mobile termination requires verifying Twilio's current
regional support, caller-ID requirements, and consent rules before enabling.

## Environment variables

Copy `.env.example` to `.env` and fill in real values. Never commit secrets.

## Setup instructions

### Backend

```bash
cd backend
cp ../.env.example .env   # edit .env with your values
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (all services)

```bash
cp .env.example .env   # edit values
docker compose up --build
```

## Running tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest -q
```

27 tests pass (unit + integration against mock providers). These tests use mock
telephony/voice providers and an in-process test database; they do NOT place real
calls or call real provider APIs.

## Database migrations

```bash
cd backend
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
```

## Production deployment

See `docker-compose.yml` and `backend/Dockerfile`. Set `APPLICATION_ENV=production`,
provide real `TELEPHONY_*`, `VOICE_*`, `GOOGLE_OAUTH_*` credentials, and use a
managed PostgreSQL + Redis. Put a reverse proxy with TLS in front of the backend.
Do not expose PostgreSQL/Redis/admin endpoints to the public internet.

## External accounts and credentials still needed

- Telephony provider account (e.g. Twilio) with a verified phone number and
  outbound calling enabled, plus verified destination number.
- Real-time voice provider API key (STT/TTS/LLM or speech-to-speech).
- Google OAuth client ID/secret for Gmail/Calendar integration.
- PostgreSQL and Redis hosting for production.
- A domain with TLS for public webhook endpoints.

## Known limitations / blockers (not production-ready yet)

- No real telephony credentials configured; outbound calls are mock-only.
- No real voice provider credentials; STT/TTS/LLM are mock-only.
- Gmail/Calendar OAuth requires a Google Cloud project and consent-screen setup.
- Indian mobile termination must be verified against the telephony provider's
  current regulatory requirements before enabling real calls.
- Frontend static-export build timed out in this constrained environment;
  `next dev` works.

## Acceptance criteria status

Not yet satisfied for real providers. The following require external credentials
and a verified phone number before they can be demonstrated:

- Real outbound call placed and answered
- Two-way voice conversation with real STT/TTS
- Real Gmail/Calendar tool execution
- Production deployment on a cloud server

See the final implementation report for a per-feature classification.