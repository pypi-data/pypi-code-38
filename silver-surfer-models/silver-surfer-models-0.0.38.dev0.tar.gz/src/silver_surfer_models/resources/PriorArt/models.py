from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from ...database import Base


class PriorArtModel(Base):
    __tablename__ = 'prior_arts'

    id = Column(Integer, primary_key=True)
    ptab2_document_id = Column(
        Integer,
        ForeignKey('ptab2_documents.id'),
    )
    tag = Column(String(128), nullable=False)
    title = Column(Text)
    exhibit = Column(String(128))
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('ptab2_document_id', 'tag'),)
