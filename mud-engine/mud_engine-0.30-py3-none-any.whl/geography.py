import logging
from .base import MUDObject
from .base import MUDAction
from .base import MUDActionException
from .base import MUDInterface
from .base import MUDFactory
from .npc import NPC


class GeographyInterface(MUDInterface):

    name = 'geography'

    def load_geography(self):
        return GeographyFactory.load_geography()

class GeographyMeta(type):

    _game_grid = {}
    _geography_types = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        cls._geography_types[name.lower()] = inst
        return inst

def GeographyEvents(MUDDec):
    pass


class Geography(MUDObject, metaclass=GeographyMeta):

    def __init__(self, x, y, z, description, detail, players=None, entrance_descriptions=None):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.description = description
        self.entrance_descriptions = entrance_descriptions or {}
        self.detail = detail
        self.players = players or []
        self.events = {}
        interface = MUDInterface.get_interface("geography")()
        if (self.x, self.y, self.z) in GeographyMeta._game_grid:
            interface.engine.geography.remove(GeographyMeta._game_grid[self.x, self.y, self.z])
        GeographyMeta._game_grid[self.x, self.y, self.z] = self
        interface.engine.geography.append(self)

    def get_direction_coordinates(self, direction):

        if direction == "north":
            return (self.x, self.y + 1, self.z)
        if direction == "south":
            return (self.x, self.y - 1, self.z)
        if direction == "east":
            return (self.x + 1, self.y, self.z)
        if direction == "west":
            return (self.x - 1, self.y, self.z)
        if direction == "up":
            return (self.x, self.y, self.z + 1)
        if direction == "down":
            return (self.x, self.y, self.z - 1)

    def message_players(self, message):
        for player in self.players:
            player.queue_message(message)

    @property
    def north(self):
        return GeographyMeta._game_grid.get((self.x, self.y + 1, self.z), None)

    @property
    def south(self):
        return GeographyMeta._game_grid.get((self.x, self.y - 1, self.z), None)

    @property
    def east(self):
        return GeographyMeta._game_grid.get((self.x + 1, self.y, self.z), None)

    @property
    def west(self):
        return GeographyMeta._game_grid.get((self.x - 1, self.y, self.z), None)

    @property
    def up(self):
        return GeographyMeta._game_grid.get((self.x, self.y, self.z + 1), None)

    @property
    def down(self):
        return GeographyMeta._game_grid.get((self.x, self.y, self.z - 1), None)

    def action_enter(self, player):
        return [lambda: self.render_to_player(player)]

    def action_exit(self, player):
        return []

    def action_exit_north(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} exits to the north")]

    def action_exit_south(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} exits to the south")]

    def action_exit_east(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} exits to the east")]

    def action_exit_west(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} exits to the west")]

    def action_exit_up(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} exits through the ceiling")]

    def action_exit_down(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} exits through the floor")]

    def action_enter_north(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} enters in from the south")]

    def action_enter_south(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} enters in from the north")]

    def action_enter_east(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} enters in from the west")]

    def action_enter_west(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} enters in from the east")]

    def action_enter_up(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} enters in from below")]

    def action_enter_down(self, player):
        return [lambda: player.message_location(other_player_message=f"{player.name} enters in from above")]

    def move_player(self, player, direction):

        # exit -> exit_dir -> enter -> enter_dir

        new_location = getattr(self, direction)
        if not new_location:
            player.queue_message("You can't move in that direction")
            return

        try:
            acts = []
            acts += self.action_exit(player) or []
            acts += getattr(self, "action_exit_" + direction)(player) or []
            player.set_location(new_location)
            acts += new_location.action_enter(player) or []
            acts += getattr(new_location, "action_enter_" + direction)(player) or []
            for act in acts:
                act()
        except MUDActionException:
            pass


    def render_to_player(self, player):

        msg = f"{self.description}\r\n{self.detail}\r\n"

        if self.players:
            msg += "\r\n".join([v.render_display_name() for v in self.players if v != player])

        player.queue_message(msg)


class GeographyFactory(MUDFactory):

    @classmethod
    def create_geography(self, *args, **kwargs):

        type = kwargs.get("type", "geography")
        if 'type' in kwargs:
            del kwargs['type']

        npcs = kwargs.get("npcs", [])
        if 'npcs' in kwargs:
            del kwargs['npcs']


        if type not in GeographyMeta._geography_types:
            logging.warning(f"Couldn't find type {type} in known geography types, missing a subclass of Geography")
            type = "geography"

        geo = GeographyMeta._geography_types[type](*args, **kwargs)

        for npc in npcs:
            npc.spawn_location = geo
            npc.set_location(geo)

        return geo

    @classmethod
    def load_geography(cls):
        # This will eventually pull geography from the persistent storage
        return [
            cls.create_geography(
                0,
                0,
                0,
                "The Void",
                "You stand in a void"
            ),
        ]
