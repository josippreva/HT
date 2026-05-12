from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    number_range_id: Mapped[int] = mapped_column(
        ForeignKey("number_ranges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subscriber_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscribers.id"),
        nullable=True,
        index=True,
    )

    number_value: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    number_category: Mapped[str] = mapped_column(
        String(30),
        default="standard",
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="slobodan",
        nullable=False,
        index=True,
    )

    assigned_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    quarantine_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    number_range = relationship("NumberRange")
    subscriber = relationship("Subscriber")