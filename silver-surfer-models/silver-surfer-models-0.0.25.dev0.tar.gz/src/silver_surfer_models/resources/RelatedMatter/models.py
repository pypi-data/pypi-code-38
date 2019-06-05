from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class RelatedMatterModel(Base):
    __tablename__ = 'related_matters'

    id = Column(Integer, primary_key=True)
    document_id = Column(
        Integer,
        ForeignKey('documents.id'),
        nullable=False,
    )
    pacer_case_id = Column(
        Integer,
        ForeignKey('pacer_cases.id'),
    )
    trial_id = Column(
        Integer,
        ForeignKey('trials.id'),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('document_id', 'pacer_case_id'),
        UniqueConstraint('document_id', 'trial_id'),
    )
