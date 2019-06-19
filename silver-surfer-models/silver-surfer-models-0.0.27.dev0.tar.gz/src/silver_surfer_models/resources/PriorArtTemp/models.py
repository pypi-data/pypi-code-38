from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)

from ...database import Base


class PriorArtTempModel(Base):
    __tablename__ = 'prior_arts_temp'

    id = Column(Integer, primary_key=True)
    prior_art_id = Column(
        Integer,
        ForeignKey('prior_arts.id'),
        nullable=False,
    )
    prior_art_detail = Column(Text)
    updated_at = Column(DateTime, nullable=False)
