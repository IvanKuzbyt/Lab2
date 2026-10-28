"""Add minimum_stock to products (Lab 7 variant 10)."""
from alembic import op
import sqlalchemy as sa
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None
def upgrade():
    op.add_column("products", sa.Column("minimum_stock", sa.Integer, nullable=False, server_default="5"))
def downgrade():
    op.drop_column("products", "minimum_stock")
