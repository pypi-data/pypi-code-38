from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class PTAB2DocumentModel(Base):
    __tablename__ = 'ptab2_documents'

    id = Column(Integer, primary_key=True)
    document_category = Column(String(100))
    document_filing_date = Column(DateTime)
    document_identifier = Column(String(100), nullable=False, unique=True)
    document_name = Column(String(256))
    document_number = Column(String(20))
    document_size = Column(String(20))
    document_title_text = Column(String(500))
    document_type_name = Column(String(256))
    filing_party_category = Column(String(256))
    media_type_category = Column(String(256))
    petitioner_application_number_text = Column(String(256))
    petitioner_counsel_name = Column(String(100))
    petitioner_grant_date = Column(DateTime)
    petitioner_group_art_unit_number = Column(String(20))
    petitioner_inventor_name = Column(String(256))
    petitioner_party_name = Column(String(256))
    petitioner_patent_number = Column(String(20))
    petitioner_patent_owner_name = Column(String(256))
    petitioner_technology_center_number = Column(String(20))
    proceeding_number = Column(String(20))
    proceeding_type_category = Column(String(20))
    respondent_application_number_text = Column(String(20))
    respondent_counsel_name = Column(String(100))
    respondent_grant_date = Column(DateTime)
    respondent_group_art_unit_number = Column(String(20))
    respondent_inventor_name = Column(String(256))
    respondent_party_name = Column(String(256))
    respondent_patent_number = Column(String(20))
    respondent_patent_owner_name = Column(String(256))
    respondent_technology_center_number = Column(String(20))
    subproceeding_type_category = Column(String(20))
    file_id = Column(Integer, ForeignKey('files.id'))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
