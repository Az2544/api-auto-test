\# api-auto-test



\[!\[CI](https://github.com/Az2544/api-auto-test/actions/workflows/ci.yml/badge.svg)](https://github.com/Az2544/api-auto-test/actions/workflows/ci.yml)



针对 \[fastapi-todo](https://github.com/Az2544/fastapi-todo) 的接口自动化测试框架。



\## 技术栈



Python 3.11 · FastAPI · Pytest · httpx · Allure · Docker Compose · GitHub Actions



\## 快速开始



```bash

docker compose up --build -d

pip install -r requirements-dev.txt

pytest

