from .player import Player
from .player import PlayerInterface
from .player import PlayerState
from .base import MUDObject

class NPC(Player):

    spawn_location = None

    def __init__(self, *args, **kwargs):
        from .engine import MUDEngine
        spawn_location = kwargs.get('spawn_location')
        if 'spawn_location' in kwargs:
            del kwargs['spawn_location']
        super().__init__(*args, **kwargs)
        self.spawn_location = spawn_location
        MUDEngine.add_player(self)

    def queue_message(self, *args, **kwargs):
        pass
