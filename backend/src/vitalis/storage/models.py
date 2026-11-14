from typing import Any

from sqlalchemy import JSON, Boolean, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ObservationRecord(Base):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    crew_member_id: Mapped[str] = mapped_column(String(80), index=True)
    metric_id: Mapped[str] = mapped_column(String(100), index=True)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    unit: Mapped[str] = mapped_column(String(40))
    observed_at: Mapped[str] = mapped_column(String(40), index=True)
    source: Mapped[str] = mapped_column(String(32))
    synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
