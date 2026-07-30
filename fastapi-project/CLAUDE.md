## Project

FastAPI service that orchestrates LLM workflows with **LangGraph**. `src/` layout,
packaged with setuptools, dependencies managed with **uv**. Versioned API under
`/api/v1`. Package root is `fieldwork` — import as `from fieldwork.… import …`.
There is **no root `main.py`**; the app is `fieldwork.main:app`.

## Commands

| Task | Command |
| --- | --- |
| Run API (reload) | `uv run uvicorn fieldwork.main:app --reload` → `/health` = `{"status":"ok"}` |
| API docs (Scalar) | open `/api/v1/scalar` — HTTP basic auth (`SWAGGER_USER` / `SWAGGER_PASS`) |
| Tests | `uv run pytest` (layers: `tests/unit`, `tests/integration`, `tests/e2e`) |
| Lint / format | `uv run ruff check .` / `uv run ruff format .` |
| Add dependency | `uv add <pkg>` (dev: `uv add --dev <pkg>`), then commit `uv.lock` |

## Working agreement (collaboration)

- **Keep the user in the loop on important decisions** — architecture/schema
  changes, new dependencies, anything hard to reverse. Propose first, don't assume.
- **Flag unguarded failure paths at the end of the response.** When code I write or
  touch can fail at runtime with no `try/except` or fallback — e.g. it assumes a
  specific LLM response shape/content, parses external data, indexes/keys into a
  structure, or calls an external API/service — call it out explicitly at the end
  of my reply (what can fail, where, and the impact) so the user can decide whether
  to add handling. Don't bury it or leave it silent.
- **Never auto-run tests or scripts that call real model/LLM APIs** (they cost
  money/credits). Instead, **give the user the exact command to run themselves**,
  e.g. `uv run pytest tests/e2e -k <name>`, and let them approve/run it. Same for
  anything that spends credits or hits paid external services.
- Prefer handing over a command to producing a side effect whenever money,
  external services, or irreversible changes are involved.

## Architecture — adding a feature

A feature spans these layers; keep them separate:

1. **Endpoint** — `api/v1/endpoints/<feature>.py` exposing `router = APIRouter()`;
   register it in `api/v1/router.py`.
2. **API schemas** (HTTP request/response) — `api/v1/schemas/<feature>.py`.
3. **LLM schemas** (structured output) — `llm/schemas/<feature>/`.
   **Never merge the API and LLM schema layers.**
4. **Workflow** — `llm/workflows/<feature>/`: `graph.py` (build + compile the
   `StateGraph`), `state.py`, and `nodes/` (one node per file, re-exported from
   `nodes/__init__.py`). Export the compiled workflow from the package `__init__.py`.
5. **Prompts** — YAML under `llm/prompts/<feature>/`, loaded via `get_prompt()` /
   `load_prompt()`. No inline prompt strings.

Keep endpoints thin: endpoint → invoke a workflow/service. Business logic lives in
workflows/services, not in endpoints.

## Coding standards

- **Imports at the top of the file, always.** No imports in the middle of code,
  no lazy imports inside functions.
- **Absolute `fieldwork.` imports only** — no relative imports (`.foo`, `..foo`).
- **Every import must be a declared, installed dependency.** No `try/except
  ImportError` optional-import fallbacks — if a package is missing, let it fail
  loudly at import time; don't silently degrade behavior.
- **Class-based by default.** Group related state + behavior into a class rather
  than loose functions.
- **`__init__` declares the instance state used across the class** — mostly values
  pulled from settings, e.g. `self.timeout = settings.LLM_REQUEST_TIMEOUT`. Don't
  re-read `settings` ad hoc throughout methods.
- **Helpers go in `utils/`.** Don't scatter one-off helper functions or random
  module-level constants across feature files. Shared constants → `core/constants.py`.
- **No dead code** — no unused functions or speculative constants.
- **Every package dir has `__init__.py`** (package marker + curated re-exports).
- **Config via the single `settings` singleton** (`from fieldwork.core.config import
  settings`). Every env var lives in **both** `.env.example` **and** `core/config.py`.
- **Logging, not print**: `logger = get_logger(__name__)`; `setup_logging()` once
  at startup.
- **Async-first for I/O**: `async def` + `await`; acquire DB connections with
  `async with db_manager.get_connection() as conn:`. Never block the event loop.
- **Errors**: all app exceptions subclass **`fieldworkError`** (base, in
  `core/exceptions.py`) — e.g. `DatabaseError(fieldworkError)`. Raise these, not
  bare built-ins like `RuntimeError`/`ValueError`, for application failures; carry
  a `status_code` where it maps to an HTTP response. Register handlers via
  `register_exception_handlers(app)`. Never silently swallow exceptions.
- **Type hints + docstrings** on modules, classes, and public functions.
- **Model IDs come from config tiers** (`{PROVIDER}_MODEL` / `_MINI_MODEL` /
  `_ADVANCED_MODEL` / `_LATEST_MODEL`) — never hardcode a model name.
- **Secrets only via settings/env** — never committed.
- Line length is 100 (ruff). Run ruff before committing.

## Dependencies

- Add packages **manually, one at a time** with `uv add`; don't bulk-add. Commit
  `uv.lock` so other machines reproduce the exact versions.
- Don't reintroduce removed config groups (AWS / Firecrawl / Webhook) unless
  actually wiring that service — add the vars to `.env.example` and `config.py`
  together.

## Don't

- Don't run cost-incurring model tests — hand the command to the user.
- Don't merge the API and LLM schema layers.
- Don't use relative imports or mid-file imports.
- Don't put business logic in endpoints.
- Don't hardcode model IDs or secrets.
