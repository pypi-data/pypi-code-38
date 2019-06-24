# -*- coding: utf-8 -*-

from Products.CMFPlone import PloneMessageFactory as PMF
from plone.registry.interfaces import IRegistry
from plone import api
from operator import itemgetter
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from ideabox.policy import _


def dict_list_2_vocabulary(dict_list):
    """dict_list_2_vocabulary
    Converts a dictionary list to a SimpleVocabulary

    :param dict_list: dictionary list
    """
    terms = []
    for item in dict_list:
        for key in sorted([k for k in item]):
            terms.append(SimpleVocabulary.createTerm(key, str(key), item[key]))
    return SimpleVocabulary(terms)


class ReviewStateVocabularyFactory(object):
    def __call__(self, context):
        values = [
            {"draft": PMF("draft")},
            {"deposited": PMF("deposited")},
            {"project_analysis": PMF("project_analysis")},
            {"vote": PMF("vote")},
            {"result_analysis": PMF("result_analysis")},
            {"selected": PMF("selected")},
            {"rejected": PMF("rejected")},
            {"study_in_progress": PMF("study_in_progress")},
            {"in_progress": PMF("in_progress")},
            {"realized": PMF("realized")},
        ]
        return dict_list_2_vocabulary(values)


ReviewStateVocabulary = ReviewStateVocabularyFactory()


class GenderVocabularyFactory(object):
    def __call__(self, context):
        values = [{"MALE": _("MALE", u"Male")}, {"FEMALE": _("FEMALE", u"Female")}]
        return dict_list_2_vocabulary(values)


GenderVocabulary = GenderVocabularyFactory()


class ZipCodeVocabularyFactory(object):
    def __call__(self, context):
        registry = getUtility(IRegistry)
        dict_value = registry.get("ideabox.vocabulary.zip_code")
        values = []
        for key in dict_value:
            val = {key: dict_value[key]}
            values.append(val)
        return dict_list_2_vocabulary(values)


ZipCodeVocabulary = ZipCodeVocabularyFactory()


def make_terms(items):
    """Create zope.schema terms for vocab from tuples"""
    terms = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items]
    return terms


class ProjectsVocabularyFactory(object):
    def __call__(self, context):
        brains = api.content.find(portal_type="Project", review_state="vote")
        results = [(b.UID, b.Title) for b in brains]
        results = sorted(results, key=itemgetter(1))
        terms = make_terms(results)
        return SimpleVocabulary(terms)


ProjectsVocabulary = ProjectsVocabularyFactory()


class VoteVocabularyFactory(object):
    def __call__(self, context):
        values = [{"FOR": _("FOR", u"For")}, {"AGAINST": _("AGAINST", u"Against")}]
        return dict_list_2_vocabulary(values)


VoteVocabulary = VoteVocabularyFactory()
