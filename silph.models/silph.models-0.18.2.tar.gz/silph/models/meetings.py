
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    BigInt,
    String,
    Text,
    Boolean,
    Timestamp,
    ForeignKey,
    Numeric,
    Serial,
)

from .base import WebTable
from .users import User


class Meeting(WebTable, table_name='meetings'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, foreign_key=ForeignKey(User.id))
    code = Column(String(5))
    type = Column(SmallInt, default=0) # 0: VERIFICATION, 1: CELEBRITY, 2: BROADCAST

    latitude = Column(Numeric(12, 8), nullable=False)
    longitude = Column(Numeric(12, 8), nullable=False)

    created = Column(Timestamp)
    #updated = Column(Timestamp, nullable=False, default=datetime.datetime.now)

    async def payload(self):
        struct = {
            'id': self.id,
            'code': self.code,
            'type': self.type,
            'user': self.user.payload(),
            'created': int(self.created.timestamp()),
            'updated': int(self.updated.timestamp()),
            'version': 0,
        }

        return struct


class TravelersMet(WebTable, table_name='travelers_met'):
    user = Column.with_name('user_id', Integer, primary_key=True, foreign_key=ForeignKey(User.id))
    traveler = Column.with_name('traveler_id', Integer, primary_key=True, foreign_key=ForeignKey(User.id))
    meeting = Column.with_name('meeting_id', Integer, foreign_key=ForeignKey(Meeting.id))
    type = Column(SmallInt, default=0)

    latitude = Column(Numeric(12, 8), nullable=False, default=0.0)
    longitude = Column(Numeric(12, 8), nullable=False, default=0.0)

    created = Column(Timestamp)
