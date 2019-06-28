def attrs(cls):

    def prop_get(prop):

        def prop_get_eval(self):
            return getattr(self, '_{}'.format(prop))

        #return lambda self: getattr(self, '_{}'.format(prop))
        return prop_get_eval

    def wrap(cls):
        [setattr(cls, prop, property(prop_get(prop))) for prop in cls._defaults]
        cls.__slots__ = tuple(['_{}'.format(_p) for _p in cls._defaults])
        return cls

    return wrap(cls)


@attrs
class BaseObj:
    """
    Base object, with:

    * __slots__ to avoid typos
    * A general constructor
    * A general string representation
    * A default equality testing that compares attributes.
    """
    __slots__ = ()
    _defaults = {}
    _force_def = {}
    _ignore_nondef = ()

    def __init__(self, *args, **kwargs):
        """
        Attribute values can be given positionally or as keyword.
        If an attribute is not given it will take its value from the
        'defaults' class member. If an attribute is given both positionally
        and as keyword, the keyword wins.
        """
        _defaults = self.__class__._defaults
        _d = {
            **_defaults,
            **(dict(zip(_defaults, args))),
            **kwargs,
            **self.__class__._force_def
        }
        for p, v in _d.items():
            setattr(self, '_{}'.format(p), v)

    def keys(self):
        return (prop[1:] for prop in self.__slots__)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default):
        return getattr(self, key) if hasattr(self, key) else default

    def __repr__(self):
        cls_name = self.__class__.__name__
        contain_str = ', '.join(
            '{}={!r}'.format(p, v) for p, v in self.non_defaults().items())
        return '{}({})'.format(cls_name, contain_str)

    __str__ = __repr__

    def diff(self, other):
        """
        Return differences between self and other as dictionary of 2-tuples.
        """
        if isinstance(other, self.__class__):
            diff = {}
            for k in self.__class__._defaults:
                left = getattr(self, k)
                right = getattr(other, k)
                if left != right:
                    diff[k] = (left, right)
        else:
            raise Exception("diff object not {}".format(
                self.__class__.__name__))
        return diff

    def non_defaults(self):
        """
        Get a dictionary of all attributes that differ from the default.
        """
        non_defaults = {}
        for p, default in {
                **self.__class__._defaults,
                **self.__class__._force_def
        }.items():
            if p not in self.__class__._ignore_nondef:
                cur_value = getattr(self, p)
                if cur_value != default:  # and (cur_value==cur_value or default == default):
                    non_defaults[p] = cur_value
        return non_defaults

    def __nonzero__(self):
        """ 
        """
        return True if self.non_defaults() else False

    def __bool__(self):
        return True if self.non_defaults() else False

    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and {**other} == {**self} 


class MetaProps(type):
    def __repr__(cls):
        attrs = [attr for attr in cls.__dict__ if not attr.startswith('_')]
        display_name = cls.__name__ if not cls.__name__.startswith('_') else ""
        return '{}({})'.format(display_name, (', ').join(attrs))

class BaseProps(metaclass=MetaProps):
    pass