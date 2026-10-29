from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ProductRecord(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("quantity >= 0"),
        CheckConstraint("unit_price >= 0"),
        CheckConstraint("minimum_stock >= 0"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    minimum_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    operations: Mapped[list["StockOperationRecord"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class StockOperationRecord(Base):
    __tablename__ = "stock_operations"
    __table_args__ = (CheckConstraint("quantity > 0"), CheckConstraint("operation_type IN ('receipt', 'write_off')"))
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    product: Mapped[ProductRecord] = relationship(back_populates="operations")
