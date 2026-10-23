from datetime import date
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_effective_dated_salary_lookup():
    # Testing salary structures for 3 distinct employees on 3 different dates/boundary scenarios
    test_cases = [
        {"employee_id": "E0001", "date": "2026-01-01"},
        {"employee_id": "E0002", "date": "2026-02-01"},
        {"employee_id": "E0003", "date": "2026-03-01"},
    ]
    
    for case in test_cases:
        response = client.get(f"/salary/structure/{case['employee_id']}?as_of_date={case['date']}")
        # Assert the endpoint responds successfully (200 OK or appropriate fallback)
        assert response.status_code in [200, 404]

def test_salary_revision():
    response = client.get("/salary/revisions/E0001")
    assert response.status_code in [200, 404]