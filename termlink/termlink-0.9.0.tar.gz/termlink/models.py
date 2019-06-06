"""Model representations of API interfaces"""

from dataclasses import dataclass

from marshmallow import Schema, fields

from termlink.configuration import Config

_configuration = Config()
_logger = _configuration.logger


class CodingSchema(Schema):
    """A `Coding` schema

    Attributes:
        type:       string field
        system:     string field
        version:    string field
        code:       string field
        display     string field
    """
    type = fields.Str()
    system = fields.Str()
    version = fields.Str()
    code = fields.Str()
    display = fields.Str()


@dataclass(frozen=True)
class Coding():
    """
    A 'Coding' object as defined by the API.

    Attributes:
        type (str):     the type of object
        system (str):   identity of the terminology system
        version (str):  version of the system
        code (str):     symbol in syntax defined by the system
        display (str):  representation defined by the system
    """
    type: str = 'coding'
    system: str = None
    version: str = None
    code: str = None
    display: str = None


class RelationshipSchema(Schema):
    """A `Relationship` schema

    Attributes:
        system: string field
        source: `CodingSchema` field
        target: `CodingSchema` field
    """
    equivalence = fields.Str()
    source = fields.Nested(CodingSchema())
    target = fields.Nested(CodingSchema())


@dataclass(frozen=True)
class Relationship():
    """
    A 'Relationship' object as defined by the API.

    Attributes:
        equivalence (str):  The degree of equivalence between concepts.
        source object:       The source concept.
        target object:       The target concept.
    """
    equivalence: str
    source: Coding
    target: Coding
