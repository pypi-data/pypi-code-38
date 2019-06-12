from sqlalchemy import (Column, Integer, String, Text, DateTime,ForeignKey,func)
from sqlalchemy.orm import relationship
from potnanny_core.database import Base


class Grow(Base):
    """Keep track of the stages in a grow cycle."""

    __tablename__ = 'grows'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), nullable=False)
    notes = Column(Text, nullable=True)
    started = Column(DateTime, default=func.now())
    transitioned = Column(DateTime, nullable=True)
    ended = Column(DateTime, nullable=True)

    # relationships
    room_id = Column(Integer, ForeignKey('rooms.id'))

    def __repr__(self):
        return "<Grow({})>".format(self.name)
