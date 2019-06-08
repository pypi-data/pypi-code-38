import logging
from .base import MUDObject
from .base import MUDInterface

class AreaInterface(MUDInterface):
    name = 'area'

class Area(MUDObject):

    interface = AreaInterface

    def __init__(self, location, description, detail):
        self.location = location
        self.description = description
        self.detail = detail
        self.players = []
        self.npcs = []
