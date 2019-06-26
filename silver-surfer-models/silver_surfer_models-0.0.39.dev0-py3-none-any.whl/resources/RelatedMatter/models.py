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
    ptab2_document_id = Column(
        Integer,
        ForeignKey('ptab2_documents.id'),
        nullable=False,
    )
    related_pacer_case_id = Column(
        Integer,
        ForeignKey('pacer_cases.id'),
    )
    related_ptab2_proceeding_id = Column(
        Integer,
        ForeignKey('ptab2_proceedings.id'),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('ptab2_document_id', 'related_pacer_case_id'),
        UniqueConstraint('ptab2_document_id', 'related_ptab2_proceeding_id'),
    )
