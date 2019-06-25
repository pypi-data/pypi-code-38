from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
)

from ...database import Base


class TrialModel(Base):
    __tablename__ = 'trials'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    ptab_trial_num = Column(String(128), nullable=False, unique=True)
    trial_filing_date = Column(DateTime, nullable=False)
    patent_num = Column(String(128), nullable=False)

    accorded_filing_date = Column(DateTime)
    institution_decision_date = Column(DateTime)
    application_number = Column(String(128))
    inventor_name = Column(String(500))
    patent_owner_name = Column(String(500))
    petitioner_party_name = Column(String(500))
    prosecution_status = Column(String(128))

    is_cleaned = Column(Boolean, nullable=False)
    is_processed = Column(Boolean, nullable=False)
    updated_at = Column(DateTime, nullable=False)
