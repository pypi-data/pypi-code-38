from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class FileModel(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    file_format = Column(String(128), nullable=False)
    s3_bucket_name = Column(String(128), nullable=False)
    s3_key_name = Column(String(128), nullable=False)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            's3_bucket_name',
            's3_key_name',
        ),
    )
