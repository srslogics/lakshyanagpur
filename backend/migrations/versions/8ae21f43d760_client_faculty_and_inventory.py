"""client-approved faculty allocation and inventory catalogue"""

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "8ae21f43d760"
down_revision = "f7b31d9a2c40"
branch_labels = None
depends_on = None


FACULTIES = (
    ("Meet Sir", "Physics", "PHY", (("Tatva", "JEE"), ("Tatva", "NEET"))),
    (
        "Kajal Ma'am",
        "Physics",
        "PHY",
        (
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    ),
    (
        "Jitendra Sir",
        "Chemistry",
        "CHEM",
        (
            ("Tatva", "JEE"),
            ("Tatva", "NEET"),
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    ),
    (
        "Anita Ma'am",
        "Maths",
        "MATH",
        (
            ("Tatva", "JEE"),
            ("Tatva", "NEET"),
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    ),
    (
        "Kanchan Ma'am",
        "Biology",
        "BIO",
        (
            ("Tatva", "JEE"),
            ("Tatva", "NEET"),
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    ),
)

INVENTORY = (
    ("ESS-MATH-B1", "Essential Math Booklet 1", "book"),
    ("ESS-CHEM-B1", "Essential Chemistry Booklet 1", "book"),
    ("ESS-PHYS-B1", "Essential Physics Booklet 1", "book"),
    ("ESS-BIO-B1", "Essential Biology Booklet 1", "book"),
    ("BAG-GENERIC", "Bag", "bag"),
    ("TSHIRT-GENERIC", "T-shirt", "apparel"),
)


def _id(prefix):
    return f"{prefix}_{uuid4().hex}"


def upgrade():
    with op.batch_alter_table("faculty_teaching_assignments") as batch_op:
        batch_op.alter_column(
            "created_by",
            existing_type=sa.String(length=64),
            nullable=True,
        )

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("sku", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("source_note", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_inventory_items_category",
        "inventory_items",
        ["category"],
    )
    op.create_index(
        "ix_inventory_items_created_by",
        "inventory_items",
        ["created_by"],
    )
    op.create_index(
        "ix_inventory_items_is_active",
        "inventory_items",
        ["is_active"],
    )
    op.create_index(
        "ix_inventory_items_name",
        "inventory_items",
        ["name"],
    )
    op.create_index(
        "ix_inventory_items_sku",
        "inventory_items",
        ["sku"],
        unique=True,
    )

    connection = op.get_bind()
    now = datetime.now(timezone.utc)
    inventory_items = sa.table(
        "inventory_items",
        sa.column("id", sa.String(length=64)),
        sa.column("sku", sa.String(length=40)),
        sa.column("name", sa.String(length=255)),
        sa.column("category", sa.String(length=40)),
        sa.column("unit", sa.String(length=40)),
        sa.column("quantity_on_hand", sa.Integer()),
        sa.column("notes", sa.Text()),
        sa.column("source_note", sa.String(length=255)),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_by", sa.String(length=64)),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    for sku, name, category in INVENTORY:
        exists = connection.execute(
            sa.select(inventory_items.c.id).where(inventory_items.c.sku == sku)
        ).scalar_one_or_none()
        if exists:
            continue
        connection.execute(inventory_items.insert().values(
            id=_id("inv"),
            sku=sku,
            name=name,
            category=category,
            unit="piece",
            quantity_on_hand=None,
            notes="Quantity and variants have not been supplied by the client.",
            source_note="Client confirmation · 28 Jul 2026",
            is_active=True,
            created_by=None,
            created_at=now,
            updated_at=now,
        ))

    users = sa.table(
        "users",
        sa.column("id", sa.String(length=64)),
        sa.column("full_name", sa.String(length=255)),
        sa.column("mobile", sa.String(length=10)),
        sa.column("email", sa.String(length=255)),
        sa.column("password_hash", sa.String(length=255)),
        sa.column("role", sa.String(length=64)),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    subjects = sa.table(
        "subjects",
        sa.column("id", sa.String(length=64)),
        sa.column("name", sa.String(length=120)),
        sa.column("code", sa.String(length=24)),
        sa.column("program", sa.String(length=255)),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    batches = sa.table(
        "batches",
        sa.column("id", sa.String(length=64)),
        sa.column("name", sa.String(length=120)),
        sa.column("program", sa.String(length=255)),
    )
    assignments = sa.table(
        "faculty_teaching_assignments",
        sa.column("id", sa.String(length=64)),
        sa.column("faculty_id", sa.String(length=64)),
        sa.column("batch_id", sa.String(length=64)),
        sa.column("subject_id", sa.String(length=64)),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_by", sa.String(length=64)),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    for faculty_name, subject_name, subject_code, scopes in FACULTIES:
        faculty_id = connection.execute(
            sa.select(users.c.id).where(
                users.c.full_name == faculty_name,
                users.c.role == "faculty",
            )
        ).scalar_one_or_none()
        if not faculty_id:
            faculty_id = _id("usr")
            connection.execute(users.insert().values(
                id=faculty_id,
                full_name=faculty_name,
                mobile=None,
                email=None,
                password_hash="unprovisioned",
                role="faculty",
                is_active=True,
                created_at=now,
                updated_at=now,
            ))

        subject_id = connection.execute(
            sa.select(subjects.c.id).where(subjects.c.code == subject_code)
        ).scalar_one_or_none()
        if not subject_id:
            subject_id = _id("sub")
            connection.execute(subjects.insert().values(
                id=subject_id,
                name=subject_name,
                code=subject_code,
                program="All programs",
                is_active=True,
                created_at=now,
                updated_at=now,
            ))

        for batch_name, program in scopes:
            batch_id = connection.execute(
                sa.select(batches.c.id).where(
                    batches.c.name == batch_name,
                    batches.c.program == program,
                )
            ).scalar_one_or_none()
            if not batch_id:
                continue
            existing = connection.execute(
                sa.select(assignments.c.id).where(
                    assignments.c.faculty_id == faculty_id,
                    assignments.c.batch_id == batch_id,
                    assignments.c.subject_id == subject_id,
                )
            ).scalar_one_or_none()
            if existing:
                continue
            connection.execute(assignments.insert().values(
                id=_id("fta"),
                faculty_id=faculty_id,
                batch_id=batch_id,
                subject_id=subject_id,
                is_active=True,
                created_by=None,
                created_at=now,
                updated_at=now,
            ))


def downgrade():
    op.drop_index("ix_inventory_items_sku", table_name="inventory_items")
    op.drop_index("ix_inventory_items_name", table_name="inventory_items")
    op.drop_index("ix_inventory_items_is_active", table_name="inventory_items")
    op.drop_index("ix_inventory_items_created_by", table_name="inventory_items")
    op.drop_index("ix_inventory_items_category", table_name="inventory_items")
    op.drop_table("inventory_items")
    connection = op.get_bind()
    assignments = sa.table(
        "faculty_teaching_assignments",
        sa.column("faculty_id", sa.String(length=64)),
        sa.column("created_by", sa.String(length=64)),
    )
    connection.execute(
        assignments.update()
        .where(assignments.c.created_by.is_(None))
        .values(created_by=assignments.c.faculty_id)
    )
    with op.batch_alter_table("faculty_teaching_assignments") as batch_op:
        batch_op.alter_column(
            "created_by",
            existing_type=sa.String(length=64),
            nullable=False,
        )
