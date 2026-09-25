"""
待办接口自动化测试 - D3
覆盖：CRUD + 异常 + 边界，共 20 个用例
"""
import uuid


def _unique_title(prefix="todo"):
    """生成唯一标题，避免用例之间互相干扰"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ========== 一、基础 CRUD（11 个） ==========

def test_read_root(client):
    """GET / 返回 200 和欢迎信息"""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to the Todo API"}


def test_list_todos_returns_list(client):
    """GET /todos 返回一个列表"""
    resp = client.get("/todos")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_todo_default_done_false(client):
    """POST /todos 只传 title，done 默认 false"""
    title = _unique_title("create")
    resp = client.post("/todos", json={"title": title})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == title
    assert data["done"] is False
    assert "id" in data


def test_create_todo_with_done_true(client):
    """POST /todos 同时传 done=true"""
    title = _unique_title("done")
    resp = client.post("/todos", json={"title": title, "done": True})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == title
    assert data["done"] is True


def test_created_todo_appears_in_list(client):
    """创建后能在列表里查到"""
    title = _unique_title("visible")
    client.post("/todos", json={"title": title})
    resp = client.get("/todos")
    titles = [t["title"] for t in resp.json()]
    assert title in titles


def test_update_todo_title(client):
    """PUT 更新 title，done 不变"""
    created = client.post("/todos", json={"title": _unique_title("old")}).json()
    new_title = _unique_title("new")
    resp = client.put(f"/todos/{created['id']}", json={"title": new_title})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == new_title
    assert data["done"] == created["done"]


def test_update_todo_done(client):
    """PUT 更新 done"""
    created = client.post("/todos", json={"title": _unique_title(), "done": False}).json()
    resp = client.put(f"/todos/{created['id']}", json={"done": True})
    assert resp.status_code == 200
    assert resp.json()["done"] is True


def test_update_todo_both_fields(client):
    """PUT 同时更新 title 和 done"""
    created = client.post("/todos", json={"title": _unique_title(), "done": False}).json()
    new_title = _unique_title("both")
    resp = client.put(f"/todos/{created['id']}", json={"title": new_title, "done": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == new_title
    assert data["done"] is True


def test_update_todo_empty_body_keeps_original(client):
    """PUT 传空 body，数据保持不变"""
    created = client.post("/todos", json={"title": _unique_title("keep"), "done": False}).json()
    resp = client.put(f"/todos/{created['id']}", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == created["title"]
    assert data["done"] == created["done"]


def test_delete_todo(client):
    """DELETE 删除存在的 todo，返回被删对象"""
    created = client.post("/todos", json={"title": _unique_title("del")}).json()
    resp = client.delete(f"/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_deleted_todo_not_in_list(client):
    """删除后列表里查不到"""
    created = client.post("/todos", json={"title": _unique_title("gone")}).json()
    client.delete(f"/todos/{created['id']}")
    resp = client.get("/todos")
    ids = [t["id"] for t in resp.json()]
    assert created["id"] not in ids


# ========== 二、异常场景（6 个） ==========

def test_update_nonexistent_todo_404(client):
    """PUT 不存在的 id → 404"""
    resp = client.put("/todos/999999", json={"title": "x"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"


def test_delete_nonexistent_todo_404(client):
    """DELETE 不存在的 id → 404"""
    resp = client.delete("/todos/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"


def test_create_todo_missing_title_422(client):
    """POST 缺 title → 422"""
    resp = client.post("/todos", json={"done": False})
    assert resp.status_code == 422


def test_create_todo_title_wrong_type_422(client):
    """POST title 不是字符串 → 422"""
    resp = client.post("/todos", json={"title": 123})
    assert resp.status_code == 422


def test_create_todo_done_wrong_type_422(client):
    """POST done 不是 bool → 422"""
    resp = client.post("/todos", json={"title": "x", "done": "not-bool"})
    assert resp.status_code == 422


def test_delete_todo_invalid_id_422(client):
    """DELETE 非整数 id → 422"""
    resp = client.delete("/todos/abc")
    assert resp.status_code == 422


# ========== 三、边界场景（3 个） ==========

def test_create_todo_empty_title(client):
    """空标题：当前 pydantic 模型接受空字符串"""
    resp = client.post("/todos", json={"title": ""})
    assert resp.status_code == 201
    assert resp.json()["title"] == ""


def test_create_todo_long_title(client):
    """超长标题：1000 字符"""
    long_title = "a" * 1000
    resp = client.post("/todos", json={"title": long_title})
    assert resp.status_code == 201
    assert resp.json()["title"] == long_title
    assert len(resp.json()["title"]) == 1000


def test_create_todo_duplicate_title(client):
    """重复标题：允许，id 不同"""
    title = _unique_title("dup")
    r1 = client.post("/todos", json={"title": title}).json()
    r2 = client.post("/todos", json={"title": title}).json()
    assert r1["id"] != r2["id"]
    assert r1["title"] == r2["title"] == title