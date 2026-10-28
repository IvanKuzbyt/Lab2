"""Create warehouse tables (base revision)."""
from alembic import op
import sqlalchemy as sa
revision = "001"
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("products", sa.Column("id", sa.Integer, primary_key=True), sa.Column("code", sa.String(64), nullable=False, unique=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("quantity", sa.Integer, nullable=False), sa.Column("unit_price", sa.Numeric(12,2), nullable=False), sa.CheckConstraint("quantity >= 0"), sa.CheckConstraint("unit_price >= 0"))
    op.create_table("stock_operations", sa.Column("id", sa.Integer, primary_key=True), sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False), sa.Column("operation_type", sa.String(16), nullable=False), sa.Column("quantity", sa.Integer, nullable=False), sa.Column("quantity_after", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime), sa.CheckConstraint("quantity > 0"), sa.CheckConstraint("operation_type IN ('receipt', 'write_off')"))
def downgrade():
    op.drop_table("stock_operations")
    op.drop_table("products")
