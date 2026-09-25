# api-auto-test



[![CI](https://github.com/Az2544/api-auto-test/actions/workflows/ci.yml/badge.svg)](https://github.com/Az2544/api-auto-test/actions/workflows/ci.yml)

![Python](https://img.shields.io/badge/python-3.11-blue)

![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)



API automation testing framework for [fastapi-todo](https://github.com/Az2544/fastapi-todo), a simple in-memory Todo API.



## Tech Stack



\- Python 3.11, FastAPI, uvicorn (service under test)

\- Pytest, httpx, PyYAML (test framework)

\- Allure (reporting)

\- Docker / Docker Compose (containerization)

\- GitHub Actions (CI)



## Architecture



&#x20;   +--------------------------+     +---------------------+

&#x20;   |   pytest (tests/)        |     |   Allure Report     |

&#x20;   |  - integration (httpx) --+---->|   (HTML)            |

&#x20;   |  - unit (TestClient)     |     +---------------------+

&#x20;   +------------+-------------+

&#x20;                | HTTP

&#x20;                v

&#x20;   +--------------------------+

&#x20;   |   Docker Container       |

&#x20;   |   uvicorn main:app       |

&#x20;   |   (fastapi-todo)         |

&#x20;   |   0.0.0.0:8000           |

&#x20;   +--------------------------+

&#x20;                ^

&#x20;                | push triggers

&#x20;   +------------+-------------+

&#x20;   |   GitHub Actions CI      |

&#x20;   +------------+-------------+



## Quick Start



1\. Start service:



&#x20;      docker compose up --build -d



2\. Install test dependencies:



&#x20;      python -m venv .venv

&#x20;      .\\.venv\\Scripts\\Activate.ps1

&#x20;      pip install -r requirements-dev.txt



3\. Run tests:



&#x20;      pytest



4\. View Allure report (requires Java + allure CLI):



&#x20;      allure serve allure-results



## Test Strategy



Two layers:



| Layer | Location | Method | Purpose |

|---|---|---|---|

| Integration | tests/test\_todo\_crud.py | httpx over HTTP to real container | End-to-end behavior |

| Unit | tests/test\_todo\_unit.py | FastAPI TestClient in-process | Code logic and coverage |



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



&#x20;   api-auto-test/

&#x20;   |- app/main.py

&#x20;   |- tests/

&#x20;   |   |- conftest.py

&#x20;   |   |- test\_todo\_crud.py

&#x20;   |   |- test\_todo\_unit.py

&#x20;   |   |- README.md

&#x20;   |   `- data/todo\_cases.yaml

&#x20;   |- .github/workflows/ci.yml

&#x20;   |- config.yaml

&#x20;   |- pytest.ini

&#x20;   |- requirements.txt

&#x20;   |- requirements-dev.txt

&#x20;   |- Dockerfile

&#x20;   |- docker-compose.yml

&#x20;   `- README.md



## CI



On every push to main, GitHub Actions runs:



1\. Checkout

2\. Set up Python 3.11

3\. Install dependencies

4\. Start service via docker compose

5\. Wait for readiness

6\. Run 30 tests

7\. Generate Allure report

8\. Upload allure-report and allure-results as artifacts



See [Actions](https://github.com/Az2544/api-auto-test/actions).



## License



MIT




