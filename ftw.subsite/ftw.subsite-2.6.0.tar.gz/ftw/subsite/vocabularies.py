from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary
from ftw.subsite import _


class AvailableLanguagesVocabulary(object):
    """ Vocabulary base on plone.app.vocabularies.AvailableContentLanguages
    but also adds an empty term
    """

    def __call__(self, context):
        factory = getUtility(
            IVocabularyFactory,
            name='plone.app.vocabularies.AvailableContentLanguages',
            context=context)
        vocab = factory(context)
        terms = vocab._terms
        terms.append(vocab.createTerm("", "default", _(u"inherit_language", default=u"inherit language")))
        return SimpleVocabulary(terms)


AvailableLanguagesVocabularyFactory = AvailableLanguagesVocabulary()
