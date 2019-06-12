from abc import abstractmethod
from .. import errors
from marshmallow import ValidationError, Schema, fields

class CredsBaseSchema(Schema):
    # wont be required until persisted
    provider_id = fields.String(required=False, allow_none=True, allow_blank=False)
    label = fields.String(required=False, allow_none=True, allow_blank=False)
    provider_class = fields.String(required=True, allow_none=False, allow_blank=False)
    provider_type = fields.String(required=True, allow_none=False, allow_blank=False)

    created_at = fields.DateTime(required=False, allow_none=True, allow_blank=False)
    modified_at = fields.DateTime(required=False, allow_none=True, allow_blank=False)


    def __init__(self, strict=True, **kwargs):
        super(CredsBaseSchema, self).__init__(strict=strict, **kwargs)

# pylint: disable=too-few-public-methods
class Creds(object):
    """The creds base object. Provides interface for provider cred implementations"""

    # The schema for validating configuration (required), must be overloaded
    _schema = None

    provider_id = None
    provider_class = None
    provider_type = None
    label = None
    # Creds are nested in this key
    creds = None

    # Not quite a trait
    created_at = None
    modified_at = None
    #origin = None

    def __init__(self, provider_class=None, provider_type=None, provider_label=None, config=None):
        """Initializes this class with the given configuration

        Args:
            provider_class (string): Static string from the providerClass enum
            provider_type (string): Static string for one of the registered types
            provider_label (string): Provider label
            config (dict): Config dictionary for this cred type
            created_at (DateTime): created data
            modified_at (DateTime): last midified time
        """
        self.provider_class = provider_class
        self.provider_type = provider_type
        self.label = provider_label
        self.creds = config

        #self._validate_config()

    def validate(self):
        """Validates the schema

        Raises: ValidationError, ValueError
        """

        if not self._schema:
            raise ValueError('No Schema defined for the model')

        # bubble up errors
        self._schema.validate(self._schema.dump(self).data)
        return True


    @abstractmethod
    def validate_permissions(self):
        """Does the actual permission validation for the implemented provider"""
