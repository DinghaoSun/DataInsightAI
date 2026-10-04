from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    row_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    column_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        default=None,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )
