"""
待办接口自动化测试 - CRUD 基础用例
D2: 只放第一个用例，验证框架能跑通
"""


def test_read_root(client):
    """GET / 应返回 200 和欢迎信息"""
    resp = client.get("/")

    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to the Todo API"}