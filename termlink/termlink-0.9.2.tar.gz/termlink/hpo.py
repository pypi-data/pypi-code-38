"""Handles Human Phenotype Ontology conversion.

This module provides methods to extract and transform the HPO (Human Phenotype Ontology).

The download files for HPO are provided at https://hpo.jax.org/app/download/ontology
"""
import json

from urllib.parse import urlparse

from pronto import Ontology, Term

from termlink.commands import SubCommand
from termlink.models import Coding, Relationship, RelationshipSchema
from termlink.services import RelationshipService


def _to_equivalence_from_scope(scope):
    """Converts a scope into an equivalence

    Args:
        scope: a `pronto.Synonym.scope`

    Returns:
        an equivalence from https://www.hl7.org/fhir/valueset-concept-map-equivalence.html
    """
    try:
        return {
            'BROAD': 'wider',
            'NARROW': 'narrower',
            'EXACT': 'equivalent',
            'RELATED': 'relatedto'
        }[scope]
    except KeyError:
        raise RuntimeError('scope \'%s\' is not supported' % scope)


def _to_system(abbreviation):
    """Converts an abbreviation to a system identifier.

    Args:
        abbreviation: a `pronto.Term.id`

    Returns:
        a system identifier
    """
    try:
        return {
            'HP': 'http://www.human-phenotype-ontology.org/'
        }[abbreviation]
    except KeyError:
        raise RuntimeError(
            'system abbreviation \'%s\' is not supported' % abbreviation)


def _to_coding(term):
    """Converts a term into a `Coding`.

    Args:
        term: A `pronto.Term`

    Returns:
        a `termlink.models.Coding`
    """
    (abbreviation, code) = term.id.split(':')
    return Coding(
        system=_to_system(abbreviation),
        code=code,
        display=term.name
    )


def _to_relationship(source, equivalence, target):
    """Converts a source and target `pronto.Term` into a JSON object.

    Args:
        source: a `pronto.Term`
        equivalence: a concept map equivalence
        target: a `pronto.Term`

    Returns:
        a 'termlink.models.Relationship` in JSON form
    """
    source = _to_coding(source)
    target = _to_coding(target)
    return Relationship(equivalence, source, target)


class Command(SubCommand):
    "A command executor for Human Phenotype Ontology operations."
    @staticmethod
    def execute(args):
        uri = urlparse(args.uri)
        skip_synonyms = args.skip_synonyms
        skip_alt_ids = args.skip_alt_ids

        service = Service(uri, skip_alt_ids, skip_synonyms)

        relationships = service.get_relationships()
        schema = RelationshipSchema()
        relationships = [schema.dump(relationship)
                         for relationship in relationships]
        print(json.dumps(relationships))


class Service(RelationshipService):
    "Converts the Human Phenotype Ontology"

    def __init__(self, uri, skip_alt_ids=False, skip_synonyms=False):
        """Bootstraps a service

        Args:
            uri: URI to root location of .obo files
            skip_alt_ids: Skips 'alt_id' conversions if True
            skip_synonyms: Skips 'synonym' conversions if True
        """
        if uri.scheme != 'file':
            raise ValueError("'uri.scheme' %s not supported" % uri.scheme)

        self.uri = uri
        self.skip_synonyms = skip_synonyms
        self.skip_alt_ids = skip_alt_ids

    def get_relationships(self):
        """Parses a list of `Relationship` objects

        Returns:
            yields `Relationship`s in JSON form
        """
        ontology = Ontology(self.uri.path)

        # child to parent relationships
        for term in ontology:
            for child in term.children:
                yield _to_relationship(child, "subsumes", term)

        # parent to child relationships
        for term in ontology:
            for parent in term.parents:
                yield _to_relationship(parent, "specializes", term)

        # alt_id relationships:
        if not self.skip_alt_ids:
            for term in ontology:
                for other, values in term.other.items():
                    if other == 'alt_id':
                        for value in values:
                            target = Term(
                                id=value,
                                name=term.name,
                                desc=term.desc
                            )
                            yield _to_relationship(term, "equal", target)

        # synonym relationships
        if not self.skip_synonyms:
            for term in ontology:
                for synonym in term.synonyms:
                    target = Term(
                        id=term.id,
                        name=synonym.desc,
                        desc=term.desc
                    )
                    equivalence = _to_equivalence_from_scope(synonym.scope)
                    yield _to_relationship(term, equivalence, target)

        # todo - lookup concept based on system and code
        # xref relationships
        # for term in ontology:
        #     for other, values in term.other.items():
        #         if other == 'xref':
        #             for value in values:
        #                 (abbreviation, code) = value.split(':')
        #                 system = _to_system(abbreviation)
