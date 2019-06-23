from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class ClaimModel(Base):
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True)
    patent_id = Column(
        Integer,
        ForeignKey('patents.id'),
    )
    patent_application_id = Column(
        Integer,
        ForeignKey('patent_applications.id'),
    )
    claim_number = Column(Integer, nullable=False)
    claim_text = Column(Text, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('patent_id', 'claim_number'),
        UniqueConstraint('patent_application_id', 'claim_number'),
    )
