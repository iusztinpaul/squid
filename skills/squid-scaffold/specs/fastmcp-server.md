---
name: fastmcp-server
description: FastMCP server conventions — tool and prompt design, session lifecycle, error surfacing, resource registration. TRIGGER when building an MCP server with FastMCP in Python. SKIP for the generic MCP SDK or non-Python MCP servers.
---

# FastMCP server

Opinionated FastMCP server structure. Builds on [`python-backend`](python-backend.md) — same `src/` layout, same logging discipline, same testing conventions.

## When to use

- Building an MCP server that exposes tools, prompts, or resources to an LLM client.
- Adding an MCP surface to an existing Python backend.

## When NOT to use

- Non-MCP HTTP APIs — use [`fastapi-service`](fastapi-service.md).
- Plain Python CLIs — use [`cli-tool-python`](cli-tool-python.md).
- Projects using the lower-level `mcp` SDK directly. FastMCP is the opinionated wrapper; if you're hand-rolling session lifecycle, you've outgrown this spec.

## Decision tree

- Server runs **locally over stdio** (Claude Desktop / Claude Code) → FastMCP default. Start here.
- Server runs **over HTTP** (remote agents, browser) → FastMCP's HTTP transport. Same shape; different entry point.
- Server needs **both tools and resources** → one `FastMCP` instance, modules split under `mcp/tools/`, `mcp/resources/`, `mcp/prompts/`.
- Server state outlives a single tool call (DB client, loaded model, cache) → bootstrap in the `lifespan` context manager, not per-call.

## Canonical principles

### 1. One entry point, `scripts/serve_mcp.py`

`init_logger()` at module level first — same rule as [`python-backend`](python-backend.md#logging-first-init_logger-at-module-level); FastMCP logs on import, so those lines bypass your formatter otherwise — then `from my_service.mcp_server import mcp` and `mcp.run()` (stdio by default).

### 2. Tool naming: `verb_noun`, snake_case

- `search_documents`, not `documentsSearch` / `DocumentSearch` / `doSearch`.
- The LLM picks tools by name and docstring. Both are part of the API surface — treat them like function signatures.
- One verb per tool. If you reach for `update_or_create_user`, split it.
- Name the capability, not the wiring: `search_documents`, not `call_search_service`.

### 3. Pydantic for every tool argument and return

FastMCP auto-generates the JSON schema from type hints. Use Pydantic models (not `TypedDict`, not bare `dict`) so validation errors surface to the LLM as structured feedback.

```python
from pydantic import BaseModel, Field

class SearchArgs(BaseModel):
    query: str = Field(..., min_length=1, description="Free-text query")
    limit: int = Field(10, ge=1, le=100)

class SearchResult(BaseModel):
    doc_id: str
    score: float
    snippet: str

@mcp.tool()
async def search_documents(args: SearchArgs) -> list[SearchResult]:
    """Find documents matching the query, ranked by relevance."""
    ...
```

Annotate every argument, every return, every field. Add a `description` wherever the name isn't self-explanatory — the LLM reads the schema; vague fields cost tool-call accuracy.

### 4. Errors are data, not exceptions

A tool that raises a bare exception is a tool the LLM can't recover from. Return structured error results for expected failures (not-found, validation, rate-limit); raise only for bugs.

```python
from typing import Literal

class SearchError(BaseModel):
    kind: Literal["not_found", "rate_limited", "invalid_query"]
    message: str

@mcp.tool()
async def search_documents(args: SearchArgs) -> list[SearchResult] | SearchError:
    try:
        return await _search(args)
    except RateLimitedError as e:
        return SearchError(kind="rate_limited", message=str(e))
```

Reserve raw exceptions for "this should never happen in prod" cases — they surface as MCP protocol errors and can end the session.

### 5. Long-lived resources live in `lifespan`, not in tool bodies

State that needs setup (DB client, embedding model, cache) lives in a lifespan context manager at module level:

```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP

@asynccontextmanager
async def lifespan(app: FastMCP):
    db = await connect_db()
    try:
        app.state.db = db
        yield
    finally:
        await db.close()

mcp = FastMCP("my-service", lifespan=lifespan)
```

FastMCP reuses the process across tool calls — opening a new DB connection per call is pure overhead.

### 6. Layout

Mirror the python-backend tree, with the MCP surface in its own subpackage:

```
src/my_service/
├── mcp_server.py          # `mcp = FastMCP(...)` + lifespan
└── mcp/
    ├── tools/             # one module per related tool cluster
    ├── prompts/           # prompt templates (if any)
    └── resources/         # resource registrations (if any)
scripts/
└── serve_mcp.py           # entry point; init_logger + mcp.run()
```

Tool modules import `mcp` from `mcp_server` and register via `@mcp.tool()` at import time. The entry script imports `mcp_server`, which triggers the registration side effect. Keep registration at import time — side effects inside functions are harder to trace and easier to miss.

### 7. Testing

- **Unit-test the tool body directly** (`await search_documents(SearchArgs(query="x"))`). No FastMCP runtime needed; mirrors the pattern in [`squid-testing-python`](../../squid-testing-python/SKILL.md).
- **Integration-test the full session** via FastMCP's test client (`async with Client(mcp) as client: ...`).
- Don't unit-test FastMCP itself — see [`python-backend`](python-backend.md#testing-discipline-reminder).
