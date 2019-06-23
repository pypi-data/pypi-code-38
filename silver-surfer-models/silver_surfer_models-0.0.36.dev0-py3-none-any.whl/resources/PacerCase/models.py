from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class PacerCaseModel(Base):
    __tablename__ = 'pacer_cases'

    id = Column(Integer, primary_key=True)
    case_no = Column(String(256))
    court_id = Column(String(191))
    pacer_case_external_id = Column(String(191))
    cause = Column(String(256))
    county = Column(String(256))
    defendant = Column(String(256))
    disposition = Column(String(256))
    filed_date = Column(DateTime)
    flags = Column(String(256))
    jurisdiction = Column(String(256))
    lead_case = Column(String(256))
    nature_of_suit = Column(String(256))
    office = Column(String(256))
    plaintiff = Column(String(256))
    related_case = Column(String(256))
    terminated_date = Column(DateTime)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('court_id', 'pacer_case_external_id'),)
