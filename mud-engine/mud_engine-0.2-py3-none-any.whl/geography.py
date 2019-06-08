import logging
from .base import MUDObject
from .base import MUDInterface

GAME_GRID = {}

class GeographyInterface(MUDInterface):

    name = 'geography'

    def load_geography(self):
        return GeographyFactory.load_geograhpy()

class Geography(MUDObject):

    def __init__(self, x, y, z, description, detail):
        self.x = x
        self.y = y
        self.z = z
        self.description = description
        self.detail = detail
        self.players = []
        self.npcs = []
        interface = GeographyInterface()
        global GAME_GRID
        GAME_GRID[self.x, self.y, self.z] = self

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

    def render_to_player(self, player):
        msg = "{}\r\n{}\r\n".format(self.description, self.detail)
        player.queue_message(msg)


class GeographyFactory(MUDObject):

    @classmethod
    def load_geograhpy(cls):
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

