from sqlalchemy import (Column, Integer, String, Text)
from potnanny_core.database import Base


class Keychain(Base):
    """Store account/plugin/settings/other info in a key-value pair."""

    __tablename__ = 'keychains'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), nullable=False, unique=True)
    data = Column(Text, nullable=True)

    def __repr__(self):
        return "<Keychain({})>".format(self.name)
