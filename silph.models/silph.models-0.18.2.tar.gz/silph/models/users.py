
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


class Avatar(WebTable, table_name='avatars'):
    id = Column(Serial, primary_key=True, unique=True)

    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class Badge(WebTable, table_name='badges'):
    id = Column(Serial, primary_key=True, unique=True)
    slug = Column(Text)

    name = Column(Text)
    description = Column(Text)
    image = Column(Text)

    public = Column(Boolean)
    show_count = Column(Boolean)

    rule = Column(Text)
    criteria = Column(Integer)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)



class User(WebTable, table_name='users'):
    id = Column(Serial, primary_key=True, unique=True)

    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    silph_username = Column.with_name('username', String)
    reddit_username = Column(String)
    game_username = Column.with_name('in_game_username', String)

    ban_level = Column(Integer)

    role = Column(Integer)
    is_in_field_test = Column(Integer)

    created = Column(Timestamp)

    @property
    def name(self):
        return self.game_username or 'Traveler #%x' % self.id

    @property
    def active(self):
        return self.ban_level < 1

    def payload(self):
        struct = {
            'id': self.id,
            'name': self.username,
            'role': self.role,
            'created': int(self.created.timestamp()),
            'version': 0,
        }

        return struct


class ApiUser(WebTable, table_name='api_users'):
    id = Column(String, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, primary_key=True)
    active = Column(Boolean)

    created = Column(Timestamp)
    updated = Column(Timestamp)

    @property
    def token(self):
        return self.id


class UserLogin(WebTable, table_name='user_logins'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, nullable=False)
    vendor = Column.with_name('vendor_id', Integer, nullable=False)

    username = Column(Text)
    identifier = Column(String)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class UnlockedAvatar(WebTable, table_name='unlocked_user_avatars'):
    user = Column.with_name('user_id', Integer, primary_key=True)
    avatar = Column.with_name('avatar_id', Integer, primary_key=True)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class UserBadge(WebTable, table_name='user_badges'):
    user = Column.with_name('user_id', Integer, primary_key=True)
    badge = Column.with_name('badge_id', Integer, primary_key=True)

    variant = Column(String, default='0')
    count = Column(Integer, default=0)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class TravelersCard(WebTable, table_name='travelers_cards'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, nullable=False)
    trainer_type = Column.with_name('trainer_type_id', Integer)

    avatar = Column.with_name('avatar_id', Integer)
    gender = Column(Integer)
    skintone = Column(Integer)

    @property
    def gender_code(self):
        return 'm' if self.gender == 0 else 'f'

    team = Column(SmallInt)
    xp = Column(Integer)
    top_pokemon = Column.with_name('top_6_pokemon', Text)

    home_region = Column(Text)
    pokedex = Column.with_name('pokedex_count', SmallInt)
    raid_average = Column(SmallInt)
    playstyle = Column(SmallInt)
    goal = Column.with_name('current_goal', SmallInt)

    public = Column.with_name('is_public', Boolean)
    badge_sort = Column(SmallInt)

    show_trainer_name = Column(Boolean)
    show_discords = Column(Boolean)
    show_reddit = Column(Boolean)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)

