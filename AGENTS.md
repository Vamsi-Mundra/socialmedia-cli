# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

SocialMedia CLI (`socialmedia-cli`) is a Python CLI tool for social media management (currently Twitter). It has a Typer-based CLI, an LLM abstraction layer (OpenAI, Groq, Ollama providers), a daily-digest pipeline, and a drafts system. See `README.md` and `USAGE_GUIDE.md` for user-facing docs.

### Development environment

- Python 3.12, virtual environment at `.venv`
- Activate: `source .venv/bin/activate`
- The package is installed in editable mode (`pip install -e .`)

### Key commands

| Task | Command |
|------|---------|
| Run tests | `source .venv/bin/activate && pytest tests/ --disable-warnings -v` |
| Run linter | `source .venv/bin/activate && ruff check .` |
| CLI help | `source .venv/bin/activate && socialmedia-cli --help` |

### Non-obvious caveats

- **click/typer compatibility**: The `pyproject.toml` pins `typer ^0.9.0`, which requires `click <8.2`. The update script pins `click>=7.1.1,<8.2` to avoid `TypeError: Parameter.make_metavar() missing 1 required positional argument: 'ctx'`.
- **`socialmedia_cli/tests/test_openai.py`**: This is a manual integration script, not a proper pytest test. It uses relative imports that break when collected by pytest. Exclude it by running `pytest tests/` (the top-level `tests/` directory) instead of `pytest` from the repo root.
- **Pre-existing test failures**: 4 tests fail due to code bugs (not environment issues): `test_digest_pipeline` (unregistered "fake" provider), `test_invalid_command` (wrong expected exit code), `test_post_tweet_success`/`test_post_tweet_tweepy_error` (incorrect mock target).
- **External APIs**: All tests mock external services. No API keys (`OPENAI_API_KEY`, `GROQ_API_KEY`, `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`) are needed for running the test suite.
- **`openai` package**: Required at import time by `socialmedia_cli/llm/providers/openai.py` even when not using OpenAI. The update script installs it.
