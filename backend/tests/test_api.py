"""
backend/tests/test_api.py
Basic API tests — run with: pytest backend/tests/
"""
import pytest
from backend.app import create_app
from backend.models.base import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Public endpoints ──────────────────────────────────────────
def test_school_returns_200(client):
    r = client.get("/api/school")
    assert r.status_code == 200

def test_director_returns_200(client):
    r = client.get("/api/director")
    assert r.status_code == 200

def test_teachers_returns_list(client):
    r = client.get("/api/teachers")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_classes_returns_list(client):
    r = client.get("/api/classes")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_news_paginated(client):
    r    = client.get("/api/news")
    data = r.get_json()
    assert r.status_code == 200
    assert "items" in data
    assert "total" in data

def test_achievements_returns_list(client):
    r = client.get("/api/achievements")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_leaderboard_returns_list(client):
    r = client.get("/api/achievements/leaderboard")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_faq_returns_list(client):
    r = client.get("/api/faq")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_graduates_returns_list(client):
    r = client.get("/api/graduates")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_gallery_returns_list(client):
    r = client.get("/api/gallery")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

# ── Auth ──────────────────────────────────────────────────────
def test_login_wrong_credentials(client):
    r = client.post("/api/admin/login",
                    json={"username": "fake", "password": "wrong"},
                    content_type="application/json")
    assert r.status_code == 401

def test_admin_me_without_token(client):
    r = client.get("/api/admin/me")
    assert r.status_code == 401

def test_graduate_submit_missing_fields(client):
    r = client.post("/api/graduates", json={}, content_type="application/json")
    assert r.status_code == 422

def test_graduate_submit_valid(client):
    r = client.post("/api/graduates",
                    json={"full_name":"Тест","graduated_year":2023},
                    content_type="application/json")
    assert r.status_code == 201
