"""
D5: fixture 分层 + Allure 失败自动附加
"""
import pytest
import httpx
import yaml
import allure
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
    return _load_yaml(CONFIG_FILE)


@pytest.fixture(scope="session")
def base_url(config):
    return config["base_url"]


@pytest.fixture(scope="session")
def client(base_url, config, request):
    """
    httpx 客户端 + 记录每次响应，失败时自动附加到 Allure 报告
    """
    records = []

    def _log_response(response):
        records.append(response)

    c = httpx.Client(
        base_url=base_url,
        timeout=config["timeout"],
        event_hooks={"response": [_log_response]},
    )
    c._records = records

    # 挂到 pytest config 上，供 makereport hook 访问
    request.config._api_client = c

    yield c
    c.close()


@pytest.fixture(scope="session")
def todo_cases():
    return _load_yaml(DATA_DIR / "todo_cases.yaml")


# ========== function 层 ==========

@pytest.fixture(scope="function")
def created_todos(client):
    """登记本用例创建的 todo，结束时自动清理"""
    ids = []
    yield ids
    for tid in ids:
        try:
            client.delete(f"/todos/{tid}")
        except Exception:
            pass


# ========== 失败自动附加 hook ==========

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    client = getattr(item.config, "_api_client", None)
    if client is None:
        return

    records = getattr(client, "_records", [])
    if not records:
        return

    # 把最近一次请求/响应附加到报告
    resp = records[-1]
    try:
        body = resp.text
    except Exception:
        body = "<unreadable>"

    content = (
        f"URL: {resp.request.method} {resp.request.url}\n"
        f"Status: {resp.status_code}\n"
        f"Request body: {resp.request.content.decode('utf-8', 'ignore')}\n"
        f"Response body: {body}\n"
    )
    allure.attach(
        content,
        name="last_request_response",
        attachment_type=allure.attachment_type.TEXT,
    )

    # 清空，避免污染下一个用例
    records.clear()