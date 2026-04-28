from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AreaCode(Base):
    __tablename__ = "area_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"),
        nullable=False,
        index=True,
    )

    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id"),
        nullable=False,
        index=True,
    )

    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("cities.id"),
        nullable=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    entity = relationship("Entity")
    region = relationship("Region")
    city = relationship("City")