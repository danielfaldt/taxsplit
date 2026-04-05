from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_index_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Skatteuttag" in response.text
    assert 'id="language-switch"' in response.text


def test_api_calculate_returns_json():
    response = client.post("/api/calculate", json={"year": 2026})
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended"]["salary"] >= 0


def test_security_and_sitemap_exist():
    assert client.get("/security.txt").status_code == 200
    assert client.get("/sitemap.xml").status_code == 200


def test_client_script_persists_form_state_on_input():
    response = client.get("/static/app.js")
    assert response.status_code == 200
    body = response.text
    assert 'form.addEventListener("input", saveStateIfFormField);' in body
    assert 'localStorage.setItem(STORAGE_KEY, JSON.stringify(formToObject()));' in body
