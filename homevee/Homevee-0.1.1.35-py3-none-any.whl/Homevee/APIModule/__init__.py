from abc import abstractmethod


class APIModule:
    def __init__(self):
        return

    @abstractmethod
    def get_function_mappings(self):
        raise NotImplementedError