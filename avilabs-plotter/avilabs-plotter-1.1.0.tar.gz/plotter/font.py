from .color import Color

class Font:
    def __init__(self, color=None, size=10):
        self.color = color if color is not None else Color(red=0, green=0, blue=0)
        self.size = size

    def __eq__(self, other):
        return self.color == other.color and self.size == other.size
