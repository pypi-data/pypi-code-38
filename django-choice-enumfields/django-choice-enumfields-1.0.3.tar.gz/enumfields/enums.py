from enum import Enum as BaseEnum
from enum import EnumMeta as BaseEnumMeta
from enum import _EnumDict


class Choice:

    def __init__(self, value, label, next=None, initial=True, **kwargs):
        self.value = value
        self.label = label
        self.next = next
        self.initial = initial
        for k, v in kwargs.items():
            setattr(self, k, v)


class ChoiceEnumMeta(BaseEnumMeta):

    def __new__(mcs, name, bases, attrs):
        member_names = attrs._member_names
        choices = {
            name: attrs[name] if isinstance(attrs[name], Choice)
            else Choice(attrs[name], name.replace('_', ' ').title())
            for name in member_names
        }
        attrs._member_names = []
        for member_name in member_names:
            attrs.pop(member_name)
            attrs[member_name] = choices[member_name].value
        attrs._member_names = member_names

        obj = BaseEnumMeta.__new__(mcs, name, bases, attrs)
        for name, choice in choices.items():
            m = obj[name]
            for k, v in choice.__dict__.items():
                if k != 'value':
                    setattr(m, k, v)

        return obj


class ChoiceEnum(ChoiceEnumMeta('ChoiceEnum', (BaseEnum,), _EnumDict())):

    @classmethod
    def choices(cls):
        """
        Returns a list formatted for use as field choices.
        (See https://docs.djangoproject.com/en/dev/ref/models/fields/#choices)
        """
        return tuple((m.value, m.label) for m in cls)

    def __str__(self):
        """
        Show our label when Django uses the Enum for displaying in a view
        """
        return str(self.label)


class NumChoiceEnum(int, ChoiceEnum):

    def __str__(self):  # See Enum.__str__
        return str(self.label)
