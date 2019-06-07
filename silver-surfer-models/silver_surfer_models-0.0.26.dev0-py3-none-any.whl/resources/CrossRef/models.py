from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class CrossRefModel(Base):
    __tablename__ = 'cross_refs'

    id = Column(Integer, primary_key=True)
    doi = Column(String(191), nullable=False)
    authors = Column(Text)
    doi_url = Column(String(500))
    issn = Column(Text)
    issue = Column(String(10))
    journal = Column(String(500))
    pages = Column(String(128))
    pmid = Column(String(50))
    ref_type = Column(String(128))
    text = Column(Text)
    title = Column(Text)
    volume = Column(String(50))
    year = Column(Integer)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('doi'),)
