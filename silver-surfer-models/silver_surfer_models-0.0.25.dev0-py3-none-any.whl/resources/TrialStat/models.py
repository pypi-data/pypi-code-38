from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint)
from datetime import datetime

from ...database import Base


class TrialStatModel(Base):
    __tablename__ = 'trial_stats'

    id = Column(Integer, primary_key=True)

    stat_type = Column(String(190), nullable=False)
    name = Column(String(190), nullable=False)
    ref_counts_by_type = Column(Text)
    id_count = Column(Integer)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('stat_type', 'name'),
    )
