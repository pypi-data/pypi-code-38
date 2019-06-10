
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    String,
    Text,
    Timestamp,
    Serial,
    Real,
    Boolean,
    Numeric,
)

from .base import WebTable


class Pokemon(WebTable, table_name='pokemons'):
    id = Column(Serial, primary_key=True, unique=True)

    name = Column.with_name('identifier', String, nullable=False)
    species = Column.with_name('species_id', Integer, nullable=False)

    height = Column(SmallInt, nullable=False)
    weight = Column(SmallInt, nullable=False)

    base_xp = Column.with_name('base_experience', SmallInt, nullable=False)

    order = Column(SmallInt, nullable=False)

    primary_type = Column.with_name('type_1_id', SmallInt, nullable=False)
    secondary_type = Column.with_name('type_2_id', SmallInt, nullable=False)

    primary_type_text = Column.with_name('type_1', SmallInt, nullable=False)
    secondary_type_text = Column.with_name('type_2', SmallInt, nullable=False)

    base_stamina = Column(Integer)
    description = Column(Text)

    updated = Column(Timestamp)


class Pkmn(WebTable, table_name='pkmns'):
    slug = Column.with_name('species_form_slug', String, primary_key=True, unique=True)

    available = Column.with_name('is_available', Boolean)
    released = Column.with_name('is_released', Boolean)

    shiny_available = Column(Boolean)
    shiny_released = Column(Boolean)

    pokedex_id = Column.with_name('national_pokedex_id', Integer)

    species_slug = Column(String)
    species_name = Column(String)

    form = Column.with_name('form_name', String)

    is_default_form = Column.with_name('default_display_form', Boolean)

    generation = Column.with_name('gen', Integer)

    primary_type = Column.with_name('type1', Integer, nullable=False)
    secondary_type = Column.with_name('type2', Integer, nullable=False)

    raid_tier = Column.with_name('raid_boss_tier', Integer)
    raid_verified = Column.with_name('is_raid_boss_tier_verified', Boolean)

    raid_shiny = Column.with_name('raid_boss_shiny_available', Boolean)

    legendary = Column.with_name('is_legendary', Boolean)
    mythical = Column.with_name('is_mythical', Boolean)
    regional = Column.with_name('is_regional', Boolean)

    nesting = Column.with_name('is_nesting', Boolean)

    description = Column(Text)

    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    stat_total = Column(Integer)

    weight = Column(Real)
    height = Column(Real)

    updated = Column(Timestamp)

    @property
    def type(self):
        if self.legendary:
            return 'Legendary'
        if self.mythical:
            return 'Mythical'
        if self.regional:
            return 'Regional'

        return 'Non-Legendary'


class PokemonType(WebTable, table_name='types'):
    id = Column(Serial, primary_key=True, unique=True)

    title = Column(String, nullable=False)

    bg_primary_color = Column.with_name('background_hex', String)
    bg_secondary_color = Column.with_name('background_hex_2', String)
    font_color = Column.with_name('font_hex', String)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)
