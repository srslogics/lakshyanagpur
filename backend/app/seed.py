from .models import Lead, User
from .security import hash_password

def seed_development_data(db):
    """Explicit local-only seed; enabled only with SEED_DEMO_DATA=true."""
    if not db.query(User).first():
        db.add_all([
            User(email="owner@lakshyanagpur.in", full_name="Lakshya Director", role="owner", password_hash=hash_password("ChangeMe123!")),
            User(email="counsellor@lakshyanagpur.in", full_name="Priya Kulkarni", role="counsellor", password_hash=hash_password("ChangeMe123!")),
        ]); db.flush()
    if not db.query(Lead).first():
        owner = db.query(User).filter_by(role="owner").first()
        db.add(Lead(student="Aarav Thakre", mobile="9876543210", parent="Mr. Thakre", parent_mobile="9876543211", program="JEE 11th", source="website", counsellor="Priya Kulkarni", owner_id=owner.id, stage="New Enquiry", priority="high", next_action="Confirm counselling appointment", summary="High-intent website enquiry."))
    db.commit()
