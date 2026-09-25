import pytest
import httpx


@pytest.fixture(scope="session")
def base_url():
    """被测服务的根地址"""
    return "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def client(base_url):
    """httpx 客户端，整个测试会话共用"""
    with httpx.Client(base_url=base_url, timeout=10.0) as c:
        yield c