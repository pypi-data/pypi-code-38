"""Base provider class for all provider types"""
from abc import abstractmethod
from marshmallow import Schema, fields, ValidationError


from .. import errors


class BaseSchema(Schema):
    type = fields.String(required=True, allow_none=False, allow_blank=False)
    id = fields.String(required=True, allow_none=False, allow_blank=False)

class BaseProviderSchema(Schema):
    _id = fields.String(required=False, allow_none=True, allow_blank=False)
    provider_id = fields.String(required=False, allow_none=True, allow_blank=False) # wont be required until persisted
    label = fields.String(required=True)
    provider_class = fields.String(required=True)
    provider_type = fields.String(required=True)
    created = fields.DateTime(required=False)
    modified = fields.DateTime(required=False)
    origin = fields.Nested(BaseSchema, required=True, many=False)

    def __init__(self, strict=True, **kwargs):
        super(BaseProviderSchema, self).__init__(strict=strict, **kwargs)

# pylint: disable=too-few-public-methods
class BaseProvider(object):
    """The provider base object. """

    # The schema for minimum configuration (required)
    # schema will be overloaded for specific type validation
    _schema = None

    # Explicitly set the object attributes
    _id = None
    provider_id = None
    creds = None
    config = None
    provider_class = None
    provider_type = None
    label = None
    origin = None

    def __init__(self, provider_class=None, provider_type=None, provider_label=None, config=None, creds=None):
        """Initializes this class with the given configuration

        Args:
            provider_class (String): Constant string from ProviderClass enum
            provider_type (String): Constant string for supported provider type
            label (String): Human readable lable
            config (dict): The configuration object for provider
            creds (Creds): The credentials object
        """
        self.label = provider_label
        self.provider_class = provider_class
        self.provider_type = provider_type

        self.config = config
        self.creds = creds

    def validate(self):
        """ validate the object using the inherited scheam from the instantaited class"""
        if not self._schema:
            raise ValueError('No Schema provided for Model')

        # just let errors bubble up
        # We pull out the schema fields first and pass only those through validation
        try:
            self._schema.validate(self._schema.dump(self).data)
        except ValidationError as e:
            # Convert to avoid format KeyErrors in ErrorBase.__str__
            msg = str(e.messages).replace('{','{{').replace('}','}}')
            raise errors.ValidationError(msg)

    @abstractmethod
    def validate_permissions(self):
        """Does the actual permission validation for the implemented provider"""

    @abstractmethod
    def get_redacted_config(self):
        """Return the configuration with all private key material and credentials replaced with None.

        This function can be used to retrieve scrubbed configuration, with only non-confidential
        fields populated.

        Args:
            placeholder: The placeholder for redacted fields.

        Returns:
            dict: The non-confidential configuration
        """
