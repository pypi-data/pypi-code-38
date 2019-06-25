from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class LongTaskModel(Base):
    __tablename__ = 'long_tasks'

    id = Column(Integer, primary_key=True)
    trial_id = Column(
        Integer,
        ForeignKey('trials.id'),
        nullable=False,
    )
    name = Column(String(128), nullable=False)
    state = Column(String(128), nullable=False)
    progress = Column(Float, nullable=False)
    celery_task_id = Column(String(128), nullable=False)
    result = Column(String(1024))
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('celery_task_id'),)
