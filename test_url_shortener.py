import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from url_shortener import app, validate_shortcode


def test_rest_get_and_post(client):
    shortcode = "1test_"
    url = "https://example.com"

    with freeze_time("2020-10-16 10:00:00") as freezer:
        # create short url
        r = client.post("/shorten", json={"url": url, "shortcode": shortcode})
        assert r.status_code == 201
        assert r.json() == {"shortcode": "1test_"}

        r = client.post(
            "/shorten", json={"url": "https://xxx.com", "shortcode": shortcode}
        )
        assert r.status_code == 409
        assert "Code is already used" in r.json()["detail"]

        r = client.post("/shorten", json={"url": url, "shortcode": "<wrong length>"})
        assert r.status_code == 412
        assert "length" in r.json()["detail"]

        r = client.post("/shorten", json={"url": url, "shortcode": "smbls!"})
        assert r.status_code == 412
        assert "invalid characters" in r.json()["detail"]

        # check redirect
        freezer.tick()
        r = client.get(f"/{shortcode}", allow_redirects=False)
        assert r.status_code == 302
        assert r.headers["location"] == url

        # test stats
        r = client.get(f"/{shortcode}/stats", allow_redirects=False)
        assert r.status_code == 200
        assert r.json() == {
            "created": "2020-10-16T10:00:00",
            "lastRedirect": "2020-10-16T10:00:01",
            "redirectCount": 1,
        }

        # test lastRedirect and redirectCount
        freezer.tick()
        r = client.get(f"/{shortcode}", allow_redirects=False)
        assert r.status_code == 302
        r = client.get(f"/{shortcode}/stats", allow_redirects=False)
        assert r.status_code == 200
        assert r.json() == {
            "created": "2020-10-16T10:00:00",
            "lastRedirect": "2020-10-16T10:00:02",
            "redirectCount": 2,
        }

        r = client.get("/<nonexisting>/stats", allow_redirects=False)
        assert r.status_code == 404


def test_automatic_shortcode_creation(client):
    url = "https://github.com/kopchik"
    r = client.post("/shorten", json={"url": url})
    assert r.status_code == 201
    shortcode = r.json()["shortcode"]
    validate_shortcode(shortcode)

    r = client.get(f"/{shortcode}", allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == url


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
