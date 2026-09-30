"""Dry-run-first parent provisioning from the institute's five-column workbook.

No credentials or source contact data are written to the repository. Existing
accounts are never reset or reassigned. Ambiguous identities need an explicit
row-number -> admission-number JSON mapping. --apply performs owner API writes.
"""
import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import getpass
import json
import os
import re

import openpyxl
import requests


def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def mobile(value):
    if value is None or str(value).strip() in {"", "-", "NA", "N/A"}:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    digits = re.sub(r"\D", "", str(value))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if not re.fullmatch(r"[6-9][0-9]{9}", digits):
        raise ValueError("Invalid Indian mobile number")
    return digits


def read_contacts(path, mother_rows=()):
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(book.active.values)
        expected = ["srno", "studentsname", "studentsno", "motherno", "fatherno"]
        if [key(v) for v in rows[1][:5]] != expected:
            raise ValueError("Unexpected workbook columns; review the source before importing")
        contacts = []
        for row in rows[2:]:
            if not row[1]:
                continue
            number, name, student_phone, mother, father = row[:5]
            relation = "mother" if int(number) in mother_rows or not father else "father"
            chosen = mother if relation == "mother" else father
            item = {"row": int(number), "name": str(name).strip(), "relation": relation}
            try:
                item["mobile"] = mobile(chosen)
            except ValueError:
                item["error"] = "invalid selected parent number"
                item["mobile"] = None
            try:
                item["studentMobile"] = mobile(student_phone)
            except ValueError:
                item["studentMobile"] = None
            contacts.append(item)
        return contacts
    finally:
        book.close()


def make_plan(contacts, students, settings, mapping=None):
    mapping = mapping or {}
    result = []
    for contact in contacts:
        item = dict(contact)
        item["status"] = "review"
        if not item["mobile"]:
            item["status"] = "review" if item.get("error") else "skip_missing"
            result.append(item)
            continue
        explicit = mapping.get(str(item["row"]))
        matches = [s for s in students if s["admissionNumber"] == explicit] if explicit else [s for s in students if key(s["fullName"]) == key(item["name"])]
        if len(matches) != 1:
            suggestions = sorted(students, key=lambda s: SequenceMatcher(None, key(s["fullName"]), key(item["name"])).ratio(), reverse=True)[:2]
            item["suggestions"] = [{"name": s["fullName"], "admissionNumber": s["admissionNumber"],
                                    "studentMobileMatches": bool(item["studentMobile"] and item["studentMobile"] == s.get("mobile"))} for s in suggestions]
            result.append(item)
            continue
        student = matches[0]
        item.update(studentId=student["id"], admissionNumber=student["admissionNumber"], matchedName=student["fullName"])
        if student["status"] != "active":
            item["error"] = "student is not active"
        else:
            same = [p for p in settings["parentAccess"] if p["studentId"] == student["id"] and p["mobile"] == item["mobile"]]
            users = [u for u in settings["users"] if u["mobile"] == item["mobile"]]
            if same:
                item["status"] = "existing" if all(p["isActive"] for p in same) else "review"
            elif users and settings.get("parentScopedMobileSupport") and all(u.get("role") in {"student", "parent_student"} for u in users):
                item["status"] = "create"
            elif users:
                item["error"] = "number already belongs to an existing account; not reassigned"
            else:
                item["status"] = "create"
        result.append(item)
    for student_id, count in Counter(r.get("studentId") for r in result if r.get("studentId")).items():
        if count > 1:
            for r in result:
                if r.get("studentId") == student_id:
                    r.update(status="review", error="multiple workbook rows map to this student")
    # Resume an interrupted sibling import only when this workbook already
    # confirms a child linked to that exact parent. Never reset its password.
    for item in result:
        if item.get("error") != "number already belongs to an existing account; not reassigned":
            continue
        users = [u for u in settings["users"] if u["mobile"] == item["mobile"] and u.get("role") == "parent"]
        confirmed = any(r["status"] == "existing" and r["mobile"] == item["mobile"] for r in result)
        if confirmed and len(users) == 1 and users[0].get("isActive") and settings.get("parentSiblingSupport"):
            item.update(status="link", linkExistingParent=True)
            item.pop("error", None)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--owner-mobile", required=True)
    parser.add_argument("--mother-row", type=int, action="append", default=[])
    parser.add_argument("--mapping", help="Reviewed row-number to ERP admission-number JSON")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.base_url.startswith("https://"):
        raise SystemExit("Use an HTTPS endpoint")
    mapping = None
    if args.mapping:
        with open(args.mapping) as handle:
            mapping = json.load(handle)
    session = requests.Session()
    def call(method, path, **kwargs):
        response = session.request(method, args.base_url.rstrip("/") + path, timeout=60, **kwargs)
        if not response.ok:
            raise RuntimeError(f"{method} {path.split('?')[0]} returned HTTP {response.status_code}; stopped without retrying writes")
        return response.json()
    auth = call("POST", "/api/auth/login", json={"mobile": args.owner_mobile,
                "password": os.getenv("PARENT_PROVISION_OWNER_PASSWORD") or getpass.getpass("Owner password: ")})
    session.headers["Authorization"] = "Bearer " + auth["access_token"]
    settings = call("GET", "/api/settings/bootstrap")
    students, page = [], 1
    while True:
        data = call("GET", f"/api/students?page_size=100&page={page}")
        students.extend(data["items"])
        if len(students) >= data["total"]:
            break
        page += 1
    plan = make_plan(read_contacts(args.source, args.mother_row), students, settings, mapping)
    safe = [{k: v for k, v in row.items() if k not in {"mobile", "studentMobile", "studentId"}} for row in plan]
    print(json.dumps({"counts": dict(Counter(r["status"] for r in plan)), "rows": safe}, indent=2))
    if not args.apply:
        return
    if not settings.get("parentScopedMobileSupport"):
        raise SystemExit("Deploy parent mobile separation before applying; nothing changed")
    if any(r["status"] == "review" for r in plan):
        raise SystemExit("Resolve all review rows before applying; nothing changed")
    groups = defaultdict(list)
    for row in plan:
        if row["status"] in {"create", "link"}:
            groups[row["mobile"]].append(row)
    if any(len(rows) > 1 for rows in groups.values()) and not settings.get("parentSiblingSupport"):
        raise SystemExit("Deploy sibling support before applying this workbook; nothing changed")
    password = os.getenv("PARENT_PROVISION_TEMP_PASSWORD") or getpass.getpass("Shared temporary password: ")
    if len(password) < 6:
        raise SystemExit("Temporary password must have at least six characters")
    created = 0
    for number, siblings in groups.items():
        for index, row in enumerate(siblings):
            call("POST", "/api/settings/parent-access", json={"studentId": row["studentId"],
                 "fullName": "Parent of " + " / ".join(s["matchedName"] for s in siblings),
                 "mobile": number, "password": password, "contactType": "primary_contact",
                 "linkExistingParent": index > 0 or row.get("linkExistingParent", False)})
            created += 1
            print(f"Created/link verified by API: row {row['row']}, {row['matchedName']}")
    final = call("GET", "/api/settings/bootstrap")
    linked = {(r["studentId"], r["mobile"]) for r in final["parentAccess"] if r["isActive"]}
    assert all((r["studentId"], r["mobile"]) in linked for r in plan if r["status"] in {"create", "link", "existing"})
    print(f"Verified {created} new child links; existing passwords unchanged; missing contacts skipped.")


if __name__ == "__main__":
    main()
