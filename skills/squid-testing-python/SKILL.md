---
name: squid-testing-python
description: Write and evaluate effective Python tests using pytest. Use when writing tests, reviewing test code, debugging test failures, or improving test coverage. Covers test design, fixtures, parameterization, mocking, and async testing.
---

# Writing Effective Python Tests

## Core Principles

Every test should be **atomic**, **self-contained**, and test **single functionality**. A test that tests multiple things is harder to debug and maintain.

## Test Structure

### Mirror the module layout

Keep a one-to-one relationship between test files and the modules they cover: `myapp/service.py` → `tests/.../test_service.py`. This makes the test for any given module obvious and keeps coverage gaps visible.

### Follow AAA (Arrange, Act, Assert)

Structure each test body in three beats — set up inputs (Arrange), call the thing under test (Act), then assert on the result. Keep them in that order; don't interleave more setup after the act.

### Atomic unit tests

Each test should verify a single behavior. The test name should tell you what's broken when it fails. Multiple assertions are fine when they all verify the same behavior.

```python
# Good: Name tells you what's broken
def test_user_creation_sets_defaults():
    user = User(name="Alice")
    assert user.role == "member"
    assert user.id is not None
    assert user.created_at is not None

# Bad: If this fails, what behavior is broken?
def test_user():
    user = User(name="Alice")
    assert user.role == "member"
    user.promote()
    assert user.role == "admin"
    assert user.can_delete_others()
```

### Use parameterization for variations of the same concept

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase_conversion(input, expected):
    assert input.upper() == expected
```

### Use separate tests for different functionality

Don't parameterize unrelated behaviors. If the test logic differs, write separate tests.

## Project-Specific Rules

<!--
Fill in project-specific conventions here. Common examples to consider:

- Global asyncio mode (e.g. `asyncio_mode = "auto"` in pyproject.toml → no
  `@pytest.mark.asyncio` decorators needed).
- Preferred test transports / in-memory clients for the server framework
  (e.g. FastAPI `TestClient`, FastMCP in-memory client).
- Snapshot testing conventions (e.g. `inline-snapshot`, `syrupy`).
- Required markers (`@pytest.mark.integration`, `@pytest.mark.slow`).
- Forbidden patterns (local imports inside test bodies, real network calls,
  real DB connections in unit tests).

Delete this comment and replace the examples below with the real rules.
-->

### Imports at module level

Put ALL imports at the top of the file. Do not import inside test function bodies.

```python
# Correct
import pytest
from myapp.service import do_work

def test_something():
    assert do_work() is not None

# Wrong - no local imports
def test_something():
    from myapp.service import do_work  # Don't do this
    ...
```

### Async tests

If the project sets `asyncio_mode = "auto"` in `pyproject.toml`, write async tests without decorators:

```python
# Correct (when asyncio_mode = "auto")
async def test_async_operation():
    result = await some_async_function()
    assert result == expected
```

Otherwise, mark explicitly with `@pytest.mark.asyncio`.

### Inline snapshots for complex data

If the project uses `inline-snapshot`, use it for JSON schemas and complex structures:

```python
from inline_snapshot import snapshot

def test_schema_generation():
    schema = generate_schema(MyModel)
    assert schema == snapshot()  # Will auto-populate on first run
```

Commands:
- `pytest --inline-snapshot=create` - populate empty snapshots
- `pytest --inline-snapshot=fix` - update after intentional changes

## Fixtures

### Share setup through fixtures, not setup/teardown methods

Put shared fixtures in `conftest.py` so they're available across test files without imports. Use fixtures (and their `yield`-based teardown) for setup and cleanup — avoid xUnit-style `setUp`/`tearDown` methods.

### Prefer function-scoped fixtures

```python
@pytest.fixture
def client():
    return Client()

def test_with_client(client):
    result = client.ping()
    assert result is not None
```

### Use `tmp_path` for file operations

```python
def test_file_writing(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("content")
    assert file.read_text() == "content"
```

## Mocking

### Mock at the boundary

Use `pytest-mock`'s `mocker` fixture (preferred) or `unittest.mock` patches.

```python
from unittest.mock import AsyncMock

async def test_external_api_call(mocker):
    mock = mocker.patch("mymodule.external_client.fetch", new_callable=AsyncMock)
    mock.return_value = {"data": "test"}
    result = await my_function()
    assert result == {"data": "test"}
```

### Don't mock what you own

Test your code with real implementations when possible. Mock external services (HTTP APIs, third-party SDKs), not your own internal classes.

### Don't write unit tests against infrastructure components

Orchestrators, model-serving runtimes, observability clients, and similar infrastructure should be exercised via **integration tests**, not unit tests with mocks of their internals.

## Test Naming

Test files must be named `test_*.py` and test functions `test_*` so pytest discovers them. Beyond that, use descriptive names that explain the scenario:

```python
# Good
def test_login_fails_with_invalid_password():
def test_user_can_update_own_profile():
def test_admin_can_delete_any_user():

# Bad
def test_login():
def test_update():
def test_delete():
```

## Error Testing

```python
import pytest

def test_raises_on_invalid_input():
    with pytest.raises(ValueError, match="must be positive"):
        calculate(-1)

async def test_async_raises():
    with pytest.raises(ConnectionError):
        await connect_to_invalid_host()
```

## Running Tests

```bash
uv run pytest -n auto              # Run all tests in parallel
uv run pytest -n auto -x           # Stop on first failure
uv run pytest path/to/test.py      # Run specific file
uv run pytest -k "test_name"       # Run tests matching pattern
uv run pytest -m "not integration" # Exclude integration tests
```

Prefer project Make targets when available: `make unit-tests`, `make integration-tests`, `make tests`.

## Checklist

Before submitting tests:
- [ ] Each test tests one thing
- [ ] Imports at module level
- [ ] Descriptive test names
- [ ] Async decorators consistent with project's asyncio mode
- [ ] Parameterization for variations of same behavior
- [ ] Separate tests for different behaviors
- [ ] No unit tests against infrastructure components (those go to integration tests)
- [ ] 0 warnings when running the test suite
