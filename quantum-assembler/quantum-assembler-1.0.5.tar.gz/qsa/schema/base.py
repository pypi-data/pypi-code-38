import marshmallow

from qsa.lib.datastructures import DTO


class Schema(marshmallow.Schema):
    """A :class:`marshmallow.Schema` implementation that returns
    a :class:`sg.lib.datastructures.DTO` instance on its :meth:`load()`
    method, instead of a dictionary.
    """

    @classmethod
    def defaults(cls, defaults=None):
        return cls().dump(defaults or {})

    @classmethod
    def getfordump(cls, *args, **kwargs):
        kwargs['unknown'] = marshmallow.EXCLUDE
        return cls(*args, **kwargs)

    @classmethod
    def getforload(cls, *args, **kwargs):
        kwargs['unknown'] = marshmallow.EXCLUDE
        return cls(*args, **kwargs)

    def dump(self, *args, **kwargs):
        result = super().dump(*args, **kwargs)
        return DTO.fromdict(result) if not self.many\
            else [DTO.fromdict(x) for x in result]

    def load(self, *args, **kwargs):
        kwargs['unknown'] = marshmallow.EXCLUDE
        result = super(Schema, self).load(*args, **kwargs)
        return DTO.fromdict(result) if not self.many\
            else [DTO.fromdict(x) for x in result]
