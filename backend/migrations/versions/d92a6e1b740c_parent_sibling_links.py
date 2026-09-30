"""Allow one parent identity to link to multiple children without copying users."""
from alembic import op
import sqlalchemy as sa

revision = "d92a6e1b740c"
down_revision = "a6d9c4e72b10"
branch_labels = None
depends_on = None


def upgrade():
    naming = {"pk": "pk_%(table_name)s"}
    inspector = sa.inspect(op.get_bind())
    constraint = inspector.get_pk_constraint("parent_accounts")["name"] or "pk_parent_accounts"
    with op.batch_alter_table("parent_accounts", naming_convention=naming) as batch:
        batch.drop_constraint(constraint, type_="primary")
        batch.create_primary_key("pk_parent_accounts", ["user_id", "student_id"])


def downgrade():
    # Never silently delete sibling links during rollback.
    duplicates = op.get_bind().execute(sa.text(
        "SELECT user_id FROM parent_accounts GROUP BY user_id HAVING COUNT(*) > 1"
    )).first()
    if duplicates:
        raise RuntimeError("Cannot downgrade while parents have multiple linked children")
    with op.batch_alter_table("parent_accounts") as batch:
        batch.drop_constraint("pk_parent_accounts", type_="primary")
        batch.create_primary_key("pk_parent_accounts", ["user_id"])
