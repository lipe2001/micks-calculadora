"""create sales table

Revision ID: 0001_create_sales_table
Revises: 
Create Date: 2025-10-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_create_sales_table"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),

        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),

        sa.Column("n_cellphones", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_computers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_smart_tvs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_tv_box", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_others", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gamer", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        sa.Column("total_weight", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("plan", sa.String(length=20), nullable=False),
        sa.Column("speed_mbps", sa.Integer(), nullable=False),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_sales_email", "sales", ["email"])
    op.create_index("ix_sales_created_at", "sales", ["created_at"])

def downgrade() -> None:
    op.drop_index("ix_sales_created_at", table_name="sales")
    op.drop_index("ix_sales_email", table_name="sales")
    op.drop_table("sales")