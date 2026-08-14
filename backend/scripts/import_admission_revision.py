"""Preview or apply the latest client admission-register revision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.database import SessionLocal
from app.importers.admission_revision import AdmissionRevisionConflict, import_revision
from app.models import User


DEFAULT_MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "imports"
    / "admission_revision_2026_08_13.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--owner-mobile", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    with SessionLocal() as db:
        owner = db.query(User).filter_by(mobile=args.owner_mobile, role="owner").first()
        if not owner:
            raise AdmissionRevisionConflict("Active owner account not found")
        result = import_revision(db, manifest, owner, apply=args.apply)
        if not args.apply:
            db.rollback()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
