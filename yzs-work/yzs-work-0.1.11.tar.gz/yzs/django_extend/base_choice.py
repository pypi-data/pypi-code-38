from collections import OrderedDict

import six


class ChoiceMeta(type):

    def __new__(metaclass, cls, bases, attrs):
        base_meta = super(ChoiceMeta, metaclass).__new__(metaclass, cls, bases, attrs)

        if attrs:
            _choice_dict = OrderedDict()

            for field, value in attrs.items():
                if isinstance(value, (list, tuple)) and len(value) >= 2:
                    setattr(base_meta, field, value[0])
                    setattr(base_meta, '{}_desc'.format(field), value[1])
                    _choice_dict[value[0]] = value[1]

            setattr(base_meta, 'CHOICES', [(key, value) for key, value in _choice_dict.items()])
            setattr(base_meta, 'CHOICE_DICT', _choice_dict)
        return base_meta


class ChoiceMixin(object):
    @classmethod
    def get_display_value(cls, choice, default=None):
        return cls.CHOICE_DICT.get(choice, default)

    @classmethod
    def choices(cls):
        return getattr(cls, 'CHOICES', [])

    @classmethod
    def choice_dict(cls):
        return getattr(cls, 'CHOICE_DICT', {})


class Choice(six.with_metaclass(ChoiceMeta, ChoiceMixin)):
    pass



