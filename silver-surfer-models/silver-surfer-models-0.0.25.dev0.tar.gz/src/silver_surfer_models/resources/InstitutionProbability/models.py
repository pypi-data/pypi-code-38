from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint, Boolean, Float)
from datetime import datetime

from ...database import Base


class InstitutionProbabilityModel(Base):
    __tablename__ = 'institution_probabilities'

    id = Column(Integer, primary_key=True)

    ptab_trial_num = Column(String(190), unique=True, nullable=False)
    is_instituted = Column(Boolean)
    probability_of_institution = Column(Float)
    probability_end_before_trial_end = Column(Float)
    probability_of_all_claims_instituted = Column(Float)
    probability_of_some_claims_instituted = Column(Float)

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
