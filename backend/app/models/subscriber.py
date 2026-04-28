from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    subscriber_type: Mapped[str] = mapped_column(String(30), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    oib: Mapped[str | None] = mapped_column(String(20), nullable=True)
    jmbg: Mapped[str | None] = mapped_column(String(20), nullable=True)

    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("cities.id"),
        nullable=True,
        index=True,
    )

    postal_code_id: Mapped[int | None] = mapped_column(
        ForeignKey("postal_codes.id"),
        nullable=True,
        index=True,
    )

    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

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