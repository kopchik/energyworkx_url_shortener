import pytest
from fastapi.testclient import TestClient

from url_shortener import app


def test_rest_api(client):
    shortcode = "1test_"
    url = "http://example.com"

    r = client.post("/shorten", json={"url": url, "shortcode": shortcode})
    assert r.status_code == 201
    assert r.json() == {"shortcode": "1test_"}

    r = client.post("/shorten", json={"url": "http://xxx.com", "shortcode": shortcode})
    assert r.status_code == 409
    assert "Code is already used" in r.json()["detail"]

    r = client.post("/shorten", json={"url": url, "shortcode": "<wrong length>"})
    assert r.status_code == 412
    assert "length" in r.json()["detail"]

    r = client.post("/shorten", json={"url": url, "shortcode": "smbls!"})
    assert r.status_code == 412
    assert "invalid characters" in r.json()["detail"]

    r = client.get(f"/{shortcode}", allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == url


@pytest.fixture
def client():
    return TestClient(app)
