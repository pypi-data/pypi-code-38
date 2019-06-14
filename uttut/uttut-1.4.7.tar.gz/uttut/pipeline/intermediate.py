from typing import Dict


class Intermediate:

    """Collect intermediate products when Pipe run transformation

    attributes:
        collection (list): store input intermediates
        checkpoints (dict): (key, value) = (name, index)

    """

    def __init__(self, checkpoints: Dict[str, int]):
        self._collection: list = []
        self._checkpoints = checkpoints

    def add(self, intermediate):
        """Append intermediate into self._collection

        Arg:
            intermediate: object to be stored in self.collection

        """
        self._collection.append(intermediate)

    def get_from_checkpoint(self, name: str):
        """Retrieve intermediate in collection according to name of checkpoint

        Arg:
            name (str): name of checkpoint

        Raise:
            KeyError if name is not in self._checkpoints
            IndexError if self._checkpoints[name] >= len(self._collection)

        """
        if name not in self._checkpoints:
            raise KeyError(f"{name} is not found.")
        ck_index = self._checkpoints[name]
        return self._collection[ck_index]

    def __getitem__(self, key):
        """Retrieve intermediates by index or slice

        Arg:
            key (int or slice)

        Return:
            intermediates (list)

        Raise:
            IndexError: list index out of range if input index >= len(self.collection)

        """
        return self._collection[key]
