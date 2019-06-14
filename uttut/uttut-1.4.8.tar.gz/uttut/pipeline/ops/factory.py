class OperatorFactory:

    def __init__(self):
        self._factory = {}

    def register(self, name: str, op_class):
        """register an operator

        Args:
            name (str): user defined name of operator
            op_class (Operator): an Operator class

        Raise:
            KeyError if name is existed.
        """

        if name not in self._factory:
            self._factory[name] = op_class
        else:
            raise KeyError(f"{name} already exists.")

    def __getitem__(self, op_name):
        if op_name not in self._factory:
            raise KeyError(f"{op_name} is not registered")
        return self._factory[op_name]

    def __eq__(self, other):
        if not isinstance(other, OperatorFactory):
            return False
        return self._factory == other._factory
