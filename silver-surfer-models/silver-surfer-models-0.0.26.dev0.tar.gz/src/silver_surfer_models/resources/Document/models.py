from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class DocumentModel(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    trial_id = Column(
        Integer,
        ForeignKey('trials.id'),
        nullable=False,
    )
    ptab_document_id = Column(Integer, nullable=False)
    title = Column(String(128))
    filing_date = Column(DateTime)
    type = Column(String(128))
    file_id = Column(Integer)
    has_smart_doc = Column(Boolean)
    exhibit_number = Column(String(128))
    document_number = Column(String(128))
    is_petition_doc = Column(Boolean, default=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('ptab_document_id'),
        {'extend_existing': True},
    )
