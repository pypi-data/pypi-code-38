from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint)
from datetime import datetime

from ...database import Base


class DocumentReferenceModel(Base):
    __tablename__ = 'document_references'

    id = Column(Integer, primary_key=True)
    ptab2_document_id = Column(
        Integer,
        ForeignKey('ptab2_documents.id'),
        nullable=False,
    )
    type = Column(String(50), nullable=False)
    value = Column(String(128), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('ptab2_document_id', 'type', 'value'),)
