# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

SocialMedia Web is a full-stack social media management application built on top of the original `socialmedia-cli` Python CLI tool.

- **Backend** (`backend/`): FastAPI + SQLite + SQLAlchemy. Provides REST API for auth (JWT), Twitter OAuth, and post management. Reuses the CLI's Twitter posting logic via `requests_oauthlib`.
- **Frontend** (`frontend/`): Next.js 14 (App Router) + Tailwind CSS. Sign up/sign in, dashboard with Twitter account connection, post composer, and post history with links.
- **CLI** (`socialmedia_cli/`): Original Python CLI tool (retained for reference/library use).

### Development environment

- Python 3.12, virtual environment at `.venv`
- Node.js 22 (via nvm), frontend deps at `frontend/node_modules`
- Activate Python env: `source .venv/bin/activate`

### Key commands

| Task | Command |
|------|---------|
| Start backend | `cd backend && source ../.venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Start frontend | `cd frontend && npm run dev` |
| Run CLI tests | `source .venv/bin/activate && pytest tests/ --disable-warnings -v` |
| Run CLI linter | `source .venv/bin/activate && ruff check .` |
| Build frontend | `cd frontend && npx next build` |

### Non-obvious caveats

- **bcrypt/passlib compatibility**: passlib 1.7.x is incompatible with bcrypt >= 5.0. The update script pins `bcrypt<5`.
- **click/typer compatibility**: The `pyproject.toml` pins `typer ^0.9.0`, which requires `click <8.2`. The update script pins `click>=7.1.1,<8.2`.
- **`openai` package**: Required at import time by `socialmedia_cli/llm/providers/openai.py` even when not using OpenAI.
- **`socialmedia_cli/tests/test_openai.py`**: Manual integration script with broken relative imports. Run `pytest tests/` (top-level directory) instead of `pytest` from repo root to skip it.
- **Pre-existing CLI test failures**: 4 tests fail due to code bugs (not environment issues).
- **Twitter API credentials**: The Twitter connect/post features require `TWITTER_CONSUMER_KEY` and `TWITTER_CONSUMER_SECRET` environment variables to be set with valid X Developer Portal credentials. Without them, the OAuth connect button returns a 503 error and posting returns 401.
- **Frontend env**: `frontend/.env.local` sets `NEXT_PUBLIC_API_URL=http://localhost:8000`. Change if backend runs on a different port.
- **SQLite DB**: Created automatically at `backend/socialmedia.db` on first backend startup.
