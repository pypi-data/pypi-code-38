import re
from functools import partial

from dirty_validators.basic import AnyOf, BaseValidator, IsEmpty, Length, NumberRange, Regexp
from dirty_validators.complex import AllItems, IfField, ItemLimitedOccurrences, ModelValidate, Optional, Required, Some

from jsonschema4dm.models import BaseJsonSchemaObject, JsonSchemaRefObject

IsBoolean = partial(AnyOf, values=[True, False])

JsonSchemaSimpleTypes = partial(AnyOf, values=["array", "boolean", "integer",
                                               "null", "number", "object", "string"])


class IsRegex(BaseValidator):
    NOT_REGEX = 'notRegex'

    error_messages = {NOT_REGEX: "'$value' is not a valid regular expression"}

    def _internal_is_valid(self, value, *args, **kwargs):
        regex = re.compile(r'^/(.+)/m?i?g?$')
        try:
            pattern = regex.match(value).group(1)
        except AttributeError:
            self.error(self.NOT_REGEX, value)
            return False

        try:
            re.compile(pattern)
        except re.error:
            self.error(self.NOT_REGEX, value)
            return False
        return True


class URI(Regexp):
    """
    Simple regexp based uri validation. Much like the email validator, you
    probably want to validate the uri later by other means if the uri must
    resolve.
    """

    INVALID_URI = 'invalidURI'

    error_code_map = {Regexp.NOT_MATCH: INVALID_URI}
    error_messages = {INVALID_URI: "'$value' is not a valid uri."}

    def __init__(self, *args, **kwargs):
        regex = r'^([a-z]+\:\/\/)?(([^\/\:]+\.[a-z]{2,10}\/?)?|([0-9]{1,3}\.){3}' \
                r'[0-9]{1,3})?(\:[0-9]+\/?)?([^?\#])*(\?[^\#]*)?(\#.*)?$'
        super(URI, self).__init__(regex, re.IGNORECASE, *args, **kwargs)


class IsJsonSchemaObject(Some):

    def __init__(self, *args, **kwargs):
        validators = [
            JsonSchemaMetaValidator(),
            JsonSchemaRefObjectValidator()
        ]
        super(IsJsonSchemaObject, self).__init__(validators, *args, **kwargs)


class JsonSchemaMetaValidator(ModelValidate):
    __modelclass__ = BaseJsonSchemaObject

    id = Optional()
    d_schema = Optional(validators=[URI()])
    title = Optional()
    description = Optional()

    default = Optional()  # TODO

    multipleOf = Optional(validators=[NumberRange(min=0)])
    maximum = Optional()

    exclusiveMaximum = Optional(validators=[IfField(field_name='maximum',
                                                    field_validator=IsEmpty(),
                                                    validator=IsEmpty())])
    exclusiveMinimum = Optional(validators=[IfField(field_name='minimum',
                                                    field_validator=IsEmpty(),
                                                    validator=IsEmpty())])

    maxLength = Optional(validators=[NumberRange(min=0)])
    minLength = Optional(validators=[NumberRange(min=0)])
    pattern = Optional(validators=[IsRegex()])

    additionalItems = Optional(validators=[Some(validators=[IsBoolean(),
                                                            IsJsonSchemaObject()])])
    items = Optional(validators=[Some(validators=[IsJsonSchemaObject(),
                                                  AllItems(validator=IsJsonSchemaObject())])])

    maxItems = Optional(validators=NumberRange(min=0))
    minItems = Optional(validators=NumberRange(min=0))

    uniqueItems = Optional()

    maxProperties = Optional(validators=NumberRange(min=0))
    minProperties = Optional(validators=NumberRange(min=0))

    required = Optional(validators=[AllItems(validator=Length(min=1))])

    additionalProperties = Optional(validators=[Some(validators=[IsBoolean(),
                                                                 IsJsonSchemaObject()])])

    definitions = Optional(validators=[AllItems(validator=IsJsonSchemaObject())])

    properties = Optional(validators=[AllItems(validator=IsJsonSchemaObject())])
    patternProperties = Optional(validators=[AllItems(validator=IsJsonSchemaObject())])

    dependencies = Optional(validators=[Some(validators=[JsonSchemaSimpleTypes(),
                                                         AllItems(validator=Length(min=1))])])

    """
            
        "default": {}
    """

    enum = Optional(validators=[Length(min=1),
                                ItemLimitedOccurrences(min_occ=1, max_occ=1)])

    type = Optional(validators=[Some(validators=[JsonSchemaSimpleTypes(),
                                                 AllItems(validator=JsonSchemaSimpleTypes())])])

    allOf = Optional(validators=[Length(min=1),
                                 AllItems(validator=IsJsonSchemaObject())])
    anyOf = Optional(validators=[Length(min=1),
                                 AllItems(validator=IsJsonSchemaObject())])
    oneOf = Optional(validators=[Length(min=1),
                                 AllItems(validator=IsJsonSchemaObject())])
    p_not = Optional(validators=[IsJsonSchemaObject()])

    default = Optional()

    def _internal_is_valid(self, value, *args, **kwargs):
        result = super(JsonSchemaMetaValidator, self)._internal_is_valid(value, *args, **kwargs)

        if not result and self.stop_on_fail:
            return False

        # TODO validate default value

        return True


class JsonSchemaRefObjectValidator(ModelValidate):
    __modelclass__ = JsonSchemaRefObject

    d_ref = Required(validators=[URI()])
