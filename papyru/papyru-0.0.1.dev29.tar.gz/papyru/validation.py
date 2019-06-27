import cerberus
import json
import jsonschema
import yaml
from bravado_core.spec import Spec
from bravado_core.validate import validate_object

from .problem import Problem


def _validation_error(detail):
    return Problem.unsupported_media_type(detail=detail)


class Validator:
    def validate(self, representation):
        raise Exception('implement me')


class BravadoValidator(Validator):
    def __init__(self, spec_file_name, definition_name):
        with open(spec_file_name, 'r') as f:
            spec_dict = yaml.load(f.read())
            self.spec = Spec.from_dict(spec_dict)
            self.schema = spec_dict['definitions'][definition_name]

    def validate(self, representation):
        try:
            validate_object(self.spec, self.schema, representation)
            return representation
        except jsonschema.exceptions.ValidationError as exc:
            raise _validation_error('%s' % exc)


class JSONSchemaValidator(Validator):
    def __init__(self, spec_file_name):
        with open(spec_file_name, 'r') as f:
            self.schema = json.load(f)

    def validate(self, representation):
        try:
            jsonschema.validate(instance=representation, schema=self.schema)
            return representation
        except jsonschema.exceptions.ValidationError as exc:
            raise _validation_error('%s' % exc)


class CerberusValidator(Validator):
    def __init__(self, schema_description):
        self.validator = cerberus.Validator(schema_description['schema'])

        if 'allow_unknown' in schema_description:
            self.validator.allow_unknown = schema_description['allow_unknown']

    def validate(self, representation):
        try:
            if not self.validator.validate(representation):
                raise _validation_error('%s' % self.validator.errors)
            else:
                return self.validator.normalized(representation)
        except cerberus.validator.DocumentError as exc:
            raise _validation_error('%s' % exc)
