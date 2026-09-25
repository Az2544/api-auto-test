"""
D4: fixture 分层
- session 层：config / base_url / client / todo_cases
- function 层：created_todos（自动清理本用例创建的数据）
"""
import pytest
import httpx
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_FILE = ROOT / "config.yaml"
DATA_DIR = Path(__file__).parent / "data"


def _load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ========== session 层 ==========

@pytest.fixture(scope="session")
def config():
    """加载 config.yaml，测试期间只读一次"""
    return _load_yaml(CONFIG_FILE)


@pytest.fixture(scope="session")
def base_url(config):
    return config["base_url"]


@pytest.fixture(scope="session")
def client(base_url, config):
    """httpx 客户端，整个会话共用一个连接池"""
    with httpx.Client(base_url=base_url, timeout=config["timeout"]) as c:
        yield c


@pytest.fixture(scope="session")
def todo_cases():
    """加载 YAML 测试数据"""
    return _load_yaml(DATA_DIR / "todo_cases.yaml")


# ========== function 层 ==========

@pytest.fixture(scope="function")
def created_todos(client):
    """
    function 级清理器：
    用例通过 created_todos.append(id) 登记本用例创建的 todo，
    测试结束后自动逐个删除，避免脏数据累积。
    """
    ids = []
    yield ids
    for tid in ids:
        try:
            client.delete(f"/todos/{tid}")
        except Exception:
            pass