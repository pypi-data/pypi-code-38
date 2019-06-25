from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)

from ...database import Base


class ProcessorResultModel(Base):
    __tablename__ = 'processor_results'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False)
    processor_name = Column(String(128), nullable=False)
    result = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False)
