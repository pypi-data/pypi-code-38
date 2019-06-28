# -*- coding: utf-8 -*-
"""
Various models mixins adding new features/columns to SQLAlchemy models
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
)
from sqlalchemy.ext.declarative import declared_attr


class TimeStampedMixin(object):
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(),
            info={
                'colanderalchemy': {
                    'exclude': True, 'title': u"Créé(e) le",
                }
            },
            default=datetime.now,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(),
            info={
                'colanderalchemy': {
                    'exclude': True, 'title': u"Mis(e) à jour le",
                }
            },
            default=datetime.now,
            onupdate=datetime.now
        )


class PersistentACLMixin(object):
    """Extend pyramid ACL mechanism to offer row-level ACL

    Subclasses may set the following attributes :

    - ``.__default_acl__`` as an ACL or callable returning an ACL, traditionaly
      set at class level.
    - ``.__acl__`` as an ACL or callable returning an ACL, this can be set on
      class or directly on instance.

    If both are defined, ``__acl__``, the more specific, is prefered.

    Use actual callables, not properties, in subclasses to prevent pyramid from
    silently ignoring any AttributeError your callable should trigger.
    """
    def _get_acl(self):
        # Any AttributeError raised at this function level would be masked.
        # See https://github.com/Pylons/pyramid/pull/2613/files
        if getattr(self, '_acl', None) is None:
            if getattr(self, "__default_acl__", None) is not None:
                return self.__default_acl__
            elif getattr(self, "parent", None) is not None:
                return self.parent.__acl__
            else:
                raise AttributeError('__acl__')
        return self._acl

    def _set_acl(self, value):
        self._acl = value

    def _del_acl(self):
        self._acl = None

    __acl__ = property(_get_acl, _set_acl, _del_acl)


class DuplicableMixin(object):
    """
    Factorize duplication logic on sqlalchemy models

    __duplicable_fields__ attr should contain the list of attributes to be
    copied from a model to its duplicate.
    """
    __duplicable_fields__ = None

    def duplicate(self, factory=None, **kwargs):
        """
        Duplicate all fields listed in __duplicable_fields__ plus optional
        ad-hoc values.

        :param class factory: The new instance class
        :param kwargs: allow to provide ad-hoc values for the attrs of the
          new instance. They will take precedence over copied values.
        :returns: new instance combining fields copied from self, and ad-hoc
          args. The instance is not saved.
        """

        if self.__duplicable_fields__ is None:
            raise NotImplementedError(
               u"DuplicableMixin implementors should define "
               + u"__duplicable_fields__"
            )

        if factory is None:
            factory = self.__class__

        duplicate_obj = factory()
        for i in self.__duplicable_fields__:
            setattr(duplicate_obj, i, getattr(self, i))
        for k, v in kwargs.items():
            setattr(duplicate_obj, k, v)
        return duplicate_obj
