
class Singleton(object):
    """
    Implements the singleton pattern.

    Example:

        Create a singleton class::

            class MySingleton(Singleton):
                def __init__(self):
                    super().__init__()
                    self.value = 0

                def add(self):
                    self.value += 1


        Use the singleton::

            MySingleton.get_instance().add()
            MySingleton.get_instance().add()
            print(MySingleton.get_instance().value)
    """
    _instance = None

    def __init__(self):
        """
        Ensures there is only one instance created. Make sure to
        use super() in subclasses.
        """
        if self._instance:
            raise ValueError('{}.{} is a singleton and can only have a single instance.'.format(
                self.__class__.__module__,
                self.__class__.__name__))

    @classmethod
    def get_instance(cls):
        """
        Get an instance of the singleton.
        """
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
