def typed_property(name, expected_type):
    '''
    Class property with a static type
    '''
    storage_name = '_' + name

    @property
    def prop(self):
        return getattr(self, storage_name)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError(f'{name} must be a {expected_type}')
        setattr(self, storage_name, value)
    return prop

def default_property(name):
    '''
    Simplified default class property
    '''
    storage_name = '_' + name

    @property
    def prop(self):
        return getattr(self, storage_name)

    @prop.setter
    def prop(self, value):
        setattr(self, storage_name, value)
    return prop


class DefaultRepresentationMixin:
    '''
    Mixin that provides object representation for humans
    '''
    def __str__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def __repr__(self):
        return self.__str__()
