
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


class CommunityType(WebTable, table_name='communit_types'):
    id = Column(Serial, primary_key=True, unique=True)

    name = Column(Text, nullable=False)


class Community(WebTable, table_name='communities'):
    id = Column(Serial, primary_key=True, unique=True)

    type = Column.with_name('type_id', Integer, foreign_key=ForeignKey(CommunityType.id))

    identifier = Column(String, nullable=False)
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)

    description = Column(Text)
    status = Column(Integer)

    image = Column(String, nullable=False)
    lat = Column(Numeric(8, 12), nullable=False)
    lon = Column(Numeric(8, 12), nullable=False)
    size = Column(Integer, nullable=False)

    valor = Column(Boolean, nullable=False, default=True)
    mystic = Column(Boolean, nullable=False, default=True)
    instinct = Column(Boolean, nullable=False, default=True)

    min_player_level = Column(SmallInt, nullable=False, default=0)
    registrations = Column(SmallInt, nullable=False, default=0)
    scanners = Column.with_name('has_scanners', Boolean, nullable=False, default=0)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class CommunityAdmin(WebTable, table_name='community_admins'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, foreign_key=ForeignKey(User.id))
    community = Column.with_name('community_id', Integer, foreign_key=ForeignKey(Community.id))
    type = Column.with_name('type_id', Integer, foreign_key=ForeignKey(CommunityType.id))

    identifier = Column(String)
    owner = Column.with_name('is_owner', Boolean, nullable=False, default=True)


class DiscordMeta(WebTable, table_name='community_discord_meta'):
    community = Column.with_name('community_id', Integer, primary_key=True, foreign_key=ForeignKey(Community.id))

    server = Column(Text, nullable=False)
    channel = Column(BigInt)

    updated = Column(Timestamp)

class TelegramMeta(WebTable, table_name='community_telegram_meta'):
    community = Column.with_name('community_id', Integer, primary_key=True, foreign_key=ForeignKey(Community.id))

    invite_url = Column(Text)

    updated = Column(Timestamp)
