
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


class Event(WebTable, table_name='events'):
    id = Column(Serial, primary_key=True, unique=True)

    slug = Column(String(25), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    badge = Column.with_name('badge_id', Integer)
    image = Column(String)

    is_global = Column(Boolean)

    start = Column(Timestamp)
    end = Column(Timestamp)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class EventCommunities(WebTable, table_name='event_communities'):
    event_id = Column(Integer, primary_key=True)
    community_id = Column(Integer, primary_key=True)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class EventStaff(WebTable, table_name='event_staff'):
    user_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, primary_key=True)
    community_id = Column(Integer, primary_key=True)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class EventCheckin(WebTable, table_name='event_checkins'):
    user_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, primary_key=True)

    staff_id = Column(Integer, nullable=False)
    code = Column(String(5))

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)
