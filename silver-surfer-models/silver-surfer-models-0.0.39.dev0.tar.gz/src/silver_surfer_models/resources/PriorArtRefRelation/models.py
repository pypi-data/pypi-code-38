from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class PriorArtRefRelationModel(Base):
    __tablename__ = 'prior_art_ref_relations'

    id = Column(Integer, primary_key=True)
    prior_art_id = Column(
        Integer,
        ForeignKey('prior_arts.id'),
        nullable=False,
    )
    cross_ref_id = Column(
        Integer,
        ForeignKey('cross_refs.id'),
    )
    patent_id = Column(
        Integer,
        ForeignKey('patents.id'),
    )
    patent_application_id = Column(
        Integer,
        ForeignKey('patent_applications.id'),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint('prior_art_id', 'cross_ref_id'),
        UniqueConstraint('prior_art_id', 'patent_id'),
        UniqueConstraint('prior_art_id', 'patent_application_id'),
    )
