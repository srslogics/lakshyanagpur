from app.models import AuditLog, User
from scripts.assign_faculty_mobiles import (
    FACULTY_MOBILES,
    assign_faculty_mobiles,
)


def test_faculty_mobile_assignment_is_audited_and_idempotent(database):
    owner = database.query(User).filter_by(role="owner").one()
    database.add_all([
        User(
            full_name=full_name,
            role="faculty",
            password_hash="unprovisioned",
        )
        for full_name in FACULTY_MOBILES
    ])
    database.commit()

    preview = assign_faculty_mobiles(database, owner, apply=False)
    assert preview["eligibleAssignments"] == 5
    assert preview["assignedMobiles"] == 0
    database.rollback()

    assigned = assign_faculty_mobiles(database, owner, apply=True)
    database.commit()
    assert assigned["assignedMobiles"] == 5
    assert {
        row.full_name: row.mobile
        for row in database.query(User).filter_by(role="faculty").all()
    } == FACULTY_MOBILES
    assert database.query(AuditLog).filter_by(
        action="settings.faculty_access.mobile_assign",
    ).count() == 5

    rerun = assign_faculty_mobiles(database, owner, apply=True)
    database.commit()
    assert rerun["assignedMobiles"] == 0
    assert rerun["existingAssignments"] == 5


def test_faculty_mobile_assignment_does_not_overwrite_conflicts(database):
    owner = database.query(User).filter_by(role="owner").one()
    database.add(User(
        full_name="Meet Sir",
        mobile="9000000099",
        role="faculty",
        password_hash="unprovisioned",
    ))
    database.commit()

    result = assign_faculty_mobiles(database, owner, apply=True)
    database.commit()
    assert result["assignedMobiles"] == 0
    assert len(result["conflicts"]) == 1
    assert database.query(User).filter_by(full_name="Meet Sir").one().mobile == "9000000099"
