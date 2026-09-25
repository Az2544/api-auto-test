\# Tests



\## Structure



\- `conftest.py` — fixtures + pytest hooks

\- `test\_todo\_crud.py` — integration tests (21 cases, httpx over HTTP)

\- `test\_todo\_unit.py` — unit tests (9 cases, in-process TestClient)

\- `data/todo\_cases.yaml` — data-driven test cases



\## Fixture Layers



\### Session-scoped



\- `config` — loads config.yaml

\- `base\_url` — service root URL

\- `client` — httpx client with response recorder

\- `todo\_cases` — loaded YAML data



\### Function-scoped



\- `created\_todos` — auto-cleanup for created todo IDs

\- `reset\_state` — clears in-memory dict between unit tests (autouse)

\- `unit\_client` — TestClient instance



\## Why Integration + Unit



\*\*Integration (test\_todo\_crud.py)\*\*

\- Real HTTP: pytest -> containerized uvicorn

\- Validates external behavior: status codes, response bodies

\- Limitation: pytest-cov cannot see code inside the container



\*\*Unit (test\_todo\_unit.py)\*\*

\- In-process: pytest imports app.main directly

\- Enables coverage measurement

\- Fast, pinpoints code lines

\- Limitation: skips HTTP layer



\## Failure Logging



`pytest\_runtest\_makereport` hook in conftest.py attaches the last HTTP request

and response to the Allure report when a test fails.



\## Data Driven



Cases in `data/todo\_cases.yaml` are parameterized via `@pytest.mark.parametrize`.

Test IDs come from the `id` field in YAML. Add new cases by editing YAML only.



\## Running



