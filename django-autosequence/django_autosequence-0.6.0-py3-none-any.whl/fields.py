# coding: utf-8
from typing import Union

from django.db.models import Max
from django.db.models.fields import IntegerField

__all__ = ['AutoSequenceField']


class AutoSequenceField(IntegerField):
    """
    AutoSequenceField is an AutoField that is available for non primary keys and can be
    configured
    with unique_with to have separate sequences based on other model fields.

    It is non editable and unique

    :param start_at: integer: the starting number of the sequence, defaults to 1
    :param unique_with: string or tuple of strings: name or names of attributes
        that this sequence will be unique with

    """

    def __init__(self, start_at: int = 1, unique_with: Union[str, tuple] = None,
                 unique: bool = True, **kwargs):
        # unique by default
        kwargs['editable'] = False

        # ...unless we are using unique_with
        if unique_with:
            unique = False

        # unique_with value can be string or tuple
        self.unique_with = unique_with or ()
        if isinstance(self.unique_with, str):
            self.unique_with = (self.unique_with,)

        self.start_at = start_at
        super().__init__(unique=unique, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['editable']

        if self.start_at != 1:
            kwargs['start_at'] = self.start_at

        if self.unique_with:
            kwargs['unique_with'] = self.unique_with
        else:
            kwargs['unique'] = self._unique
        return name, path, args, kwargs

    def pre_save(self, instance, add):
        if not add:
            return getattr(instance, self.attname)

        qs = self.model.objects.all()

        if self.unique_with:
            qs = qs.filter(
                **{field: getattr(instance, field) for field in self.unique_with}
            )
        sequence = qs.aggregate(max=Max(self.attname))['max']
        if sequence:
            sequence += 1
        else:
            sequence = self.start_at
        setattr(instance, self.attname, sequence)

        return sequence
