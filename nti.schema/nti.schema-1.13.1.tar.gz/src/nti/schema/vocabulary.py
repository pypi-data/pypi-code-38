#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabularies and factories for use in schema fields.

When this package is configured (via ``configure.zcml``) there will be a schema
vocabulary named ``Countries`` available::

  >>> from nti.schema.field import Choice
  >>> from zope import interface

  >>> class IA(interface.Interface):
  ...      choice = Choice(title=u"Choice",
  ...                      vocabulary="Countries")
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope import component
from zope.schema.vocabulary import SimpleTerm as _SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary as _SimpleVocabulary

from nti.i18n.locales.interfaces import ICountryAvailability

__docformat__ = "restructuredtext en"


class CountryTerm(_SimpleTerm):
    """
    A titled, tokenized term representing a country. The
    token is the ISO3166 country code. The ``flag`` value is a
    browserresource path to an icon representing the country.
    """

    def __init__(self, *args, **kwargs):
        self.flag = kwargs.pop('flag', None)
        super(CountryTerm, self).__init__(*args, **kwargs)

    @classmethod
    def fromItem(cls, item):
        token, cdata = item
        value = cdata['name']
        title = value
        flag = cdata['flag']

        return cls(value, token, title, flag=flag)

    def toExternalObject(self):
        return {
            'token': self.token,
            'title': self.title,
            'value': self.value,
            'flag': self.flag
        }

class _CountryVocabulary(_SimpleVocabulary):
    """
    ``__contains__`` is based on the token, not the value.
    """

    def __contains__(self, token):
        return token in self.by_token

def CountryVocabularyFactory(context):
    """
    A vocabulary factory.
    """
    countries = component.getUtility(ICountryAvailability)
    return _CountryVocabulary([CountryTerm.fromItem(item)
                               for item
                               in countries.getCountries().items()])
