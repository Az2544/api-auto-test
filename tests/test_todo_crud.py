"""
D4: 数据驱动 + fixture 分层
- 创建类用例从 YAML 读数据（参数化）
- 其他用例手写，用 created_todos 做清理
"""
import pytest
import uuid
import yaml
from pathlib import Path

_DATA_FILE = Path(__file__).parent / "data" / "todo_cases.yaml"
with open(_DATA_FILE, encoding="utf-8") as f:
    CASES = yaml.safe_load(f)

VALID_CREATE = CASES["create_valid_cases"]
INVALID_CREATE = CASES["create_invalid_cases"]


def _unique_title(prefix="todo"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ========== 一、YAML 数据驱动：有效创建 ==========

@pytest.mark.parametrize("case", VALID_CREATE, ids=[c["id"] for c in VALID_CREATE])
def test_create_valid_from_yaml(client, created_todos, case):
    resp = client.post("/todos", json=case["payload"])
    assert resp.status_code == case["expected_status"]
    data = resp.json()
    assert data["done"] is case["expected_done"]
    created_todos.append(data["id"])


# ========== 二、YAML 数据驱动：无效创建 ==========

@pytest.mark.parametrize("case", INVALID_CREATE, ids=[c["id"] for c in INVALID_CREATE])
def test_create_invalid_from_yaml(client, case):
    resp = client.post("/todos", json=case["payload"])
    assert resp.status_code == case["expected_status"]


# ========== 三、手写 CRUD ==========

def test_read_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to the Todo API"}


def test_list_todos_returns_list(client):
    resp = client.get("/todos")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_created_todo_appears_in_list(client, created_todos):
    title = _unique_title("visible")
    created = client.post("/todos", json={"title": title}).json()
    created_todos.append(created["id"])

    resp = client.get("/todos")
    titles = [t["title"] for t in resp.json()]
    assert title in titles


def test_update_todo_title(client, created_todos):
    created = client.post("/todos", json={"title": _unique_title("old")}).json()
    created_todos.append(created["id"])

    new_title = _unique_title("new")
    resp = client.put(f"/todos/{created['id']}", json={"title": new_title})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == new_title
    assert data["done"] == created["done"]


def test_update_todo_done(client, created_todos):
    created = client.post("/todos", json={"title": _unique_title(), "done": False}).json()
    created_todos.append(created["id"])

    resp = client.put(f"/todos/{created['id']}", json={"done": True})
    assert resp.status_code == 200
    assert resp.json()["done"] is True


def test_update_todo_both_fields(client, created_todos):
    created = client.post("/todos", json={"title": _unique_title(), "done": False}).json()
    created_todos.append(created["id"])

    new_title = _unique_title("both")
    resp = client.put(f"/todos/{created['id']}", json={"title": new_title, "done": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == new_title
    assert data["done"] is True


def test_update_todo_empty_body_keeps_original(client, created_todos):
    created = client.post("/todos", json={"title": _unique_title("keep"), "done": False}).json()
    created_todos.append(created["id"])

    resp = client.put(f"/todos/{created['id']}", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == created["title"]
    assert data["done"] == created["done"]


def test_delete_todo(client):
    created = client.post("/todos", json={"title": _unique_title("del")}).json()
    resp = client.delete(f"/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_deleted_todo_not_in_list(client):
    created = client.post("/todos", json={"title": _unique_title("gone")}).json()
    client.delete(f"/todos/{created['id']}")

    resp = client.get("/todos")
    ids = [t["id"] for t in resp.json()]
    assert created["id"] not in ids


# ========== 四、手写异常 ==========

def test_update_nonexistent_todo_404(client):
    resp = client.put("/todos/999999", json={"title": "x"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"


def test_delete_nonexistent_todo_404(client):
    resp = client.delete("/todos/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"


def test_delete_todo_invalid_id_422(client):
    resp = client.delete("/todos/abc")
    assert resp.status_code == 422


# ========== 五、手写边界 ==========

def test_create_todo_empty_title(client, created_todos):
    resp = client.post("/todos", json={"title": ""})
    assert resp.status_code == 201
    created_todos.append(resp.json()["id"])
    assert resp.json()["title"] == ""


def test_create_todo_long_title(client, created_todos):
    long_title = "a" * 1000
    resp = client.post("/todos", json={"title": long_title})
    assert resp.status_code == 201
    created_todos.append(resp.json()["id"])
    assert resp.json()["title"] == long_title
    assert len(resp.json()["title"]) == 1000


def test_create_todo_duplicate_title(client, created_todos):
    title = _unique_title("dup")
    r1 = client.post("/todos", json={"title": title}).json()
    r2 = client.post("/todos", json={"title": title}).json()
    created_todos.append(r1["id"])
    created_todos.append(r2["id"])
    assert r1["id"] != r2["id"]
    assert r1["title"] == r2["title"] == title