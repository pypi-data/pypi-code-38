import os


# #########
# CONSTANTS
# #########

PATH = os.path.dirname(os.path.abspath(__file__))

# ########################
# BUSINESS LOGIC FUNCTIONS
# ########################


def rarity_filter(rarity: str):
    """
    This is a decorator, which will return a function, that can be used as the callable for the filter() function when
    filtering the available rewards defined in the config. The function will filter True for every reward which was
    defined with the given rarity

    CHANGELOG

    Added 12.06.2019

    :param rarity:
    :return:
    """
    def _func(reward: dict):
        return reward['rarity'] == rarity

    return _func

# ####################
# PROGRAMMING PATTERNS
# ####################


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
