"""Represents action to take in order to de-id a single field"""
import logging
import re

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

from .. import util

log = logging.getLogger(__name__)
RE_TIMEZONE = re.compile(r'(.+)([-+]\d{4})$')


class DeIdField:
    """Abstract class that represents action to take to de-identify a single field"""
    __metaclass__ = ABCMeta

    # NOTE: If you derive from this class, set a unique key for the factory method to use
    key = None
    __hash_cache = {}

    def __init__(self, fieldname):
        self.fieldname = fieldname

    @classmethod
    def factory(cls, config):
        """Create a new file profile instance for the given name.

        Arguments:
            config (dict): The configuration dictionary
        """
        result = None
        fieldname = config['name']

        for subclass in cls.__subclasses__():
            for key in config.keys():
                if subclass.key == key:
                    result = subclass(fieldname)
                    break

        if not result:
            raise ValueError('Unknown de-identify action')

        result.load_config(config)
        return result

    def to_config(self):
        """Convert to configuration dictionary"""
        result = {'name': self.fieldname}
        self.local_to_config(result)
        return result

    def local_to_config(self, config):
        """Convert rule specific settings to configuration dictionary"""
        # Most fields just store True in the key field
        config[self.key] = True

    def load_config(self, config):
        """Load rule specific settings from configuration dictionary"""

    def deidentify(self, profile, state, record):
        """Perform the update - default implementation is to do a replace"""
        new_value = self.get_value(profile, state, record)
        if new_value is not None:
            profile.replace_field(state, record, self.fieldname, new_value)

    @abstractmethod
    def get_value(self, profile, state, record):
        """Get the transformed value, given profile state and record"""

    @classmethod
    def _hash(cls, profile, value, output_format='hex'):
        """Hash a value according to profile rules"""
        # Memoize hash results
        salt = profile.hash_salt
        hash_key = (salt, value, output_format)
        result = cls.__hash_cache.get(hash_key)
        if not result:
            result = util.hash_value(value, algorithm=profile.hash_algorithm, salt=salt, output_format=output_format)
            cls.__hash_cache[hash_key] = result
        return result

    def _perform_date_inc(self, profile, state, record, fmt, timezone=False):
        new_value = None
        original = profile.read_field(state, record, self.fieldname)
        if original:
            suffix = ''

            # NOTE: Parsing optional timezone doesn't seem to be universally supported
            # Since we don't actually need the value, just strip and reapply if present
            if timezone:
                match = RE_TIMEZONE.match(original)
                if match:
                    original = match.group(1)
                    suffix = match.group(2)

            # TODO: Should we capture ValueError here?
            try:
                orig_date = datetime.strptime(original, fmt)
                new_date = orig_date + timedelta(days=profile.date_increment)
                new_value = new_date.strftime(fmt) + suffix
            except ValueError as err:
                log.error('NO ACTION WAS TAKEN! Unable to parse date field: %s', err)

        return new_value


class DeIdRemoveField(DeIdField):
    """Action to remove a field from the record"""
    key = 'remove'

    def deidentify(self, profile, state, record):
        profile.remove_field(state, record, self.fieldname)

    def get_value(self, profile, state, record):
        return None


class DeIdReplaceField(DeIdField):
    """Action to replace a field from the record"""
    key = 'replace-with'

    def __init__(self, fieldname):
        super(DeIdReplaceField, self).__init__(fieldname)
        self.value = None

    def get_value(self, profile, state, record):
        return self.value

    def local_to_config(self, config):
        config['replace-with'] = self.value

    def load_config(self, config):
        self.value = config['replace-with']


class DeIdHashField(DeIdField):
    """Action to replace a field with it's hashed value"""
    key = 'hash'

    def get_value(self, profile, state, record):
        new_value = None
        original = profile.read_field(state, record, self.fieldname)
        if original:
            new_value = self._hash(profile, original)

            # Respect character limit, if applicable
            if profile.hash_digits > 0:
                new_value = new_value[:profile.hash_digits]

        return new_value


class DeIdHashUIDField(DeIdField):
    """Action to replace a uid field with it's hashed value"""
    key = 'hashuid'

    def get_value(self, profile, state, record):
        new_value = None

        original = profile.read_field(state, record, self.fieldname)
        if original:
            orig_parts = original.split('.')

            # Determine how many fields are required
            required = profile.uid_prefix_fields + profile.uid_suffix_fields
            if required > len(orig_parts):
                raise ValueError('UID is too short to be hashed')

            # Get the digest
            digest = self._hash(profile, original, output_format='dec')
            result_parts = []

            # Build the new UID string with prefix
            if profile.uid_prefix_fields > 0:
                result_parts += orig_parts[:profile.uid_prefix_fields]

            # Parts taken from hash string
            idx = 0
            for seg in profile.uid_hash_fields:
                result_parts.append(digest[idx:idx + seg])
                idx += seg

            # And suffix
            if profile.uid_suffix_fields > 0:
                suffix = []
                # Keep no more than the number of digits specified
                # i.e. strip any dates
                for part in orig_parts[-profile.uid_suffix_fields:]:
                    if len(part) > profile.uid_max_suffix_digits:
                        part = part[-profile.uid_max_suffix_digits:]
                    suffix.append(part)
                result_parts += suffix

            new_value = '.'.join(result_parts)

        return new_value


class DeIdIncrementDateField(DeIdField):
    """Action to replace a field with it's incremented date"""
    key = 'increment-date'

    def get_value(self, profile, state, record):
        return self._perform_date_inc(profile, state, record, profile.date_format)


class DeIdIncrementDateTimeField(DeIdField):
    """Action to replace a field with it's incremented date"""
    key = 'increment-datetime'

    def get_value(self, profile, state, record):
        return self._perform_date_inc(profile, state, record, profile.datetime_format, timezone=True)
