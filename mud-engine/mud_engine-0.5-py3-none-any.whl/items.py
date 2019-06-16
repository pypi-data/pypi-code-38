from .base import MUDObject
from .base import MUDInterface

valid_slots = [
    'head', 'neck', 'chest', 'shoulder', 'hand', 'arms', 'hands',
    'waist', 'legs', 'feet', 'finger', 'back'
]

class ItemInterface(MUDInterface):

    name = 'item'

class ItemCatalogue(MUDObject):
    pass

class Item(MUDObject):

    def __init__(self, name, short_description, description, slot=None):
        self.slot = slot
        self.name = name
        self.short_description = short_description
        self.description = description
        self.interface = MUDInterface.get_interface("item")()

