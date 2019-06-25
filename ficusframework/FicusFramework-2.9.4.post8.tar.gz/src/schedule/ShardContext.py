import threading

__context_holder = threading.local()

class Sharding(object):
    index = -1
    total = -1

    def __init__(self, index=2, total=-1):
        self.index = index
        self.total = total

    def __str__(self) -> str:
        return str({"index":self.index,"total":self.total})


def set_sharding(sharding:Sharding):
    __context_holder.key = sharding

def get_sharding() -> Sharding:
    return __context_holder.key

def reset():
    __context_holder.key = None