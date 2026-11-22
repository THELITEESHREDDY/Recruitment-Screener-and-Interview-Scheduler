"""add users and job ownership

Revision ID: 22b3c775eae9
Revises: b330271b73ca
Create Date: 2026-11-21 20:08:36.068522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22b3c775eae9'
down_revision: Union[str, Sequence[str], None] = 'b330271b73ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )

    # SQLite-compatible table alteration
    with op.batch_alter_table("job_descriptions") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                nullable=True
            )
        )

        batch_op.create_foreign_key(
            "fk_job_descriptions_user_id",
            "users",
            ["user_id"],
            ["id"]
        )

        batch_op.create_index(
            "ix_job_descriptions_user_id",
            ["user_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("job_descriptions") as batch_op:
        batch_op.drop_constraint(
            "fk_job_descriptions_user_id",
            type_="foreignkey"
        )

        batch_op.drop_index(
            "ix_job_descriptions_user_id"
        )

        batch_op.drop_column("user_id")

    op.drop_index(
        "ix_users_email",
        table_name="users"
    )

    op.drop_table("users")