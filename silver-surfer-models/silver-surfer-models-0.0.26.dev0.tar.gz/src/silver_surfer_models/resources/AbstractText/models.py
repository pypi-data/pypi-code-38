from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)

from ...database import Base


class AbstractTextModel(Base):
    __tablename__ = 'abstract_texts'

    id = Column(Integer, primary_key=True)
    patent_id = Column(
        Integer,
        ForeignKey('patents.id'),
        nullable=False,
        unique=True,
    )
    abstract_text = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False)
