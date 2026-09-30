from app.models import ParentAccount, Student, User
from app.security import create_token, hash_password, verify_password
from app.routers.students import _set_portal_access


def family(db):
    parent = User(full_name="Sathe Parent", mobile="9000000081", role="parent", password_hash=hash_password("Existing123"))
    students = [Student(full_name=name, admission_number=f"FAMILY-{i}", status="active")
                for i, name in enumerate(["Alvis", "Arick", "Unrelated"])]
    db.add_all([parent, *students]); db.flush()
    db.add_all([ParentAccount(user_id=parent.id, student_id=s.id) for s in students[:2]])
    db.commit()
    return parent, students, {"Authorization": f"Bearer {create_token(parent)}"}


def test_switching_children_is_authorized_and_separate(client, database):
    parent, children, headers = family(database)
    for child in children[:2]:
        response = client.get(f"/api/parent/bootstrap?student_id={child.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["profile"]["id"] == child.id
        assert {c["id"] for c in response.json()["children"]} == {s.id for s in children[:2]}
    assert client.get(f"/api/parent/bootstrap?student_id={children[2].id}", headers=headers).status_code == 403
    children[0].status = "inactive"; database.commit()
    assert client.get(f"/api/parent/bootstrap?student_id={children[0].id}", headers=headers).status_code == 403
    assert len(client.get("/api/parent/bootstrap", headers=headers).json()["children"]) == 1


def test_sibling_messages_do_not_cross_student_context(client, database):
    _, children, headers = family(database)
    threads = []
    for child in children[:2]:
        response = client.post("/api/communication/threads", headers=headers,
                               json={"studentId": child.id, "topic": "Attendance", "body": "Please confirm"})
        assert response.status_code == 201
        threads.append(response.json()["id"])
    for child, thread in zip(children, threads):
        inbox = client.get(f"/api/communication/inbox?student_id={child.id}", headers=headers)
        assert [t["id"] for t in inbox.json()["threads"]] == [thread]
        assert client.get(f"/api/communication/threads/{thread}", headers=headers).status_code == 200
    assert client.post("/api/communication/threads", headers=headers,
                       json={"studentId": children[2].id, "topic": "Wrong child", "body": "No access"}).status_code == 403


def test_owner_explicitly_links_sibling_without_resetting_password(client, database, owner_headers):
    parent, children, _ = family(database)
    payload = {"studentId": children[2].id, "mobile": parent.mobile, "fullName": "Parent",
               "password": "123456", "contactType": "primary_contact"}
    assert client.post("/api/settings/parent-access", headers=owner_headers, json=payload).status_code == 409
    payload["linkExistingParent"] = True
    response = client.post("/api/settings/parent-access", headers=owner_headers, json=payload)
    assert response.status_code == 201
    assert response.json()["passwordUnchanged"] is True
    assert verify_password("Existing123", parent.password_hash)
    assert database.query(ParentAccount).filter_by(user_id=parent.id).count() == 3
    assert client.post("/api/settings/parent-access", headers=owner_headers, json=payload).status_code == 409


def test_inactive_child_does_not_disable_active_sibling_parent(database):
    parent, children, _ = family(database)
    children[0].status = "inactive"; database.flush()
    _set_portal_access(database, children[0].id, False)
    assert parent.is_active
    children[1].status = "inactive"; database.flush()
    _set_portal_access(database, children[1].id, False)
    assert not parent.is_active
