"""Keep parent mobile identities separate without changing existing passwords."""
from alembic import op
import sqlalchemy as sa

revision = "e73b91c8f240"
down_revision = "d92a6e1b740c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_users_mobile", table_name="users")
    op.create_index("ix_users_mobile", "users", ["mobile"], unique=False)
    for name, predicate in [("parent", "role = 'parent'"), ("nonparent", "role <> 'parent'")]:
        op.create_index(f"uq_users_{name}_mobile", "users", ["mobile"], unique=True,
                        postgresql_where=sa.text(predicate), sqlite_where=sa.text(predicate))


def downgrade():
    duplicate = op.get_bind().execute(sa.text("SELECT mobile FROM users WHERE mobile IS NOT NULL GROUP BY mobile HAVING COUNT(*) > 1 LIMIT 1")).first()
    if duplicate:
        raise RuntimeError("Cannot downgrade while parent and student accounts share a mobile number")
    op.drop_index("uq_users_parent_mobile", table_name="users")
    op.drop_index("uq_users_nonparent_mobile", table_name="users")
    op.drop_index("ix_users_mobile", table_name="users")
    op.create_index("ix_users_mobile", "users", ["mobile"], unique=True)
