"""Handles RxNorm conversion.

This module provides methods to extract, transform and load relationships
defined by the RxNorm dataset.

The download files for RxNorm are provided at https://www.nlm.nih.gov/research/umls/rxnorm/.
"""
import os
import json

from urllib.parse import urlparse

import petl as etl

from termlink.commands import SubCommand
from termlink.models import Coding, Relationship, RelationshipSchema
from termlink.services import RelationshipService

_RXNCONSO_FIELDS = ["RXCUI", "LAT", "TS", "LUI", "STT", "SUI", "ISPREF", "RXAUI",
                    "SAUI", "SCUI", "SDUI", "SAB", "TTY", "CODE", "STR", "SRL", "SUPPRESS", "CVF", ]
_RXNREL_FIELDS = ["RXCUI1", "RXAUI1", "STYPE1", "REL", "RXCUI2", "RXAUI2",
                  "STYPE2", "RELA", "RUI", "SRUI", "SAB", "SL", "DIR", "RG", "SUPPRESS", "CVF", ]

_RELATIONSHIP_TO_EQUIVALENCE = {
    'RB': 'subsumes',
}

_SAB_TO_SYSTEM = {
    'ATC': 'http://www.whocc.no/atc',
    'CVX': 'http://hl7.org/fhir/sid/cvx',
    'SNOMEDCT_US': 'http://snomed.info/sct',
}


def _to_equivalence(rel):
    """Converts a relationship into an equivalence

    Args:
        rel: relationship of second concept or atom to first concept or atom

    Returns:
        an equivalence from https://www.hl7.org/fhir/valueset-concept-map-equivalence.html
    """
    try:
        return _RELATIONSHIP_TO_EQUIVALENCE[rel]
    except KeyError:
        raise RuntimeError('rel \'%s\' is not supported' % rel)


def _to_system(sab):
    """Converts an SAB to a system.

    Args:
        sab: a UMLS source name abbreviation

    Returns:
        the identity of the terminology system
    """
    return _SAB_TO_SYSTEM.get(sab, 'http://www.nlm.nih.gov/research/umls/%s' % sab.lower())


def _to_relationship(rec):
    """Convert record in table to `Relationship`

    Record is expected to have the following fields: [source.CODE, source.STR, source.SAB, target.CODE, target.STR, target.SAB]

    Args:
        rec: A table record

    Returns:
        A `Relationship`
    """
    equivalence = _to_equivalence(rec['REL'])

    source = Coding(
        system=_to_system(rec['source.SAB']),
        code=rec['source.CODE'],
        display=rec['source.STR']
    )

    target = Coding(
        system=_to_system(rec['target.SAB']),
        code=rec['target.CODE'],
        display=rec['target.STR']
    )

    return Relationship(equivalence, source, target)


def _to_json(rec):
    """Converts a record to a formatted `Relationship` in JSON form.

    Args:
        rec: A table record

    Returns:
        A new record containing a single field, which is the JSON object
    """
    relationship = _to_relationship(rec)
    schema = RelationshipSchema()
    return [json.dumps(schema.dump(relationship))]


class Command(SubCommand):
    "A command executor for RxNorm operations"

    @staticmethod
    def execute(args):
        """Prints a JSON array of `Relationship` objects to stdout

        Args:
            args: `argparse` parsed arguments
        """
        uri = urlparse(args.uri)
        vocabularies = set(args.vocabulary)
        suppress_flags = set(args.suppress)
        service = Service(uri, vocabularies, suppress_flags)
        table = service.get_relationships()
        etl.io.totext(table, encoding='utf8', template='{relationship}\n')


class Service:
    """Converts the RxNorm database"""

    def __init__(self, uri, vocabularies=set(['RXNORM']), suppress_flags=set(['N'])):
        """Bootstraps a service

        Args:
            uri: URI to root location of .rrf files
            vocabularies: source vocabularies
            suppress_flags: suppress flags
        """

        if uri.scheme != 'file':
            raise ValueError("'uri.scheme' %s not supported" % uri.scheme)

        self.uri = uri
        self.vocabularies = vocabularies
        self.suppress_flags = suppress_flags

    def get_relationships(self):
        "Parses a list of `Relationship` objects."
        path = os.path.join(self.uri.path, 'RXNCONSO.RRF')
        rxnconso = etl \
            .fromcsv(path, delimiter='|') \
            .setheader(_RXNCONSO_FIELDS) \
            .select(lambda rec: rec['SAB'] in self.vocabularies) \
            .select(lambda rec: rec['SUPPRESS'] in self.suppress_flags) \
            .cut('RXCUI', 'CODE', 'STR', 'SAB')

        source = rxnconso.prefixheader('source.')
        target = rxnconso.prefixheader('target.')

        path = os.path.join(self.uri.path, 'RXNREL.RRF')
        rxnrel = etl \
            .fromcsv(path, delimiter='|') \
            .setheader(_RXNREL_FIELDS) \
            .select(lambda rec: rec['SAB'] in self.vocabularies) \
            .select(lambda rec: rec['STYPE1'] == 'CUI') \
            .select(lambda rec: rec['STYPE2'] == 'CUI') \
            .select(lambda rec: rec['REL'] in _RELATIONSHIP_TO_EQUIVALENCE.keys()) \
            .cut('REL', 'RXCUI1', 'RXCUI2')

        return rxnrel \
            .join(source, lkey='RXCUI1', rkey='source.RXCUI') \
            .join(target, lkey='RXCUI2', rkey='target.RXCUI') \
            .rowmap(_to_json, ['REL', 'source.CODE', 'source.STR', 'source.SAB', 'target.CODE', 'target.STR', 'target.SAB']) \
            .setheader(['relationship'])
