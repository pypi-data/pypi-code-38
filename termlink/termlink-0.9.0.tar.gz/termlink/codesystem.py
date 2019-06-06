"""Handles FHIR CodeSystem Resource conversion.


This modules provides methods to extract, transform and load relationship
defined by a FHIR CodeSystem resource.

Various FHIR CodeSystems are available at https://www.hl7.org/fhir/codesystem.html
"""

import json

from urllib.parse import urlparse

from termlink.models import Coding, Relationship, RelationshipSchema

def _get_relationships(content):
    '''Extracts concept relationships from a CodeSystem

    Args:
        content: a dict of a CodeSystem

    Returns:
        yields relationships
    '''
    
    system = content['url']
    version = content['version']

    sources = content['concept']
    targets = [sources[-1]] + sources[0:-1]
    for source, target in zip(sources, targets):
        
        source = Coding(
            system=system,
            version=version,
            code=source['code'],
            display=source['display']
        )

        target = Coding(
            system=system,
            version=version,
            code=target['code'],
            display=target['display']
        )

        yield Relationship('disjoint', source, target)

def execute(args):
    '''Converts a FHIR CodeSystem Resource

    Args:
        args:   command line arguments from argparse
    '''
    uri = urlparse(args.uri)
    if uri.scheme != 'file':
        raise ValueError(f"uri.scheme '{uri.scheme}' is not supported")

    with open(uri.path) as f:
        content = json.load(f)

    schema = RelationshipSchema()
    relationships = _get_relationships(content)
    serialized = [json.dumps(schema.dump(r)) for r in relationships]

    for o in serialized:
        print(o)

    return serialized

    
