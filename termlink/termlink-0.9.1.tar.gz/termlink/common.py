"""Handles conversions of common ontology formats

This module provides support for converting common ontology formats. The
following file types are supported:

- .obo: https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_4.html
- .owl: https://www.w3.org/OWL/

"""

import json

from urllib.parse import urlparse

import validators

from pronto import Ontology

from termlink.models import Coding, Relationship, RelationshipSchema

_SCOPE_TO_EQUIVALENCE = {
    'equivalent_to': 'equivalent'
}

def _to_equivalence_from_scope(scope):
    """Converts a scope into an equivalence

    Args:
        scope: a `pronto.Synonym.scope`

    Returns:
        an equivalence from https://www.hl7.org/fhir/valueset-concept-map-equivalence.html
    """
    try:
        return _SCOPE_TO_EQUIVALENCE[scope]
    except KeyError:
        raise RuntimeError('scope \'%s\' is not supported' % scope)


def _to_coding(term, system):
    """Converts a term into a `Coding`.

    Args:
        term: A `pronto.Term`

    Returns:
        a `termlink.models.Coding`
    """
    if ':' in term.id:
        parts = term.id.rsplit(':', 1)
        code = parts[1]
        if validators.url(parts[0]):
            system = parts[0]
    else:
        code = term.id

    return Coding(
        system=system,
        code=code,
        display=term.name
    )


def _to_relationship(source, equivalence, target, system):
    """Converts a source and target `pronto.Term` into a JSON object.

    Args:
        source: a `pronto.Term`
        equivalence: a concept map equivalence
        target: a `pronto.Term`

    Returns:
        a 'termlink.models.Relationship` in JSON form
    """
    source = _to_coding(source, system)
    target = _to_coding(target, system)
    return Relationship(equivalence, source, target)


def _get_relationships(uri, system):
    """Parses a list of `Relationship` objects

    Args:
        uri:    a URI for the ontology file on the local filesystem
        system: the target system

    Returns:
        yields relationships
    """
    ontology = Ontology(uri.path)

    # child to parent relationships
    for term in ontology:
        for child in term.children:
            yield _to_relationship(child, "subsumes", term, system)

    # parent to child relationships
    for term in ontology:
        for parent in term.parents:
            yield _to_relationship(parent, "specializes", term, system)

    for term in ontology:
        for scope, references in term.other.items():
            if scope in _SCOPE_TO_EQUIVALENCE:
                for reference in references:
                    relationship = _to_equivalence_from_scope(scope)
                    yield _to_relationship(term, relationship, ontology[reference], system)


def execute(args):
    """
    Converts an ontology in a common format.

    Args:
        args:   command line arguments from argparse
    """
    uri = urlparse(args.uri)
    if uri.scheme != 'file':
        raise ValueError("'uri.scheme' %s not supported" % uri.scheme)

    schema = RelationshipSchema()
    relationships = _get_relationships(uri, args.system)
    serialized = [json.dumps(schema.dump(r)) for r in relationships]

    for o in serialized:
        print(o)

    return serialized
