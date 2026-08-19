from datetime import datetime, timezone
from io import BytesIO

from app.models import (
    AttendanceEntry,
    AttendanceRegister,
    BiometricAttendanceDay,
    BiometricImportBatch,
    DeviceAttendanceIdentity,
    Enrollment,
    Student,
    StudentAcademicProfile,
    User,
)
from app.security import create_token, hash_password
from app.importers.biometric_attendance import SheetData, parse_essl_form_j_pdf, parse_essl_form_j_sheet


def setup_students(database):
    operator = User(
        mobile="9000000099",
        full_name="Attendance Operator",
        role="attendance_operator",
        password_hash=hash_password("Password123!"),
    )
    tatva = Student(
        admission_number="LI-2026-20001",
        full_name="Tatva Student",
        mobile="9000000101",
        status="active",
    )
    essential = Student(
        admission_number="LI-2026-20002",
        full_name="Essential Student",
        mobile="9000000102",
        status="active",
    )
    database.add_all([operator, tatva, essential])
    database.flush()
    database.add_all([
        Enrollment(student_id=tatva.id, program="JEE", batch="Tatva", status="active", is_active=True),
        Enrollment(student_id=essential.id, program="Boards", batch="Essential", status="active", is_active=True),
        StudentAcademicProfile(
            student_id=tatva.id,
            source_student_code="T-1",
            batch_name="Tatva",
            source_stream="JEE",
        ),
        StudentAcademicProfile(
            student_id=essential.id,
            source_student_code="E-1",
            batch_name="Essential",
            source_stream="Boards",
        ),
    ])
    database.commit()
    return operator, tatva, essential


def preview(client, headers, content, filename="attendance.csv"):
    response = client.post(
        "/api/attendance/biometric-imports/preview",
        headers=headers,
        files={"file": (filename, content, "text/csv")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_biometric_file_import_maps_students_and_keeps_first_daily_punch(client, database):
    operator, tatva, essential = setup_students(database)
    no_punch = Student(
        admission_number="LI-2026-20003",
        full_name="Tatva No Punch",
        mobile="9000000103",
        status="active",
    )
    database.add(no_punch)
    database.flush()
    database.add_all([
        Enrollment(student_id=no_punch.id, program="JEE", batch="Tatva", status="active", is_active=True),
        StudentAcademicProfile(
            student_id=no_punch.id,
            source_student_code="T-2",
            batch_name="Tatva",
            source_stream="JEE",
        ),
    ])
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(operator)}"}
    content = (
        b"User ID,Name,Date,Time\n"
        b"101,Tatva Student,12-08-2026,08:15:00\n"
        b"101,Tatva Student,12-08-2026,16:05:00\n"
        b"202,Essential Student,12-08-2026,08:21:00\n"
        b"999,Staff Member,12-08-2026,08:04:00\n"
    )
    staged = preview(client, headers, content)
    assert staged["device"]["serialNumber"] == "ABFR220607313"
    assert staged["sheets"][0]["detected"]["device_id"] == "User ID"

    selection = {
        "previewToken": staged["previewToken"],
        "sheetName": "Attendance",
        "deviceIdColumn": "User ID",
        "nameColumn": "Name",
        "datetimeColumn": None,
        "dateColumn": "Date",
        "timeColumn": "Time",
    }
    analysis = client.post(
        "/api/attendance/biometric-imports/analyze",
        headers=headers,
        json=selection,
    )
    assert analysis.status_code == 200, analysis.text
    assert analysis.json()["rowsSeen"] == 4
    assert analysis.json()["uniqueAttendanceDays"] == 3
    assert analysis.json()["duplicateRows"] == 1

    committed = client.post(
        "/api/attendance/biometric-imports",
        headers=headers,
        json={
            **selection,
            "mappings": [
                {"deviceUserId": "101", "studentId": tatva.id, "ignore": False},
                {"deviceUserId": "202", "studentId": essential.id, "ignore": False},
                {"deviceUserId": "999", "studentId": None, "ignore": True},
            ],
        },
    )
    assert committed.status_code == 200, committed.text
    body = committed.json()
    assert body["punchesCreated"] == 2
    assert {item["batch"] for item in body["registers"]} == {"Tatva", "Essential"}
    assert database.query(BiometricAttendanceDay).count() == 2
    tatva_day = database.query(BiometricAttendanceDay).filter_by(student_id=tatva.id).one()
    assert tatva_day.first_punch_at.hour == 2
    assert tatva_day.first_punch_at.minute == 45
    assert database.query(BiometricImportBatch).one().rows_seen == 4
    assert database.query(DeviceAttendanceIdentity).filter_by(device_user_id="999").one().is_ignored is True
    registers = database.query(AttendanceRegister).filter_by(register_kind="biometric").all()
    assert len(registers) == 2
    assert all(register.status == "draft" for register in registers)
    assert database.query(AttendanceEntry).count() == 2

    bootstrap = client.get("/api/attendance/bootstrap?day=2026-08-12", headers=headers)
    assert bootstrap.status_code == 200
    imported_sessions = [item for item in bootstrap.json()["sessions"] if item["registerKind"] == "biometric"]
    assert {item["batch"] for item in imported_sessions} == {"Tatva", "Essential"}
    tatva_register = next(item for item in imported_sessions if item["batch"] == "Tatva")
    roster = client.get(f"/api/attendance/manual-registers/{tatva_register['id']}", headers=headers)
    assert roster.status_code == 200
    statuses = {item["studentId"]: item["status"] for item in roster.json()["entries"]}
    assert statuses[tatva.id] == "present"
    assert statuses[no_punch.id] == "absent"


def test_biometric_import_rejects_unmapped_device_ids_and_duplicate_files(client, database):
    operator, tatva, _ = setup_students(database)
    headers = {"Authorization": f"Bearer {create_token(operator)}"}
    content = b"User ID,Timestamp\n101,2026-08-12 08:15:00\n"
    staged = preview(client, headers, content)
    selection = {
        "previewToken": staged["previewToken"],
        "sheetName": "Attendance",
        "deviceIdColumn": "User ID",
        "datetimeColumn": "Timestamp",
        "dateColumn": None,
        "timeColumn": None,
        "nameColumn": None,
    }
    unmapped = client.post(
        "/api/attendance/biometric-imports",
        headers=headers,
        json={**selection, "mappings": []},
    )
    assert unmapped.status_code == 409

    first = client.post(
        "/api/attendance/biometric-imports",
        headers=headers,
        json={**selection, "mappings": [{"deviceUserId": "101", "studentId": tatva.id, "ignore": False}]},
    )
    assert first.status_code == 200
    staged_again = preview(client, headers, content)
    duplicate = client.post(
        "/api/attendance/biometric-imports",
        headers=headers,
        json={**selection, "previewToken": staged_again["previewToken"], "mappings": []},
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["alreadyImported"] is True
    assert duplicate.json()["punchesCreated"] == 0
    assert "already imported" in duplicate.json()["message"]
    assert database.query(BiometricImportBatch).count() == 1


def test_parent_cannot_preview_biometric_attendance(client, parent_headers):
    response = client.post(
        "/api/attendance/biometric-imports/preview",
        headers=parent_headers,
        files={"file": ("attendance.csv", b"User ID,Timestamp\n1,2026-08-12 08:00:00\n", "text/csv")},
    )
    assert response.status_code == 403


def test_xlsx_biometric_preview(client, database):
    from openpyxl import Workbook

    operator, _, _ = setup_students(database)
    headers = {"Authorization": f"Bearer {create_token(operator)}"}
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Punches"
    sheet.append(["Enroll ID", "Punch Time"])
    sheet.append([101, datetime(2026, 8, 12, 8, 15)])
    stream = BytesIO()
    workbook.save(stream)
    staged = preview(client, headers, stream.getvalue(), "attendance.xlsx")
    assert staged["sheets"][0]["name"] == "Punches"
    assert staged["sheets"][0]["detected"]["device_id"] == "Enroll ID"
    assert staged["sheets"][0]["detected"]["datetime"] == "Punch Time"


def test_essl_form_j_excel_preview_and_student_code_suggestion(client, database):
    from openpyxl import Workbook

    operator, tatva, essential = setup_students(database)
    essential_profile = database.query(StudentAcademicProfile).filter_by(student_id=essential.id).one()
    essential_profile.source_student_code = "E-02"
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(operator)}"}
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "DetailedFormJ"
    sheet.append(['FORM "J"'])
    sheet.append(["REGISTER OF EMPLOYMENT"])
    sheet.append(["For The Month Ending August To 2026"])
    sheet.append(["Sr No.", "Employee", "Type", "1 St", "2 S", "3 M", "4 T", "5 W"])
    sheet.append([1, "Name:Device spelling", "M"])
    sheet.append([None, "Code:T-1", "InTime", "08:15", None, "09:05"])
    sheet.append([2, "Name:Vidhisha patil", "F"])
    sheet.append([None, "Code:51", "InTime", "09:10"])
    stream = BytesIO()
    workbook.save(stream)

    staged = preview(client, headers, stream.getvalue(), "form-j.xlsx")
    assert staged["sourceFormat"] == "essl_form_j_workbook"
    assert staged["report"]["reportMonth"] == "2026-08"
    assert staged["report"]["identityCount"] == 2
    assert staged["sheets"][0]["rowCount"] == 3

    selection = {
        "previewToken": staged["previewToken"],
        "sheetName": "DetailedFormJ",
        "deviceIdColumn": "Device Code",
        "nameColumn": "Student Name",
        "datetimeColumn": None,
        "dateColumn": "Date",
        "timeColumn": "InTime",
    }
    analysis = client.post(
        "/api/attendance/biometric-imports/analyze",
        headers=headers,
        json=selection,
    )
    assert analysis.status_code == 200, analysis.text
    people = {item["deviceUserId"]: item for item in analysis.json()["deviceUsers"]}
    assert people["T-1"]["studentId"] == tatva.id
    assert people["T-1"]["matchReason"] == "Student code"
    assert people["T-1"]["dayCount"] == 2
    assert people["51"]["studentId"] == essential.id
    assert people["51"]["matchReason"] == "Confirmed name merge"


def test_essl_form_j_sheet_parser_keeps_first_punches():
    sheet = SheetData("DetailedFormJ", [
        ['FORM "J"'],
        ["REGISTER OF EMPLOYMENT"],
        ["For The Month Ending August To 2026"],
        ["Sr No.", "Employee", "Type", "1 St", "2 S", "3 M", "4 T", "5 W"],
        [1, "Name:Kamal Parsatwar", "M"],
        [None, "Code:T-1", "InTime", "09:59", None, "11:32"],
        [None, "Designation:", "OutTime", "14:59", None, "13:43"],
        [None, "DOJ:01-Aug-2026", "Status", "P", "A", "P"],
    ])
    punches, errors, report = parse_essl_form_j_sheet(sheet)
    assert errors == []
    assert report["identityCount"] == 1
    assert report["reportMonth"] == "2026-08"
    assert [(item["attendanceDate"].day, item["firstPunchAt"].hour, item["firstPunchAt"].minute) for item in punches] == [
        (1, 4, 29),
        (3, 6, 2),
    ]


def test_essl_form_j_pdf_parser(monkeypatch):
    class FakePage:
        def extract_text(self):
            return 'FORM "J"\nGenerated By:essl\nFor The Month Ending August To 2026'

        def extract_words(self, **_kwargs):
            return [
                {"text": "Name:Vidhisha", "x0": 27.2, "x1": 81.4, "top": 185.2},
                {"text": "patil", "x0": 27.2, "x1": 45.0, "top": 194.4},
                {"text": "Code:51", "x0": 27.2, "x1": 57.4, "top": 203.2},
                {"text": "InTime", "x0": 166.0, "x1": 190.4, "top": 204.2},
                {"text": "14:06", "x0": 493.2, "x1": 513.2, "top": 203.2},
                {"text": "10:22", "x0": 518.4, "x1": 538.4, "top": 203.2},
            ]

    class FakePdf:
        pages = [FakePage()]

        def close(self):
            pass

    import pdfplumber
    monkeypatch.setattr(pdfplumber, "open", lambda _stream: FakePdf())
    punches, errors, metadata = parse_essl_form_j_pdf(b"fake-pdf")
    assert errors == []
    assert metadata["format"] == "essl_form_j"
    assert metadata["reportMonth"] == "2026-08"
    assert metadata["identityCount"] == 1
    assert metadata["identities"] == [{"deviceUserId": "51", "deviceName": "Vidhisha patil"}]
    assert [(item["attendanceDate"].day, item["firstPunchAt"].hour, item["firstPunchAt"].minute) for item in punches] == [
        (11, 8, 36),
        (12, 4, 52),
    ]
