import json
from pathlib import Path


MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "imports"
    / "manual_attendance_2026_08_18_27.json"
)


def test_signed_manual_attendance_manifest_is_complete_and_consistent():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    registers = manifest["registers"]

    assert len(registers) == 17
    assert {row["date"] for row in registers} == {
        "2026-08-18",
        "2026-08-19",
        "2026-08-20",
        "2026-08-22",
        "2026-08-23",
        "2026-08-24",
        "2026-08-25",
        "2026-08-26",
        "2026-08-27",
    }
    assert manifest["controls"]["missingDatesNotFabricated"] == [
        "2026-08-21"
    ]
    assert manifest["controls"]["missingRegistersNotFabricated"] == [
        "2026-08-27:Essential"
    ]
    assert len(manifest["rosters"]["Tatva"]) == 22
    assert len(manifest["rosters"]["Essential"]) == 36

    register_keys = set()
    for register in registers:
        key = (register["date"], register["batch"])
        assert key not in register_keys
        register_keys.add(key)
        roster_codes = {
            row["code"] for row in manifest["rosters"][register["batch"]]
        }
        assert set(register["absentCodes"]) <= roster_codes
        assert set(register.get("presentReasonOverrides", {})) <= roster_codes

    assert ("2026-08-27", "Essential") not in register_keys
