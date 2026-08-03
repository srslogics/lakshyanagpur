#!/usr/bin/env python3
"""Read-only production smoke checks for every Lakshya portal.

Credentials are accepted only through LAKSHYA_SMOKE_ACCOUNTS so they do not
appear in shell history or source control.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


PORTALS = {
    "operations": ("/operations", "Lakshya · Operations"),
    "student": ("/student-app/", "Lakshya Student"),
    "parent": ("/parent-app/", "Lakshya Parent"),
    "faculty": ("/faculty-app/", "Lakshya Faculty"),
    "attendance_operator": ("/attendance-app/", "Lakshya Attendance Desk"),
}


def request(base_url: str, path: str, *, payload=None, token=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json", "Cache-Control": "no-cache"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    call = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(call, timeout=30) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def read_accounts() -> list[dict[str, str]]:
    raw = os.getenv("LAKSHYA_SMOKE_ACCOUNTS", "").strip()
    if not raw:
        return []
    accounts = json.loads(raw)
    if not isinstance(accounts, list):
        raise ValueError("LAKSHYA_SMOKE_ACCOUNTS must be a JSON array")
    required = {"role", "mobile", "password"}
    for account in accounts:
        if not isinstance(account, dict) or not required.issubset(account):
            raise ValueError("Every smoke account needs role, mobile, and password")
        if account["role"] not in PORTALS:
            raise ValueError(f"Unsupported smoke role: {account['role']}")
    return accounts


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the deployed Lakshya release")
    parser.add_argument(
        "--base-url",
        default=os.getenv("LAKSHYA_BASE_URL", "https://lakshyaedutech.onrender.com"),
    )
    args = parser.parse_args()
    failures: list[str] = []
    results: list[str] = []

    status, headers, body = request(args.base_url, "/api/health")
    try:
        health = json.loads(body)
    except json.JSONDecodeError:
        health = {}
    release = str(health.get("release") or headers.get("x-lakshya-release") or "unknown")
    if status != 200 or health.get("status") != "ok":
        failures.append(f"health returned HTTP {status}")
    elif release in {"", "unknown", "development"} and "onrender.com" in args.base_url:
        failures.append("live health response does not identify its deployed release")
    else:
        results.append(f"health ok · release {release[:12]}")

    for portal, (path, expected_title) in PORTALS.items():
        page_status, _, page_body = request(args.base_url, path)
        page_text = page_body.decode("utf-8", errors="replace")
        if page_status != 200 or expected_title not in page_text:
            failures.append(f"{portal} portal failed (HTTP {page_status})")
        else:
            results.append(f"{portal} page ok")

    try:
        accounts = read_accounts()
    except (ValueError, json.JSONDecodeError) as error:
        failures.append(str(error))
        accounts = []

    for account in accounts:
        login_status, _, login_body = request(
            args.base_url,
            "/api/auth/login",
            payload={"mobile": account["mobile"], "password": account["password"]},
        )
        try:
            login = json.loads(login_body)
        except json.JSONDecodeError:
            login = {}
        user = login.get("user", {})
        if login_status != 200 or user.get("role") != account["role"]:
            failures.append(f"{account['role']} authentication failed (HTTP {login_status})")
            continue
        me_status, _, me_body = request(
            args.base_url,
            "/api/auth/me",
            token=login.get("access_token"),
        )
        try:
            me = json.loads(me_body)
        except json.JSONDecodeError:
            me = {}
        if me_status != 200 or me.get("id") != user.get("id"):
            failures.append(f"{account['role']} session verification failed (HTTP {me_status})")
            continue
        results.append(f"{account['role']} authentication ok")

    print("Lakshya production smoke check")
    for result in results:
        print(f"  PASS  {result}")
    for failure in failures:
        print(f"  FAIL  {failure}")
    if not accounts:
        print("  INFO  authentication skipped; LAKSHYA_SMOKE_ACCOUNTS is not set")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
