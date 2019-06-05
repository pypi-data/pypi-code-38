from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)

from ...database import Base


class ProcessorResultTagModel(Base):
    __tablename__ = 'processor_result_tags'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False)
    processor_result_id = Column(Integer, nullable=False)
    processor_name = Column(String(128), nullable=False)
    tag = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False)
