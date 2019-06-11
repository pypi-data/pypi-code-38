#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
For producing a JSON schema appropriate for use by clients, based on a
Zope schema.

The ``TAG`` constants are intended to be set as (boolean) tagged values
on fields of interfaces, helping determine how the schema is built.

..  note:: This schema is ad-hoc and non-standard.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from copy import copy

try:
    from collections.abc import Sequence
except ImportError: # pragma: no cover
    # Python 2
    from collections import Sequence

from numbers import Number

from six import integer_types
from six import string_types
from six import text_type

from zope.i18n import translate

from zope.interface.interfaces import IMethod
from zope.interface.interfaces import IInterface

from zope.schema import interfaces as sch_interfaces
from zope.schema import vocabulary as sch_vocabulary

from nti.schema.interfaces import IVariant
from nti.schema.interfaces import find_most_derived_interface

__docformat__ = "restructuredtext en"


#: Don't display this by default in the UI
TAG_HIDDEN_IN_UI = "nti.dataserver.users.field_hidden_in_ui"

#: Qualifying details about how the field should be treated, such as data source
#: The ``UI_TYPE`` values are defined known values for this tag.
TAG_UI_TYPE = 'nti.dataserver.users.field_type'

#: Overrides the value from the field itself
TAG_REQUIRED_IN_UI = 'nti.dataserver.users.field_required'

#: Overrides the value from the field itself, if true
TAG_READONLY_IN_UI = 'nti.dataserver.users.field_readonly'

#: A tagged value that echos semi-arbitrary data back in the schema
#: under the key ``application_info``.
#:
#: The value for this field *must* be a mapping object whose keys
#: are strings and whose values are JSON serializable. Text values
#: (specifically `zope.i18nmessageid.Message` objects) will be translated
#: when put into the schema. The object in the schema *will not* be the object
#: in the tagged value, and constituent composite values will also be copied.
#: (In case any post-processing of the schema is done based on current user,
#: request or site, this isolates such modifications.)
#:
#: .. versionadded:: 1.12.0
TAG_APPLICATION_INFO = 'nti.schema.jsonschema.field_application_info'

# Known types
#: The email type
UI_TYPE_EMAIL = 'nti.dataserver.users.interfaces.EmailAddress'

#: An email type that is stored as a non-recoverable hash.
#: The value is chosen so that a begins-with test will match
#: either this or :const:`UI_TYPE_EMAIL`, making validation easier
UI_TYPE_HASHED_EMAIL = UI_TYPE_EMAIL + ":Hashed"

#: Something that can be set once, typically during account creation
UI_TYPE_ONE_TIME_CHOICE = 'nti.dataserver.users.interfaces.OneTimeChoice'

def get_ui_type_from_interface(iface):
    ui_type = iface.getName()
    ui_type = ui_type[1:] if ui_type.startswith('I') else ui_type
    return ui_type
_interface_to_ui_type = interface_to_ui_type = get_ui_type_from_interface # BWC

def get_ui_type_from_field_interface(field):
    derived_field_iface = find_most_derived_interface(field, sch_interfaces.IField)
    if derived_field_iface is not sch_interfaces.IField:
        ui_type = get_ui_type_from_interface(derived_field_iface)
        return ui_type
    return None
_ui_type_from_field_iface = ui_type_from_field_iface = get_ui_type_from_field_interface # BWC

def get_ui_types_from_field(field):
    ui_type = ui_base_type = None
    _type = getattr(field, '_type', None)
    if isinstance(_type, type):
        ui_type = _type.__name__
    elif isinstance(_type, tuple):
        # Most commonly lists subclasses. Most commonly lists subclasses of strings
        if all((issubclass(x, string_types) for x in _type)):
            ui_type = 'basestring'
        elif all((issubclass(x, integer_types) for x in _type)):
            ui_type = 'int'
        elif all((issubclass(x, float) for x in _type)):
            ui_type = 'float'
        elif all((issubclass(x, Sequence) for x in _type)):
            ui_type = 'list'
    else:
        ui_type = get_ui_type_from_field_interface(field)

    if ui_type in ('unicode', 'str', 'basestring'):
        # These are all 'string' type

        # Can we be more specific?
        ui_type = get_ui_type_from_field_interface(field)
        if ui_type and ui_type not in ('TextLine', 'Text'): # pragma: no cover
            # Yes we can
            ui_base_type = 'string'
        else:
            ui_type = 'string'
            ui_base_type = 'string'
    elif ui_type in ('Sequence', 'MutableSequence'):
        ui_type = 'list'
    elif ui_type in ('Mapping', 'MutableMapping'):
        ui_type = 'dict'
    elif ui_type in ('Number', 'float', 'Decimal', 'Complex', 'Real', 'Rational'):
        ui_base_type = 'float'
    elif ui_type in ('int', 'long', 'Integral'):
        ui_base_type = 'int'
    elif ui_type in ('bool',):
        ui_base_type = 'bool'
    return ui_type, ui_base_type

_ui_type_from_field = ui_type_from_field = get_ui_types_from_field # BWC

def get_data_from_choice_field(v, base_type=None):
    # Vocabulary could be a name or the vocabulary itself
    choices = ()
    vocabulary = None
    if sch_interfaces.IVocabulary.providedBy(v.vocabulary): # pragma: no cover
        vocabulary = v.vocabulary
    elif isinstance(v.vocabularyName, string_types):
        name = v.vocabularyName
        vocabulary = sch_vocabulary.getVocabularyRegistry().get(None, name)

    if vocabulary is not None:
        choices = []
        tokens = []
        for term in vocabulary:
            # For BWC, we do different things depending on whether
            # there is a title or not
            if getattr(term, 'title', None):
                try:
                    # like nti.externalization, but without the dependency
                    choice = term.toExternalObject()
                except AttributeError: # pragma: no cover
                    choice = {
                        'token': term.token,
                        'value': term.value,
                        'title': term.title
                    }

                choices.append(choice)
            else: # pragma: no cover
                choices.append(term.token)  # bare; ideally this would go away
            tokens.append(term.token)

        # common case, these will all be the same type
        if  not base_type \
            and all((isinstance(x, string_types) for x in tokens)):
            base_type = 'string'
    return choices, base_type
_process_choice_field = process_choice_field = get_data_from_choice_field


class JsonSchemafier(object):

    def __init__(self, schema, readonly_override=None, context=None):
        """
        Create a new schemafier.

        :param schema: The zope schema (interface) to use.
        :param bool readonly_override: If given, a boolean value that will replace all
            readonly values in the schema.
        :param context: The context passed to :func:`zope.i18n.translate`
        """
        self.schema = schema
        self.readonly_override = readonly_override
        self.context = context

    def _iter_names_and_descriptions(self):
        """
        Return an iterable across the names and descriptions of the schema.

        Subclass hook to change what is considered.
        """
        return self.schema.namesAndDescriptions(all=True)

    def allow_field(self, name, field):
        """
        Return if the field is allowed in the external schema.

        By default, this checks to see if the field has a true value for the
        tag `TAG_HIDDEN_IN_UI`, or if the field's name starts with an underscore.

        .. versionchanged:: 1.12.0
           This will now be called for nested fields, such as the ``value_type`` or
           ``key_type`` of collections and mappings. In those cases, commonly the name will
           be the empty string.
        """
        if field.queryTaggedValue(TAG_HIDDEN_IN_UI) or name.startswith('_'):
            return False
        return True

    def get_ui_types_from_field(self, field):
        """
        Return the type and base type for the specified field
        """
        return get_ui_types_from_field(field)
    ui_types_from_field = get_ui_types_from_field # BWC

    def get_data_from_choice_field(self, field, base_type=None):
        """
        Return the choices and base type for the specified field
        """
        return get_data_from_choice_field(field, base_type)
    process_choice_field = get_data_from_choice_field # BWC

    def post_process_field(self, name, field, item_schema):
        pass

    def bind(self, schema):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.schema = schema
        return clone

    def make_schema(self):
        """
        Create the JSON schema.

        Individual fields of the schema will be checked and returned. See the various
        ``TAG`` constants for ways that the schema externalization can be influenced.

        :return: A dictionary consisting of dictionaries, one for each field. All the keys
            are strings and the values are strings, bools, numbers, or lists of primitives.
            Will be suitable for writing to JSON.
        """
        ext_schema = {}
        for k, v in self._iter_names_and_descriptions():
            __traceback_info__ = k, v
            if IMethod.providedBy(v):
                continue
            # v could be a schema field or an interface.Attribute
            if not self.allow_field(k, v):
                # If we disallow at the top level, we don't even
                # hint to its existence.
                continue

            item_schema = self._make_field_schema(v, k)

            self.post_process_field(k, v, item_schema)
            ext_schema[k] = item_schema

        return ext_schema

    def _translate(self, text):
        return translate(text, context=self.context)

    def _make_field_schema(self, field, name=None):
        name = name or field.__name__ or ''
        if not self.allow_field(name, field):
            # Disallowed, but we're already expecting a return value to put
            # in a dictionary.
            return None

        required = getattr(field, 'required', None)
        required = field.queryTaggedValue(TAG_REQUIRED_IN_UI) or required
        readonly_override = self.readonly_override
        if readonly_override is not None:
            readonly = readonly_override
        else:
            readonly = getattr(field, 'readonly', False)
            readonly = field.queryTaggedValue(TAG_READONLY_IN_UI) or readonly

        ui_base_type = None
        item_schema = {
            'name': name,
            'required': required,
            'readonly': readonly,
        }

        ui_type = field.queryTaggedValue(TAG_UI_TYPE)
        if not ui_type:
            ui_type, ui_base_type = self.get_ui_types_from_field(field)
        else:
            _, ui_base_type = self.get_ui_types_from_field(field)

        item_schema['type'] = ui_type
        item_schema['base_type'] = ui_base_type

        # Now add supplemental information about nested data.

        # Note that we're consistent to always provide *something*
        # for these optional keys, if they are expected to be there based on the
        # type of the field, it just may be None if it was excluded (or empty,
        # if all variants were excluded).

        if sch_interfaces.IChoice.providedBy(field):
            choices, base_type = self.get_data_from_choice_field(field, ui_base_type)
            item_schema['choices'] = choices
            item_schema['base_type'] = base_type

        if IVariant.providedBy(field):
            # 'fields' is not actually declared in the IVariant
            # interface; that's ok, we couldn't handle it automatically anyway.
            item_schema['value_type_options'] = [
                self._make_field_schema(the_field)
                for the_field
                in field.fields
                if self.allow_field(the_field.__name__, the_field)
            ]

        application_info = field.queryTaggedValue(TAG_APPLICATION_INFO) or {}
        item_schema['application_info'] = {
            k: self._translate(v) if isinstance(v, text_type) else copy(v)
            for k, v in application_info.items()
        }

        self._fill_field_values(item_schema, field)

        return item_schema

    def _fill_field_values(self, item_schema, field,
                           # Certain things from IField that we exclude
                           # because they are not useful externally or may
                           # expose sensitive information. `validate_invariants`
                           # is from the Object field.
                           # TODO: What if we tagged these values on import with TAG_HIDDEN_IN_UI
                           # and checked for that here?
                           _excluded=('missing_value', 'default', 'validate_invariants'),
                           # For safety, we'll refuse to output a value we don't understand.
                           # We expect dicts to have come from us, creating schemas.
                           _allowed_value_types=string_types + (Number, type(None), dict)):
        derived_field_iface = find_most_derived_interface(field, sch_interfaces.IField)
        if not derived_field_iface or derived_field_iface is sch_interfaces.IField:
            return

        # Take anything it has as a primitive, query it, and put it in the schema.
        for name, field_field in derived_field_iface.namesAndDescriptions(all=True):
            if name in item_schema or name in _excluded:
                # Cheap test first: if we've already got it, ignore it
                continue
            if not sch_interfaces.IField.providedBy(field_field):
                continue

            # A few things we handle specially.
            value = field_field.query(field)
            if sch_interfaces.IField.providedBy(value):
                # It is another field, yay, like value_type or key_type,
                # so we need to recurse
                value = self._make_field_schema(value)
            elif IInterface.providedBy(value):
                schemafier = self.bind(value)
                value = schemafier.make_schema()
            elif isinstance(value, text_type):
                value = self._translate(value)

            if not isinstance(value, _allowed_value_types):
                continue # pragma: no cover
            item_schema[name] = value
