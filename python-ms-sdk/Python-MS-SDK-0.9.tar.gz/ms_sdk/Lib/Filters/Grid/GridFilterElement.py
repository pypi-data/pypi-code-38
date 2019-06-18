

class GridFilterElement:

    values = None
    name = None

    def __init__(self, values):
        """
        GridFilterElement constructor.
        :param list|dict values:
        """
        self.values = values

    def getValues(self):
        return self.values

    def getName(self):
        return self.name
