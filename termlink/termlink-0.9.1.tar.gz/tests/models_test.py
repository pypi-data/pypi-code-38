"""Verifies the 'models.py' module"""

from nose.tools import eq_

from termlink.models import Coding, CodingSchema, Relationship, RelationshipSchema


def test_convert_coding_to_json():
    """Checks converting `Coding` to JSON"""

    system = 'system'
    version = 'version'
    code = 'code'
    display = 'display'

    coding = Coding(
        system=system,
        version=version,
        code=code,
        display=display
    )

    exp = {
        'type': 'coding',
        'system': system,
        'version': version,
        'code': code,
        'display': display
    }

    schema = CodingSchema()
    res = schema.dump(coding)

    eq_(exp, res)


def test_convert_empty_coding_to_json():
    """Checks converting `Coding` with no values to JSON"""

    coding = Coding()

    exp = {
        'type': 'coding',
        'system': None,
        'version': None,
        'code': None,
        'display': None
    }

    schema = CodingSchema()
    res = schema.dump(coding)

    eq_(exp, res)


def test_convert_partial_coding_to_json():
    """Checks converting `Coding` with some values to JSON"""

    system = 'system'

    coding = Coding(system=system)

    exp = {
        'type': 'coding',
        'system': system,
        'version': None,
        'code': None,
        'display': None
    }

    schema = CodingSchema()
    res = schema.dump(coding)

    eq_(exp, res)


def test_convert_relationship_to_json():
    """Checks converting `Relationship` to JSON"""

    equivalence = 'equivalence'
    system = 'system'
    version = 'version'
    code = 'code'
    display = 'display'

    source = Coding(
        system=system,
        version=version,
        code=code,
        display=display
    )

    target = Coding(
        system=system,
        version=version,
        code=code,
        display=display
    )

    relationship = Relationship(equivalence, source, target)

    exp = {
        'equivalence': equivalence,
        'source': {
            'type': 'coding',
            system: system,
            version: version,
            code: code,
            display: display
        },
        'target': {
            'type': 'coding',
            system: system,
            version: version,
            code: code,
            display: display
        }
    }

    schema = RelationshipSchema()
    res = schema.dump(relationship)

    eq_(exp, res)
