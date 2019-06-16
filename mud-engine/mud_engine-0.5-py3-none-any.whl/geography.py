import logging
from .base import MUDObject
from .base import MUDAction
from .base import MUDInterface

GAME_GRID = {}

class GeographyInterface(MUDInterface):

    name = 'geography'

    def load_geography(self):
        return GeographyFactory.load_geography()

class GeographyAction(MUDAction):
    pass

class Geography(MUDObject):

    def __init__(self, x, y, z, description, detail):
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

    @property
    def east(self):
        return GAME_GRID.get((self.x + 1, self.y, self.z), None)

    @property
    def west(self):
        return GAME_GRID.get((self.x - 1, self.y, self.z), None)

    @property
    def north(self):
        return GAME_GRID.get((self.x, self.y + 1, self.z), None)

    @property
    def south(self):
        return GAME_GRID.get((self.x, self.y - 1, self.z), None)

    @property
    def up(self):
        return GAME_GRID.get((self.x, self.y, self.z + 1), None)

    @property
    def down(self):
        return GAME_GRID.get((self.x, self.y, self.z - 1), None)

    @GeographyAction
    def enter(self, player):
        self.render_to_player(player)

    @GeographyAction
    def exit(self, player):
        pass

    @GeographyAction
    def enter_north(self, player):
        for other_player in self.players:
            if other_player != player:
                other_player.queue_message("\r\n{} enters in from the south\r\n".format(player.name))

    @GeographyAction
    def enter_south(self, player):
        for other_player in self.players:
            if other_player != player:
                other_player.queue_message("\r\n{} enters in from the north\r\n".format(player.name))

    @GeographyAction
    def enter_east(self, player):
        for other_player in self.players:
            if other_player != player:
                other_player.queue_message("\r\n{} enters in from the west\r\n".format(player.name))

    @GeographyAction
    def enter_down(self, player):
        for other_player in self.players:
            if other_player != player:
                other_player.queue_message("\r\n{} enters in from the east\r\n".format(player.name))

    @GeographyAction
    def enter_up(self, player):
        for other_player in self.players:
            if other_player != player:
                other_player.queue_message("\r\n{} enters in from below\r\n".format(player.name))

    @GeographyAction
    def enter_down(self, player):
        for other_player in self.players:
            if other_player != player:
                other_player.queue_message("\r\n{} enters in from above\r\n".format(player.name))

    def move_player(self, player, direction):

        new_location = getattr(self, direction)
        if not new_location:
            player.queue_message("You can't move in that direction\r\n")
            return

        self.act_exit(player)
        getattr(self, "act_exit_" + direction)(player)
        player.set_location(new_location)
        new_location.enter(player)
        getattr(new_location, "act_enter_" + direction)(player)

    def render_to_player(self, player):
        msg = "{}\r\n{}\r\n".format(self.description, self.detail)
        player.queue_message(msg)


class GeographyFactory(MUDObject):

    @classmethod
    def load_geography(cls):
        # This will eventually pull geography from the persistent storage
        return [
            Geography(
                0,
                0,
                0,
                "The Void",
                "You stand in a void"
            ),
            Geography(
                0,
                1,
                0,
                "north of the void",
                "You stand north of the void"
            )
        ]

