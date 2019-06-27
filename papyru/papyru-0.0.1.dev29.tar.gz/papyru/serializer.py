

class Serializer:
    def __init__(self,
                 representation=None,
                 instance=None):

        has_representation = representation is not None
        has_instance = instance is not None

        if has_representation and has_instance:
            self._instance = self.merge(instance, representation)
            self._representation = None

        elif has_representation:
            def validate_if_has_validator(obj):
                if hasattr(self.__class__, 'validator'):
                    return self.__class__.validator.validate(obj)
                else:
                    return obj

            self._instance = None
            self._representation = validate_if_has_validator(representation)

        elif has_instance:
            self._instance = instance
            self._representation = None

        else:
            raise Exception('Need either instance or representation or both.')

    @property
    def instance(self):
        return (self._instance
                if self._instance is not None
                else self.to_instance(self._representation))

    @property
    def representation(self):
        return (self._representation
                if self._representation is not None
                else self.to_representation(self._instance))

    def to_instance(self, representation):
        raise Exception('implement me')

    def to_representation(self, instance):
        raise Exception('implement me')

    def merge(self, instance, representation):
        raise Exception('implement me')
