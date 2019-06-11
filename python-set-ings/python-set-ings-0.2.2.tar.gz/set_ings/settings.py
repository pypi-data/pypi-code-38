import os
from .exceptions import SettingsError


def isTrue(value):
    """
    Helper to check for string representation of a boolean True.
    """
    return value.lower() in ('true', 'yes', '1')


class Property:
    """
    Settings property. Use on your Settings class.
    """

    def __init__(self, default=None, cast=str, isList=False):
        self.default = default
        self.cast = cast
        self.isList = isList

    def fromRaw(self, raw, key):
        if raw is None:
            if self.default is None:
                raise SettingsError(
                    f'Could not find "{key}" in environment, but no default \
provided.'
                )

            return self.default(key)\
                if callable(self.default)\
                else self.default

        if self.isList:
            return [self.castValue(x, key) for x in raw.split(',')]
        else:
            return self.castValue(raw, key)

    def castValue(self, value, key):
        try:
            if self.cast is bool:
                return isTrue(value)
            else:
                return self.cast(value)
        except ValueError as e:
            raise SettingsError(f'Unable to cast "{key}"') from e


class Settings:
    """
    Baseclass for your application settings.
    """

    def __init__(self):
        self.load()

    def load(self):
        for prop in dir(self):
            if type(getattr(self, prop)) is Property:
                envKey = f'{self._PREFIX}_{prop}'
                setattr(
                    self,
                    prop,
                    getattr(self, prop).fromRaw(os.environ.get(envKey), prop)
                )
