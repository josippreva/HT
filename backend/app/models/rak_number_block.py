from sqlalchemy import String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class RakNumberBlock(Base):
    __tablename__ = "rak_number_blocks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    area_code_id: Mapped[int] = mapped_column(
        ForeignKey("area_codes.id"),
        nullable=False,
        index=True,
    )

    operator_name: Mapped[str] = mapped_column(String(150), nullable=False)

    block_start: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    block_end: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    block_size: Mapped[int] = mapped_column(Integer, nullable=False)

    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    area_code = relationship("AreaCode")