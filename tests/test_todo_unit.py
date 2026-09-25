"""
进程内单元测试
- 用 FastAPI TestClient 直接 import app
- 让 pytest-cov 能看到 app/main.py 的覆盖率
- 与集成测试（httpx 打 Docker）互补
"""
import sys
import pytest
from pathlib import Path

# 保证可以 import 到项目根的 app 包
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
import app.main as main_module  # noqa: E402


@pytest.fixture(autouse=True)
def reset_state():
    """每个单元测试前后清空内存字典，避免用例互相干扰"""
    main_module.todos.clear()
    main_module.counter = 0
    yield
    main_module.todos.clear()
    main_module.counter = 0


@pytest.fixture
def unit_client():
    with TestClient(fastapi_app) as c:
        yield c


def test_unit_root(unit_client):
    resp = unit_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to the Todo API"}


def test_unit_list_empty(unit_client):
    resp = unit_client.get("/todos")
    assert resp.status_code == 200
    assert resp.json() == []


def test_unit_create(unit_client):
    resp = unit_client.post("/todos", json={"title": "unit-1"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == "unit-1"
    assert data["done"] is False


def test_unit_create_missing_title(unit_client):
    resp = unit_client.post("/todos", json={"done": True})
    assert resp.status_code == 422


def test_unit_update_title_only(unit_client):
    created = unit_client.post("/todos", json={"title": "old"}).json()
    resp = unit_client.put(f"/todos/{created['id']}", json={"title": "new"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "new"
    assert resp.json()["done"] is False


def test_unit_update_done_only(unit_client):
    created = unit_client.post("/todos", json={"title": "x"}).json()
    resp = unit_client.put(f"/todos/{created['id']}", json={"done": True})
    assert resp.status_code == 200
    assert resp.json()["title"] == "x"
    assert resp.json()["done"] is True


def test_unit_update_not_found(unit_client):
    resp = unit_client.put("/todos/9999", json={"title": "x"})
    assert resp.status_code == 404


def test_unit_delete(unit_client):
    created = unit_client.post("/todos", json={"title": "del"}).json()
    resp = unit_client.delete(f"/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_unit_delete_not_found(unit_client):
    resp = unit_client.delete("/todos/9999")
    assert resp.status_code == 404