

class SpritePixmap:
    def __init__(self, qpixmap, id):
        self.qpixmap = qpixmap
        self.id = id

    @property
    def size(self):
        """
        Return the QSize object of the QPixmap
        """
        return self.qpixmap.size()

    @property
    def width(self):
        """
        Return the width of the QPixmap
        """
        return self.qpixmap.width()

    @property
    def height(self):
        """
        Return the height of the QPixmap
        """
        return self.qpixmap.height()

    def __eq__(self, other):
        return self.height == other.height

    def __ne__(self, other):
        return self.height != other.height

    def __lt__(self, other):
        return self.height < other.height

    def __le__(self, other):
        return self.height <= other.height

    def __gt__(self, other):
        return self.height > other.height

    def __ge__(self, other):
        return self.height >= other.height
