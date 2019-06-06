import colander
import requests
import rfc3987


class ValidationFailure(Exception):
    def __init__(self, msg, errors):
        self.msg = msg
        self.errors = errors


def sqlalchemy_validator(node, value, model, session=None, msg='%s is ongeldig'):
    """
    Validate a sqlalchemy object or identifier.
    Function checks if value is an instance of sqlalchemy model
    or an id of one.
    :param node: A colander SchemaNode.
    :param value: The value to be validated. Is the key of the
        SQLAlchemy model.
    :param model: A SQLAlchemy model.
    :param session: A SQLAlchemy session. Is required if value is not an
        instance of a SQLAlchemy model.
    :param msg: A msg to attach to a `colander.Invalid` exception.
    :raises colander.Invalid: If not a valid sqlalchemy model.
    """

    m = session.query(model).get(value)

    if not m:
        raise colander.Invalid(
            node,
            msg % value
        )

    return m


#########################################################################################
# BASIC DATA TYPES (ENRICHED FOR O.E.)
#########################################################################################
class OEBoolean(colander.Boolean):
    """
    The default deserialization casts every value to a Boolean. This is not what we want.
    courtesy of cahytinne
    """
    def deserialize(self, node, cstruct):

        if cstruct is None or cstruct is colander.null:
            cstruct = colander.null  # handling this depends on being required or not

        elif not type(cstruct) is bool:
            raise colander.Invalid(node, '{0} is not a valid Boolean.'.format(cstruct))

        result = super(OEBoolean, self).deserialize(node, cstruct)
        return result


class OEInteger(colander.Integer):
    """
    the default deserialization casts floats to ints. This is not what we want.
    see also: https://github.com/Pylons/colander/issues/292
    """
    def deserialize(self, node, cstruct):

        if cstruct is None or cstruct is colander.null:
            cstruct = colander.null  # handling this depends on being required or not

        elif not type(cstruct) is int:
            raise colander.Invalid(node, '{0} is not a valid Integer.'.format(cstruct))

        result = super(OEInteger, self).deserialize(node, cstruct)
        return result


#########################################################################################
# SCHEMA NODES (FOR O.E)
#########################################################################################
class OEIDSchemaNode(colander.SchemaNode):
    schema_type = OEInteger

    def validator(self, node, cstruct):
        if cstruct < 0:
            raise colander.Invalid(node, 'Geen geldig ID ({}< 0)'.format(cstruct))


class OEEmailSchemaNode(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.All(colander.Length(max=255), colander.Email('Dit is geen geldig emailadres.'))


class OEStringSchemaNode(colander.SchemaNode):
    schema_type = colander.String


class OEDateTimeSchemaNode(colander.SchemaNode):
    schema_type = colander.DateTime


class OEBoolSchemaNode(colander.SchemaNode):
    schema_type = OEBoolean


class UrlSchemaNode(colander.SchemaNode):
    schema_type = colander.String
    title = 'Url'

    def validator(self, node, cstruct):
        if len(cstruct) > 2083:
            raise colander.Invalid(node, "URI is too long (max=2083).", cstruct)
        if not rfc3987.match(cstruct, rule='URI'):
            raise colander.Invalid(node, '{0} is geen geldige URL.'.format(cstruct))

        try:
            res = requests.get(cstruct, headers={"Accept": "application/json"})
        except requests.ConnectionError:
            raise colander.Invalid(node, "URL bestaat niet.", cstruct)
        if res is not None and res.status_code == 404:
            raise colander.Invalid(node, "URL bestaat niet.", cstruct)


class UriSchemaNode(colander.SchemaNode):
    """
    URL validator. rfc3987 is used to check if a URL is correct (https://pypi.python.org/pypi/rfc3987/)
    If ``msg`` is supplied, it will be the error message to be used when raising :exc:`colander.Invalid`;
    otherwise, defaults to 'Invalid URL'.
    """

    schema_type = colander.String
    title = 'Erfgoed id Uri'

    def validator(self, node, cstruct):
        if len(cstruct) > 100:
            raise colander.Invalid(node, "URI is too long (max=100).", cstruct)
        if not rfc3987.match(cstruct, rule='URI'):
            raise colander.Invalid(node, '{0} is geen geldige URI.'.format(cstruct))


class ExternalUriSchemaNode(UriSchemaNode):
    schema_type = colander.String

    def validator(self, node, cstruct):
        super(ExternalUriSchemaNode, self).validator(node, cstruct)

        try:
            res = requests.get(cstruct, headers={"Accept": "application/json"})
        except requests.ConnectionError:
            raise colander.Invalid(node, "URI bestaat niet.", cstruct)
        if res is not None and res.status_code == 404:
            raise colander.Invalid(node, "URI bestaat niet.", cstruct)