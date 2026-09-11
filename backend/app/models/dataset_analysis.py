from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DatasetAnalysis(Base):
    __tablename__ = "dataset_analysis"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    dataset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("datasets.id"),
        nullable=False,
    )

    analysis: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    insights: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    ai_insight: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )