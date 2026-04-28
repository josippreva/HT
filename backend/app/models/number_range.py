from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class NumberRange(Base):
    __tablename__ = "number_ranges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    rak_block_id: Mapped[int] = mapped_column(
        ForeignKey("rak_number_blocks.id"),
        nullable=False,
        index=True,
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[int | None] = mapped_column(
        ForeignKey("devices.id"),
        nullable=True,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    range_start: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    range_end: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    range_size: Mapped[int] = mapped_column(Integer, nullable=False)

    generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    rak_block = relationship("RakNumberBlock")
    location = relationship("Location")
    device = relationship("Device")