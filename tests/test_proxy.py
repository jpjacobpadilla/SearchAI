import pytest

from search_ai import Proxy


@pytest.fixture
def proxy_with_auth() -> Proxy:
    return Proxy(protocol='http', host='127.0.0.1', port=8080, username='user', password='pass')


@pytest.fixture
def proxy_no_auth() -> Proxy:
    return Proxy(protocol='https', host='proxy.io', port=443)


def test_to_httpx_proxy_url_with_auth(proxy_with_auth):
    assert proxy_with_auth.to_httpx_proxy_url() == 'http://user:pass@127.0.0.1:8080'


def test_to_httpx_proxy_url_no_auth(proxy_no_auth):
    assert proxy_no_auth.to_httpx_proxy_url() == 'https://proxy.io:443'


def test_to_playwright_proxy_with_auth(proxy_with_auth):
    expected = {'server': 'http://127.0.0.1:8080', 'username': 'user', 'password': 'pass'}
    assert proxy_with_auth.to_playwright_proxy() == expected


def test_to_playwright_proxy_no_auth(proxy_no_auth):
    expected = {'server': 'https://proxy.io:443'}
    assert proxy_no_auth.to_playwright_proxy() == expected
