from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class PetitionDocumentReferenceModel(Base):
    __tablename__ = 'petition_document_references'

    id = Column(Integer, primary_key=True)
    document_id = Column(
        Integer,
        ForeignKey('documents.id'),
        nullable=False,
    )
    type = Column(String(50), nullable=False)
    value = Column(String(255), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
