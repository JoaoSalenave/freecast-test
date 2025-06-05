import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

import pytest
from fastapi.testclient import TestClient
from service.main import app

client = TestClient(app)

def test_root_not_found():
    r = client.get("/")
    assert r.status_code == 404

@pytest.mark.django_db
def test_shows_list_returns_200():
    r = client.get("/shows/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.django_db
def test_movies_list_returns_200():
    r = client.get("/movies/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
