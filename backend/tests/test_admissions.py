from app.models import AuditLog, Enrollment, FinanceHandoff, Guardian, Lead, Student, StudentGuardian

def payload(mobile="9876543210"):
    return {"student": "Aarav Thakre", "mobile": mobile, "parent": "Mr Thakre", "parentMobile": "9876543211", "program": "JEE 11th", "source": "website", "counsellor": "Priya Kulkarni", "nextAction": "Book counselling"}

def test_duplicate_mobile_is_blocked(client, owner_headers):
    assert client.post("/api/admissions/leads", json=payload(), headers=owner_headers).status_code == 201
    response = client.post("/api/admissions/leads", json=payload(), headers=owner_headers)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "DUPLICATE_MOBILE"

def test_parent_cannot_access_admissions(client, parent_headers):
    assert client.get("/api/admissions/leads", headers=parent_headers).status_code == 403

def test_conversion_creates_connected_records_once(client, owner_headers, database):
    created = client.post("/api/admissions/leads", json=payload(), headers=owner_headers).json()
    client.patch(f"/api/admissions/leads/{created['id']}/stage", json={"stage": "Admission Confirmed"}, headers=owner_headers)
    first = client.post(f"/api/admissions/leads/{created['id']}/convert", json={"batch": "JEE-11-A"}, headers=owner_headers)
    second = client.post(f"/api/admissions/leads/{created['id']}/convert", json={"batch": "JEE-11-A"}, headers=owner_headers)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert database.query(Student).count() == 1
    assert database.query(Guardian).count() == 1
    assert database.query(StudentGuardian).count() == 1
    assert database.query(Enrollment).count() == 1
    assert database.query(FinanceHandoff).count() == 1
    assert database.query(AuditLog).filter_by(action="admissions.convert").count() == 1
    assert database.get(Lead, created["id"]).stage == "Converted"

def test_converted_stage_requires_atomic_endpoint(client, owner_headers):
    created = client.post("/api/admissions/leads", json=payload(), headers=owner_headers).json()
    response = client.patch(f"/api/admissions/leads/{created['id']}/stage", json={"stage": "Converted"}, headers=owner_headers)
    assert response.status_code == 409
