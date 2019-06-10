import copy


class DTO(dict):
    __immutable__ = False

    @classmethod
    def fromdict(cls, mapping, with_dto=False):
        """Create a new Data Transfer Object (DTO) from a regular
        Python dictionary.
        """
        return cls(mapping).as_dto(with_dto=with_dto)

    def as_dict(self):
        """Convert the DTO  to a dictionary. For use in environments
        where the DTO can not be serialized and no hooks are available
        to implement it.
        """
        dto = copy.deepcopy(self)
        for k in dto.keys():
            v = dto[k]
            if not isinstance(v, (DTO, ImmutableDTO)):
                continue
            dto[k] = v.as_dict()
        return dict(dto)

    def as_dto(self, with_dto=False):
        """Convert all dictionaries in the DTO to DTO
        instances.
        """
        dto = copy.deepcopy(self)
        dto_cls = type(self)
        for k in dto.keys():
            v = dto[k]
            if with_dto and hasattr(v, 'as_dto'):
                dto[k] = v.as_dto(with_dto)
                continue

            if isinstance(v, dict):
                dto[k] = dto_cls(**v).as_dto(with_dto=with_dto)
                continue

            if isinstance(v, (list, set, tuple)):
                cls = type(v)
                dto[k] = cls([dto_cls.fromdict(x) if isinstance(x, dict) else x
                    for x in v])

        return dto

    def __serialize__(self, func):
        return func(dict(self))

    def __getattr__(self, attname):
        if attname not in self:
            raise AttributeError(attname)
        return self[attname]

    def __setattr__(self, attname, value):
        if self.__immutable__:
            raise TypeError(attname)
        self[attname] = value

    def __repr__(self):
        super_repr = dict.__repr__(self)
        return "<%s: %s>" % (type(self).__name__, super_repr)

    def __sub__(self, keys):
        if not isinstance(keys, list):
            raise TypeError("Can only create new DTO with list.")
        return type(self)({x: self[x] for x in self.keys() if x not in keys})

    def __or__(self, dto):
        if not isinstance(dto, dict):
            raise ValueError("Cannot union dict with non-dict type.")
        keys = self.__getkeys(dto)
        new = type(self)(self)
        new.update(dto)
        return new

    def __and__(self, dto):
        """Return the intersection of `self` and `dto` by their keys."""
        keys = self.__getkeys(dto)
        if isinstance(dto, dict):
            params = {x: dto[x] for x in keys if x in self}
        else:
            params = {x: self[x] for x in keys if x in self}
        return type(self)(params)

    def __getkeys(self, dto):
        return set(dto) if not isinstance(dto, dict)\
            else set(dto.keys())


class ImmutableDTO(DTO):
    __immutable__ = True
