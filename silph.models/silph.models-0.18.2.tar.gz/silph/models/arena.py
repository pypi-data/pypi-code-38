
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

from .base import ArenaTable


class User(ArenaTable, table_name='users'):
    id = Column(Serial, primary_key=True, unique=True)

    tsr_id = Column(Integer)
    status = Column(Integer, nullable=False)

    email = Column(Text)
    username = Column.with_name('in_game_username', String)

    confirmed = Column(Boolean, nullable=False)

    mmr = Column.with_name('current_mmr', Numeric(9, 4))
    wins = Column.with_name('total_wins', Integer)
    losses = Column.with_name('total_losses', Integer)
    unique_wins = Column(Integer)

    created = Column(Timestamp)
    updated = Column(Timestamp)


class Invitation(ArenaTable, table_name='invitations'):
    id = Column(Serial, primary_key=True, unique=True)

    cup = Column.with_name('tournament_type_id', Integer, nullable=False)
    user = Column.with_name('user_id', Integer, nullable=False)

    tournament = Column.with_name('tournament_id', Integer)
    rsvp = Column.with_name('rsvp_time', Timestamp)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class Tournament(ArenaTable, table_name='tournaments'):
    id = Column(Serial, primary_key=True, unique=True)

    community = Column.with_name('community_id', Integer, nullable=False)
    cup = Column.with_name('tournament_type_id', Integer, nullable=False)

    ranked = Column.with_name('is_ranked', Boolean)

    name = Column(Text)

    # Incomplete

    created = Column(Timestamp)
    updated = Column(Timestamp)
