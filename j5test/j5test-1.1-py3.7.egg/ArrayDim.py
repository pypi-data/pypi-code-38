from j5test.IterativeTester import Dimension

class ArrayDim(Dimension):
    """This is a very simple Dimension which just gives the members of an array"""
    def __init__(self, initarray):
        self._resources = {}
        self._failed_conditions = {}
        for num, member in enumerate(initarray):
            self._resources[str(num)] = member

