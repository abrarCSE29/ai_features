# AGENTS.md — AI Features API

This document provides instructions for agentic coding assistants working in this repository.

## Project Overview

Python 3.12 FastAPI application providing modular AI-powered services: OCR (PyMuPDF), Chatbot (LangGraph + Google Gemini), and Object Detection (YOLOv8). MongoDB stores order data for chatbot tool-calling.

## Build / Run / Lint / Test Commands

```bash
# Install dependencies (preferred — uv is the package manager)
uv sync

# Or with pip
pip install -r requirements.txt

# Run the dev server with hot-reload
uvicorn main:app --reload

# Run via Docker (full stack including MongoDB)
docker compose up -d

# Lint with ruff
ruff check .

# Lint and auto-fix
ruff check --fix .

# Format with ruff
ruff format .

# Seed MongoDB with dummy order data
python scripts/setup_dummy_data.py
```

### Tests

**No test suite exists yet.** If you add tests, place them in a `tests/` directory at the project root. Use `pytest` as the test framework. Run a single test with:

```bash
pytest tests/path/to/test_file.py::test_function_name -v
```

## Project Structure

Each feature is a self-contained module under `modules/` with a consistent layout:

```
modules/<feature>/
  router.py      # FastAPI APIRouter — endpoint definitions
  service.py     # Business logic (stateless class with @staticmethod or singleton)
  models.py      # Pydantic BaseModel request/response schemas
```

Shared code lives in:

| Path | Purpose |
|---|---|
| `config/app_config.py` | Env-var configuration classes (AppConfig, ChatbotConfig) |
| `utils/api_response/` | Standardized `success()`, `error()`, `not_found()` helpers + Pydantic models |
| `utils/logger/` | Structured logger (structlog-based `Logger` class) |
| `middleware/` | Request-ID middleware, exception handler middleware |
| `scripts/` | One-off scripts (e.g., `setup_dummy_data.py`) |
| `main.py` | FastAPI app entry point — wires middleware, CORS, routers, static files |

## Code Style Guidelines

### Imports

- Standard library first, then third-party, then local — separated by blank lines.
- Use **absolute imports** for cross-module references: `from utils.api_response.service import success`.
- Use **relative imports** within a module: `from .service import OCRService`.
- Avoid wildcard imports (`from x import *`).

### Types

- All Pydantic models inherit from `BaseModel`. Use `Field(...)` for descriptions/examples.
- Use `typing` generics (`List`, `Dict`, `Optional`, `Union`) — the project targets Python 3.12 so you may also use built-in generics (`list[...]`, `dict[...]`) where consistent with surrounding code.
- Router functions should declare `response_model=Union[SuccessResponse, ErrorResponse]`.

### Naming

| Element | Convention | Example |
|---|---|---|
| Modules/packages | `snake_case` | `object_detection/` |
| Classes | `PascalCase` | `OCRService`, `AppConfig` |
| Functions/methods | `snake_case` | `extract_text_from_file` |
| Constants | `UPPER_SNAKE_CASE` | `SYSTEM_PROMPT`, `MODEL_DIR` |
| Pydantic models | `PascalCase` | `ChatRequest`, `DetectionInfo` |
| Router path params | `snake_case` | `/extract-text` (kebab-case in URLs) |

### Error Handling

- Router endpoints wrap service calls in `try/except` and return standardized responses via `error()`:
  - `ValueError` → 400/422 with descriptive `error_code` (e.g., `"OCR_ERROR"`, `"CHATBOT_ERROR"`)
  - Generic `Exception` → 500 with `error_code="INTERNAL_ERROR"`
- Services raise `ValueError` for domain errors and `RuntimeError` for missing dependencies.
- Do **not** raise raw HTTP exceptions in services — return errors through the `error()` helper.

### API Response Format

Every endpoint must return one of:
- `success(data=..., message=..., status_code=200)` → `SuccessResponse`
- `error(message=..., status_code=..., error_code=...)` → `ErrorResponse`

### Logging

- Use the project's `Logger` class (`from utils.logger.logger import Logger`), not stdlib `logging`.
- Instantiate: `logger = Logger()`
- Call: `logger.info(message="...")`, `logger.error(message="...")`
- Do not log secrets, API keys, or full request bodies.

### General Conventions

- **No comments** unless explicitly asked by the user.
- Keep router functions thin — delegate to service classes.
- Use `@classmethod` or `@staticmethod` on service classes; use a module-level singleton when state is needed (e.g., `chatbot_service = ChatbotService()`).
- Heavy/optional dependencies (ultralytics, cv2) should be imported inside the function, not at module top-level, with a `RuntimeError` if missing.
- Configuration comes from env vars via `python-dotenv` loaded in `config/app_config.py`. Never hardcode secrets.
- Docker is the recommended runtime; `docker-compose.yml` orchestrates MongoDB + the app.
