from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from datetime import datetime

from ...database import Base


class PTAB2DecisionModel(Base):
    __tablename__ = 'ptab2_decisions'

    id = Column(Integer, primary_key=True)
    board_rulings = Column(Text)
    decision_date = Column(DateTime)
    decision_type_category = Column(String(256))
    document_identifier = Column(String(256))
    document_name = Column(String(256))
    identifier = Column(String(100), nullable=False, unique=True)
    issue_type = Column(Text)
    petitioner_application_number_text = Column(String(256))
    petitioner_counsel_name = Column(String(256))
    petitioner_grant_date = Column(DateTime)
    petitioner_group_art_unit_number = Column(String(256))
    petitioner_inventor_name = Column(String(256))
    petitioner_party_name = Column(String(256))
    petitioner_patent_number = Column(String(50))
    petitioner_patent_owner_name = Column(String(256))
    petitioner_technology_center_number = Column(String(256))
    proceeding_number = Column(String(20))
    proceeding_type_category = Column(String(20))
    respondent_application_number_text = Column(String(50))
    respondent_counsel_name = Column(String(100))
    respondent_grant_date = Column(DateTime)
    respondent_group_art_unit_number = Column(String(50))
    respondent_inventor_name = Column(String(100))
    respondent_party_name = Column(String(256))
    respondent_patent_number = Column(String(20))
    respondent_patent_owner_name = Column(String(256))
    respondent_technology_center_number = Column(String(20))
    subdecision_type_category = Column(String(100))
    subproceeding_type_category = Column(String(100))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
