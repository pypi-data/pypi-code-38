from strongr.core.exception import InvalidParameterException

from strongr.secretsdomain.command import AddSecret, RemoveSecret

class CommandFactory:
    def new_add_secret(self, key, value):
        if len(key) == 0:
            raise InvalidParameterException('key len must be > 0')
        elif not isinstance(key, basestring):
            raise InvalidParameterException('key must be string type')

        if len(value) == 0:
            raise InvalidParameterException('value len must be > 0')
        elif not isinstance(value, basestring):
            raise InvalidParameterException('value must be string type')

        return AddSecret(key, value)

    def new_remove_secret(self, key):
        if len(key) == 0:
            raise InvalidParameterException('key len must be > 0')

        return RemoveSecret(key)
