# -*- coding: utf-8 -*-
""" Filters for Named Entities Recognition.
"""
from nazca.utils.dataio import sparqlquery


###############################################################################
# NER FILTERS #################################################################
###############################################################################
class AbstractNerFilter(object):
    """ A filter used for cleaning named entities results
    """

    def __call__(self, named_entities):
        raise NotImplementedError


class NerOccurenceFilter(object):
    """ A filter based on the number of occurence of
    named entities in the results.
    """

    def __init__(self, min_occ=None, max_occ=None):
        self.min_occ = min_occ
        self.max_occ = max_occ

    def __call__(self, named_entities):
        uris = [u for u, p, t in named_entities]
        counts = dict([(u, uris.count(u)) for u in set(uris)])
        return [
            n for n in named_entities
            if not ((self.min_occ and counts[n[0]] < self.min_occ) or
                    (self.max_occ and counts[n[0]] > self.max_occ))
        ]


class NerRDFTypeFilter(object):
    """ A filter based on the RDF type on entity
    E.g.

    filter = NerRDFTypeFilter('http://dbpedia.org/sparql',
                                ('http://schema.org/Place',
                                'http://dbpedia.org/ontology/Agent',
                                'http://dbpedia.org/ontology/Place'))

    """

    def __init__(self, endpoint, accepted_types):
        self.endpoint = endpoint
        self.accepted_types = accepted_types
        self.query = 'SELECT ?type WHERE{<%(uri)s> rdf:type ?type}'

    def __call__(self, named_entities):
        filtered_named_entities = []
        seen_uris = {}
        for uri, p, t in named_entities:
            if uri in seen_uris:
                if seen_uris[uri]:
                    filtered_named_entities.append((uri, p, t))
            else:
                results = sparqlquery(self.endpoint, self.query % {'uri': uri})
                types = set([r[0] for r in results])
                if not len(types.intersection(self.accepted_types)):
                    seen_uris[uri] = False
                else:
                    seen_uris[uri] = True
                    filtered_named_entities.append((uri, p, t))
        return filtered_named_entities


class NerDisambiguationWordParts(object):
    """ Disambiguate named entities based on the words parts.
    E.g.:
          'toto tutu': 'http://example.com/toto_tutu',
          'toto': 'http://example.com/toto'

          Then if 'toto' is found in the text, replace the URI 'http://example.com/toto'
          by 'http://example.com/toto_tutu'
    """

    def __call__(self, named_entities):
        # Create parts dictionnary
        parts = {}
        for uri, peid, token in named_entities:
            if ' ' in token.word:
                for part in token.word.split(' '):
                    parts[part.lower()] = uri
        # Replace named entities
        filtered_named_entities = []
        for uri, peid, token in named_entities:
            if token.word.lower() in parts:
                # Change URI
                uri = parts[token.word.lower()]
            filtered_named_entities.append((uri, peid, token))
        return filtered_named_entities


class NerReplacementRulesFilter(object):
    """ Allow to define replacement rules for Named Entities
    """

    def __init__(self, rules):
        self.rules = rules

    def __call__(self, named_entities):
        filtered_named_entities = []
        for uri, peid, token in named_entities:
            uri = self.rules.get(uri, uri)
            filtered_named_entities.append((uri, peid, token))
        return filtered_named_entities
