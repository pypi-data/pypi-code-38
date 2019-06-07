# -*- coding: utf-8 -*-
""" Sources for Named Entities Recognition.
"""
from nazca.utils.dataio import sparqlquery, rqlquery


###############################################################################
# NER SOURCE ##################################################################
###############################################################################
class AbstractNerSource(object):
    """ High-level source for Named Entities Recognition
    """

    def __init__(self, endpoint, query, name=None,
                 use_cache=True, preprocessors=None):
        """ Initialise the class.
        """
        self.endpoint = endpoint
        self.query = query
        self.name = name
        self.preprocessors = preprocessors or []
        self.use_cache = use_cache
        self._recognized_cache = {}

    def add_preprocessors(self, preprocessor):
        """ Add a preprocessor
        """
        self.preprocessors.append(preprocessor)

    def recognize_token(self, token):
        """ Recognize a token
        """
        # Applies source specific preprocessors
        for preprocessor in self.preprocessors:
            token = preprocessor(token)
            if not token:
                return []
        if self.use_cache and token.word in self._recognized_cache:
            return self._recognized_cache[token.word]
        uris = self.query_word(token.word) if token.word else []
        if self.use_cache:
            self._recognized_cache[token.word] = uris
        return uris

    def query_word(self, word):
        """ Query a word for a Named Entities Recognition process
        """
        raise NotImplementedError


class NerSourceLexicon(AbstractNerSource):
    """ Source based on a (pre-computed) dictionnary of words (token, uri)
    """

    def __init__(self, lexicon, name=None, use_cache=True, preprocessors=None):
        self.lexicon = lexicon
        self.name = name
        self.preprocessors = preprocessors or []
        self.use_cache = use_cache
        self._recognized_cache = {}

    def query_word(self, word):
        uri = self.lexicon.get(word)
        return [uri, ] if uri else []


class NerSourceLocalRql(AbstractNerSource):
    """ High-level source for Named Entities Recognition
    Local RQL version
    """

    def __init__(self, session, query, name=None,
                 use_cache=True, preprocessors=None):
        """ Initialise the class.
        """
        self.query = query
        self.session = session
        self.name = name
        self.preprocessors = preprocessors or []
        self.use_cache = use_cache
        self._recognized_cache = {}

    def query_word(self, word):
        """ Query a word for a Named Entities Recognition process
        """
        return [r[0]
                for r in self.session.execute(self.query, dict(word=word))]


class NerSourceRql(AbstractNerSource):
    """ High-level source for Named Entities Recognition
    Url version (distant source)
    """

    def query_word(self, word):
        """ Query a word for a Named Entities Recognition process
        """
        if self.endpoint.startswith('http://'):
            # url
            return [r[0]
                    for r in rqlquery(self.endpoint, self.query % {'word': word})]
        else:
            return [r[0]
                    for r in rqlquery(self.endpoint, self.query, word=word)]


class NerSourceSparql(AbstractNerSource):
    """ High-level source for Named Entities Recognition
    SPARQL version

   >>> from ner.core import NerSourceSparql
   >>> ner_source = NerSourceSparql('''SELECT ?uri
                                         WHERE{
                                         ?uri rdfs:label "%(word)s"@en}''',
                                         'http://dbpedia.org/sparql')
   >>> print ner_source.recognize_token('Victor Hugo')
                ... ['http://dbpedia.org/resource/Category:Victor_Hugo',
                     'http://dbpedia.org/resource/Victor_Hugo',
                     'http://dbpedia.org/class/yago/VictorHugo',
                     'http://dbpedia.org/class/yago/VictorHugo(ParisM%C3%A9tro)',
                     'http://sw.opencyc.org/2008/06/10/concept/en/VictorHugo',
                     'http://sw.opencyc.org/2008/06/10/concept/Mx4rve1ZXJwpEbGdrcN5Y29ycA']

    """

    def query_word(self, word):
        """ Query a word for a Named Entities Recognition process
        """
        return [r[0] for r in sparqlquery(
            self.endpoint, self.query % {'word': word})]
