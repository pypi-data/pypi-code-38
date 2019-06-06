# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility

import plone.api
import pycountry


@implementer(IVocabularyFactory)
class CountryVocabulary(object):
    """Vocabulary factory for countries regarding to ISO3166.
    """

    def __call__(self, context, query=None):
        query = safe_unicode(query.lower()) if query else None
        lang = plone.api.portal.get_current_language()
        normalizer = getUtility(IIDNormalizer)  # language aware sort function
        items = [
            (
                it.numeric,
                plone.api.portal.translate(
                    it.name,
                    domain='iso3166',
                    lang=lang
                )
            )
            for it in pycountry.countries
        ]
        items.sort(key=lambda it: normalizer.normalize(it[1], locale=lang))
        items = [
            SimpleTerm(value=it[0], title=it[1])
            for it in items
            if query is None
            or query in it[1].lower()
        ]
        return SimpleVocabulary(items)


CountryVocabularyFactory = CountryVocabulary()


def get_pycountry_name(country_id):
    if not country_id:
        return None
    country = pycountry.countries.get(numeric=country_id)
    return plone.api.portal.translate(
        country.name,
        domain='iso3166',
        lang=plone.api.portal.get_current_language()
    )
