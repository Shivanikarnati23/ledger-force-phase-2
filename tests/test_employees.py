from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_employees():
    response = client.get("/employees/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_employee_success():
    payload = {
        "employee_id": "EX9999",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@company.com",
        "department_id": "D01",
        "role_id": "R001",
        "hire_date": "2023-01-01"
    }
    response = client.post("/employees/", json=payload)
    assert response.status_code in [201, 400]

def test_get_employee_not_found():
    response = client.get("/employees/NONEXISTENT999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"

def test_create_employee_bad_data_422():
    # Missing required fields should trigger 422 Unprocessable Entity
    payload = {
        "employee_id": "BAD01",
        "first_name": "Incomplete"
    }
    response = client.post("/employees/", json=payload)
    assert response.status_code == 422

def test_search_employees():
    response = client.get("/employees/?search=Jane")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_pagination_limit():
    response = client.get("/employees/?limit=5")
    assert response.status_code == 200
    assert len(response.json()) <= 5

def test_department_filter():
    response = client.get("/employees/?department_id=D01")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_soft_delete_employee():
    response = client.delete("/employees/EX9999?exit_date=2026-10-19")
    assert response.status_code in [200, 404]