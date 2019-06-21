import logging
from .base import MUDObject
from .base import MUDAction
from .base import MUDActionException
from .base import MUDInterface
from .base import MUDFactory

GAME_GRID = {}

class GeographyInterface(MUDInterface):

    name = 'geography'

    def load_geography(self):
        return GeographyFactory.load_geography()

class GeographyAction(MUDAction):
    pass

class GeographyActionException(MUDActionException):
    pass

class GeographyMeta(type):

    _GEOGRAPHY_TYPES = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        cls._GEOGRAPHY_TYPES[name.lower()] = inst
        return inst

class Geography(MUDObject, metaclass=GeographyMeta):

    def __init__(self, x, y, z, description, detail):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.description = description
        self.detail = detail
        self.players = []
        self.npcs = []
        self.events = {}
        interface = MUDInterface.get_interface("geography")()
        global GAME_GRID
        GAME_GRID[self.x, self.y, self.z] = self
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
        return GAME_GRID.get((self.x, self.y + 1, self.z), None)

    @property
    def south(self):
        return GAME_GRID.get((self.x, self.y - 1, self.z), None)

    @property
    def east(self):
        return GAME_GRID.get((self.x + 1, self.y, self.z), None)

    @property
    def west(self):
        return GAME_GRID.get((self.x - 1, self.y, self.z), None)

    @property
    def up(self):
        return GAME_GRID.get((self.x, self.y, self.z + 1), None)

    @property
    def down(self):
        return GAME_GRID.get((self.x, self.y, self.z - 1), None)

    #@GeographyAction
    def action_enter(self, player):
        return [lambda: self.render_to_player(player)]

    #@GeographyAction
    def action_exit(self, player):
        return []

    #@GeographyAction
    def action_exit_north(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} exits to the north\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_exit_south(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} exits to the south\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_exit_east(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} exits to the east\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_exit_west(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} exits to the west\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_exit_up(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} exits through the floor\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_exit_down(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} exits through the ceiling\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_enter_north(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} enters in from the south\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_enter_south(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} enters in from the north\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_enter_east(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: acts.append(lambda: other_player.queue_message("\r\n{} enters in from the west\r\n".format(player.name))))
        return acts

    #@GeographyAction
    def action_enter_west(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} enters in from the east\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_enter_up(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} enters in from below\r\n".format(player.name)))
        return acts

    #@GeographyAction
    def action_enter_down(self, player):
        acts = []
        for other_player in self.players:
            if other_player != player:
                acts.append(lambda: other_player.queue_message("\r\n{} enters in from above\r\n".format(player.name)))
        return acts

    def move_player(self, player, direction):

        # exit -> exit_dir -> enter -> enter_dir

        new_location = getattr(self, direction)
        if not new_location:
            player.queue_message("You can't move in that direction\r\n")
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
        msg = "{}\r\n{}\r\n".format(self.description, self.detail)
        player.queue_message(msg)


class GeographyFactory(MUDFactory):

    @classmethod
    def create_geography(self, *args, **kwargs):

        type = kwargs.get("type", "geography")
        if 'type' in kwargs:
            del kwargs['type']

        if type not in GeographyMeta._GEOGRAPHY_TYPES:
            logging.warning(f"Couldn't find type {type} in known geography types, missing a subclass of Geography")
            type = "geography"

        return GeographyMeta._GEOGRAPHY_TYPES[type](*args, **kwargs)

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
