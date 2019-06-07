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
    document_id = Column(
        Integer,
        ForeignKey('documents.id'),
        nullable=False,
    )
    tag = Column(String(128), nullable=False)
    title = Column(Text)
    exhibit = Column(String(128))
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('document_id', 'tag'),)
