from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_db():
    r = client.get("/health/db")
    assert r.status_code == 200


def test_create_and_get_dataset():
    r = client.post("/api/v1/datasets", json={"name": "pytest-ds", "description": "t"})
    assert r.status_code == 201
    ds_id = r.json()["id"]
    assert client.get(f"/api/v1/datasets/{ds_id}").json()["name"] == "pytest-ds"


def test_dataset_not_found():
    assert client.get("/api/v1/datasets/999999").status_code == 404


def test_invalid_dataset_payload():
    assert client.post("/api/v1/datasets", json={"name": ""}).status_code == 422


def test_add_and_list_test_cases():
    ds_id = client.post("/api/v1/datasets", json={"name": "cases-ds"}).json()["id"]
    cases = [{"input_text": "2+2?", "expected_output": "4"}]
    r = client.post(f"/api/v1/datasets/{ds_id}/test-cases", json=cases)
    assert r.status_code == 201
    listed = client.get(f"/api/v1/datasets/{ds_id}/test-cases").json()
    assert len(listed) == 1 and listed[0]["expected_output"] == "4"


def test_empty_test_case_list_rejected():
    ds_id = client.post("/api/v1/datasets", json={"name": "empty-ds"}).json()["id"]
    assert client.post(f"/api/v1/datasets/{ds_id}/test-cases", json=[]).status_code == 422