
from asyncqlio import (
    Column,
    Integer,
    String,
    Text,
    Timestamp,
    Serial,
    Boolean,
)

from .base import WebTable


class ResearchTask(WebTable, table_name='research_tasks'):
    id = Column(Serial, primary_key=True, unique=True)

    group = Column.with_name('group_num', Integer)
    text = Column.with_name('task_text', String)
    verified = Column.with_name('is_verified', Boolean)

    pokemon1 = Column.with_name('pokemon_1', String)
    p1_verified = Column(Boolean)

    pokemon2 = Column.with_name('pokemon_2', String)
    p2_verified = Column(Boolean)

    pokemon3 = Column.with_name('pokemon_3', String)
    p3_verified = Column(Boolean)

    pokemon4 = Column.with_name('pokemon_4', String)
    p4_verified = Column(Boolean)

    pokemon5 = Column.with_name('pokemon_5', String)
    p5_verified = Column(Boolean)

    stardust = Column(Integer)
    xp = Column(Integer)
    candy = Column.with_name('rare_candy', Integer)

    razz_berry = Column(Integer)
    nanab_berry = Column(Integer)
    pinap_berry = Column(Integer)
    silver_pinap = Column(Integer)
    golden_razz = Column(Integer)

    potion = Column(Integer)
    super_potion = Column(Integer)
    hyper_potion = Column(Integer)
    max_potion = Column(Integer)

    revive = Column(Integer)
    max_revive = Column(Integer)

    poke_ball = Column(Integer)
    great_ball = Column(Integer)
    ultra_ball = Column(Integer)

    fast_tm = Column(Integer)
    charge_tm = Column(Integer)

    updated = Column(Timestamp)
