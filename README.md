# api-auto-test

[![CI](https://github.com/Az2544/api-auto-test/actions/workflows/ci.yml/badge.svg)](https://github.com/Az2544/api-auto-test/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

API automation testing framework for [fastapi-todo](https://github.com/Az2544/fastapi-todo), a simple in-memory Todo API.

## Tech Stack

- Python 3.11, FastAPI, uvicorn (service under test)
- Pytest, httpx, PyYAML (test framework)
- Allure (reporting)
- Docker / Docker Compose (containerization)
- GitHub Actions (CI)

## Architecture

    +--------------------------+     +---------------------+
    |   pytest (tests/)        |     |   Allure Report     |
    |  - integration (httpx) --+---->|   (HTML)            |
    |  - unit (TestClient)     |     +---------------------+
    +------------+-------------+
                 | HTTP
                 v
    +--------------------------+
    |   Docker Container       |
    |   uvicorn main:app       |
    |   (fastapi-todo)         |
    |   0.0.0.0:8000           |
    +--------------------------+
                 ^
                 | push triggers
    +------------+-------------+
    |   GitHub Actions CI      |
    +------------+-------------+

## Quick Start

1. Start service:

       docker compose up --build -d

2. Install test dependencies:

       python -m venv .venv
       pip install -r requirements-dev.txt

3. Run tests:

       pytest

4. View Allure report (requires Java + allure CLI):

       allure serve allure-results

## Test Strategy

Two layers:

| Layer | Location | Method | Purpose |
|---|---|---|---|
| Integration | tests/test_todo_crud.py | httpx over HTTP to real container | End-to-end behavior |
| Unit | tests/test_todo_unit.py | FastAPI TestClient in-process | Code logic and coverage |

Test coverage by category:

| Category | Cases |
|---|---|
| CRUD happy path | 11 |
| Error handling | 6 |
| Boundary | 3 |
| Data-driven (YAML) | 6 |
| Unit tests | 9 |
| Total | 30 |

Code coverage: 100%

## Directory Layout

    api-auto-test/
    |- app/main.py
    |- tests/
    |   |- conftest.py
    |   |- test_todo_crud.py
    |   |- test_todo_unit.py
    |   |- README.md
    |   `- data/todo_cases.yaml
    |- .github/workflows/ci.yml
    |- config.yaml
    |- pytest.ini
    |- requirements.txt
    |- requirements-dev.txt
    |- Dockerfile
    |- docker-compose.yml
    `- README.md

## CI

On every push to main, GitHub Actions runs:

1. Checkout
2. Set up Python 3.11
3. Install dependencies
4. Start service via docker compose
5. Wait for readiness
6. Run 30 tests
7. Generate Allure report
8. Upload allure-report and allure-results as artifacts

See [Actions](https://github.com/Az2544/api-auto-test/actions).

## License

MIT
