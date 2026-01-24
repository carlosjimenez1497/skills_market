from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Text, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Identity & dedup
    job_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    fingerprint: Mapped[str] = mapped_column(Text)

    # Source
    source: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text)
    job_view_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Job content
    company: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    language_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    first_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    times_seen: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
