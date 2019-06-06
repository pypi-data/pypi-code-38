# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import unicode_literals
from abc import ABCMeta, abstractproperty
from collections import namedtuple
try:
    from collections.abc import MutableMapping, MutableSequence, Mapping, Sequence
except ImportError:
    from collections import MutableMapping, MutableSequence, Mapping, Sequence
import fnmatch
import keyword
import re
import textwrap
from functools import update_wrapper

from . import exceptions
from .datatypes import convert_from, convert_to
from .constants import TYPE_HINTS
from .utils import mixedproperty, pythonize_attribute_name
import six


def caching(func):
    """
    This decorator caches the value in self._cache to avoid data to be
    retrieved multiple times. This works for properties or functions without
    arguments.
    """
    name = func.__name__

    def wrapper(self):
        # We use self._cache here, in the decorator _cache will be a member of
        #  the objects, so nothing to worry about
        # pylint: disable=protected-access
        if not self.caching or name not in self._cache:
            # Compute the value if not cached
            self._cache[name] = func(self)

        return self._cache[name]

    update_wrapper(wrapper, func)
    return wrapper


class VariableMap(MutableMapping):
    def __init__(self, parent, field):
        self._cache = {}
        self.caching = True
        self.parent = parent
        self._field = field

    def __repr__(self):
        return "<VariableMap {}>".format(dict(self))

    @property
    @caching
    def data(self):
        try:
            variables = next(x for x in self.parent.fulldata['children'] if x['field'] == self.field)
            variables_map = {x['data_fields']['name']: x['data_fields']['field'] for x in variables['items'] if 'field' in x['data_fields']}
        except StopIteration:
            variables_map = {}

        return variables_map

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        query = {'xsiType': self.parent.__xsi_type__,
                 '{parent_type_}/{field}[@xsi_type={type}]/{key}'.format(parent_type_=self.parent.__xsi_type__,
                                                                         field=self.field,
                                                                         type=self.parent.__xsi_type__,
                                                                         key=key): value}
        self.xnat.put(self.parent.fulluri, query=query)

        # Remove cache and make sure the reload the data
        if 'data' in self._cache:
            self.clearcache()

    def __delitem__(self, key):
        self.parent.logger.warning('Deleting of variables is currently not supported!')

    def __iter__(self):
        for key in self.data.keys():
            yield key

    def __len__(self):
        return len(self.data)

    @property
    def field(self):
        return self._field

    @property
    def xnat(self):
        return self.parent.xnat_session

    def clearcache(self):
        self._cache.clear()
        self.parent.clearcache()


class CustomVariableMap(VariableMap):
    def __setitem__(self, key, value):
        query = {'xsiType': self.parent.__xsi_type__,
                 '{type_}/fields/field[name={key}]/field'.format(type_=self.parent.__xsi_type__,
                                                                 key=key): value}
        self.xnat.put(self.parent.fulluri, query=query)

        # Remove cache and make sure the reload the data
        if 'data' in self._cache:
            self.clearcache()


@six.python_2_unicode_compatible
class XNATBaseObject(six.with_metaclass(ABCMeta, object)):
    SECONDARY_LOOKUP_FIELD = None
    _DISPLAY_IDENTIFIER = None
    _HAS_FIELDS = False
    _CONTAINED_IN = None
    _XSI_TYPE = 'xnat:baseObject'

    def __init__(self, uri=None, xnat_session=None, id_=None, datafields=None, parent=None, fieldname=None, overwrites=None, **kwargs):
        if (uri is None or xnat_session is None) and parent is None:
            raise exceptions.XNATValueError('Either the uri and xnat session have to be given, or the parent object')

        # Set the xnat session
        self._cache = {}
        self._caching = None

        # This is the object creation branch
        if uri is None and parent is not None:
            # This is the creation of a new object in the XNAT server
            self._xnat_session = parent.xnat_session
            if isinstance(parent, XNATListing):
                pass
            elif self._CONTAINED_IN is not None:
                parent = getattr(parent, self._CONTAINED_IN)
            else:
                self.logger.debug('parent {}, self._CONTAINED_IN: {}'.format(parent, self._CONTAINED_IN))
                raise exceptions.XNATValueError('Cannot determine PUT url!')

            # Check what argument to use to build the URL
            if self._DISPLAY_IDENTIFIER is not None:
                url_part_argument = pythonize_attribute_name(self._DISPLAY_IDENTIFIER)
            elif self.SECONDARY_LOOKUP_FIELD is not None:
                url_part_argument = self.SECONDARY_LOOKUP_FIELD
            else:
                raise exceptions.XNATValueError('Cannot figure out correct object creation url for <{}>, '
                                                'creation currently not supported!'.format(type(self).__name__))

            # Get extra required url part
            url_part = kwargs.get(url_part_argument)

            if url_part is not None:
                uri = '{}/{}'.format(parent.uri, url_part)
                self.logger.debug('PUT URI: {}'.format(uri))
                query = {
                    'xsiType': self.__xsi_type__,
                    'req_format': 'qs',
                }

                # Add all kwargs to query
                query.update(kwargs)

                self.logger.debug('query: {}'.format(query))
                self.xnat_session.put(uri, query=query)
            else:
                raise exceptions.XNATValueError('The {} for a {} need to be specified on creation'.format(
                    url_part_argument,
                    self.__xsi_type__
                ))

            # Clear parent cache
            parent.clearcache()

            # Parent is no longer needed after creation
            self._uri = uri
            self._parent = None
        else:
            # This is the creation of a Python proxy for an existing XNAT object
            self._uri = uri
            self._parent = parent

        self._xnat_session = xnat_session
        self._fieldname = fieldname

        if self._HAS_FIELDS:
            self._fields = CustomVariableMap(self, field='fields/field')
        else:
            self._fields = None

        if id_ is not None:
            self._cache['id'] = id_

        if datafields is not None:
            self._cache['data'] = datafields

        self._overwrites = overwrites or {}
        self._overwrites.update(kwargs)

    def __str__(self):
        if self.SECONDARY_LOOKUP_FIELD is None:
            return six.text_type('<{} {}>').format(self.__class__.__name__, self.id)
        else:
            return six.text_type('<{} {} ({})>').format(self.__class__.__name__,
                                                        getattr(self, self.SECONDARY_LOOKUP_FIELD),
                                                        self.id)

    def __repr__(self):
        return str(self)

    @abstractproperty
    def xpath(self):
        """
        The xpath of the object as seen from the root of the data. Used for
        setting fields in the object.
        """

    @property
    def parent(self):
        return self._parent

    @property
    def logger(self):
        return self.xnat_session.logger

    @property
    def fieldname(self):
        return self._fieldname

    def get(self, name, type_=None):
        try:
            value = self._overwrites[name]
        except KeyError:
            value = self.data.get(name)

        if type_ is not None and value is not None:
            if isinstance(type_, six.string_types):
                value = convert_to(value, type_)
            else:
                value = type_(value)
        return value

    def get_object(self, fieldname, type_=None):
        try:
            data = next(x for x in self.fulldata.get('children', []) if x['field'] == fieldname)['items']
            data = next(x for x in data if not x['meta']['isHistory'])  # Filter out the non-history item
            type_ = data['meta']['xsi:type']
        except StopIteration:
            if type_ is None:
                type_ = TYPE_HINTS.get(fieldname, None)

        if type_ is None:
            raise exceptions.XNATValueError('Cannot determine type of field {}!'.format(fieldname))

        cls = self.xnat_session.XNAT_CLASS_LOOKUP[type_]

        if not issubclass(cls, (XNATSubObject, XNATNestedObject)):
            raise ValueError('{} is not a subobject type!'.format(cls))

        return self.xnat_session.create_object(self.uri, type_=type_, parent=self, fieldname=fieldname)

    @property
    def fulluri(self):
        return self.uri

    def external_uri(self, query=None, scheme=None):
        """
        Return the external url for this object, not just a REST path

        :param query: extra query string parameters
        :param scheme: scheme to use (when not using original url scheme)
        :return: external url for this object
        """
        return self.xnat_session.url_for(self, query=query, scheme=scheme)

    def mset(self, values=None, timeout=None, **kwargs):
        if not isinstance(values, dict):
            values = kwargs

        if self.parent is not None:
            xsi_type = self.parent.__xsi_type__
        else:
            xsi_type = self.__xsi_type__

        # Add xpaths to query
        query = {'xsiType': xsi_type}
        for name, value in values.items():
            xpath = '{}/{}'.format(self.xpath, name)
            query[xpath] = value

        self.xnat_session.put(self.fulluri, query=query, timeout=timeout)
        self.clearcache()
        if hasattr(self.parent, 'clearcache'):
            self.parent.clearcache()

    def set(self, name, value, type_=None, timeout=None):
        """
        Set a field in the current object

        :param str name: name of the field
        :param value:  value to set
        :param type_: type of the field
        """
        if type_ is not None:
            if isinstance(type_, six.string_types):
                # Make sure we have a valid string here that is properly casted
                value = convert_from(value, type_)
            else:
                value = type_(value)

        self.mset({name: value}, timeout=timeout)

    def del_(self, name):
        self.mset({name: 'NULL'})

    @mixedproperty
    def __xsi_type__(self):
        return self._XSI_TYPE

    @property
    @caching
    def id(self):
        if 'ID' in self.data:
            return self.data['ID']
        elif self.parent is not None:
            return '{}/{}'.format(self.parent.id, self.fieldname)
        elif hasattr(self, '_DISPLAY_IDENTIFIER') and self._DISPLAY_IDENTIFIER is not None:
            return getattr(self, self._DISPLAY_IDENTIFIER)
        else:
            return '#NOID#'

    @abstractproperty
    def data(self):
        """
        The data of the current object (data fields only)
        """

    @abstractproperty
    def fulldata(self):
        """
        The full data of the current object (incl children, meta etc)
        """

    @property
    def xnat_session(self):
        return self._xnat_session

    @property
    def uri(self):
        return self._uri

    def clearcache(self):
        self._overwrites.clear()
        self._cache.clear()

    # This needs to be at the end of the class because it shadows the caching
    # decorator for the remainder of the scope.
    @property
    def caching(self):
        if self._caching is not None:
            return self._caching
        else:
            return self.xnat_session.caching

    @caching.setter
    def caching(self, value):
        self._caching = value

    @caching.deleter
    def caching(self):
        self._caching = None

    def delete(self, remove_files=True):
        """
        Remove the item from XNATSession
        """
        query = {}

        if remove_files:
            query['removeFiles'] = 'true'

        self.xnat_session.delete(self.fulluri, query=query)

        # Make sure there is no cache, this will cause 404 erros on subsequent use
        # of this object, indicating that is has been in fact removed
        self.clearcache()


class XNATObject(XNATBaseObject):
    @property
    @caching
    def fulldata(self):
        return next(x for x in self.xnat_session.get_json(self.uri)['items'] if not x['meta']['isHistory'])

    @property
    def data(self):
        return self.fulldata['data_fields']

    @property
    def xpath(self):
        return '{}'.format(self.__xsi_type__)


class XNATNestedObject(XNATBaseObject):
    @property
    def fulldata(self):
        try:
            if isinstance(self.parent.fulldata, dict):
                data = next(x for x in self.parent.fulldata['children'] if x['field'] == self.fieldname)['items']
                data = next(x for x in data if not x['meta']['isHistory'])
            elif isinstance(self.parent.fulldata, list):
                if self.parent.secondary_lookup_field is not None:
                    data = next(x for x in self.parent.fulldata if x['data_fields'][self.parent.secondary_lookup_field] == self.fieldname)
                else:
                    # Just simply select the index
                    data = self.parent.fulldata[self.fieldname]
            else:
                raise ValueError("Found unexpected data in parent! ({})".format(self.parent.fulldata))

        except StopIteration:
            data = {'data_fields': {}}

        return data

    @property
    def data(self):
        return self.fulldata['data_fields']

    @property
    def uri(self):
        return self.parent.uri

    @property
    def xpath(self):
        if isinstance(self.parent, XNATBaseObject):
            return '{}/{}[@xsi:type={}]'.format(self.parent.xpath,
                                                self.fieldname,
                                                self.__xsi_type__)
        else:
            return '{}[{}={}]'.format(self.parent.xpath,
                                      self.parent.secondary_lookup_field,
                                      self.fieldname)

    def clearcache(self):
        super(XNATNestedObject, self).clearcache()
        self.parent.clearcache()


class XNATSubObject(XNATBaseObject):
    _PARENT_CLASS = None

    @property
    def uri(self):
        return self.parent.fulluri

    @property
    def __xsi_type__(self):
        return self.parent.__xsi_type__

    @property
    def xpath(self):
        if isinstance(self.parent, XNATBaseObject):
            # XPath is this plus fieldname
            return '{}/{}'.format(self.parent.xpath, self.fieldname)
        elif isinstance(self.parent, XNATBaseListing):
            # XPath is an index in a list
            if isinstance(self.fieldname, int):
                return '{}[{}]'.format(self.parent.xpath,
                                       self.fieldname)
            else:
                return '{}[{}={}]'.format(self.parent.xpath,
                                          self.parent.secondary_lookup_field,
                                          self.fieldname)
        else:
            raise TypeError('Type of parent is invalid! (Found {})'.format(type(self.parent).__name__))

    @property
    def fulldata(self):
        prefix = '{}/'.format(self.fieldname)

        result = self.parent.fulldata

        if isinstance(result, dict):
            result = {k[len(prefix):]: v for k, v in result['data_fields'].items() if k.startswith(prefix)}
            result = {'data_fields': result}
        elif isinstance(result, list):
            try:
                if self.parent.secondary_lookup_field is not None:
                    result = next(x for x in result if x['data_fields'][self.parent.secondary_lookup_field] == self.fieldname)
                else:
                    result = result[self.fieldname]
            except (IndexError, KeyError):
                return {'data_fields': {}}
        else:
            raise ValueError("Found unexpected data in parent! ({})".format(result))

        return result

    @property
    def data(self):
        return self.fulldata['data_fields']

    def clearcache(self):
        super(XNATSubObject, self).clearcache()
        self.parent.clearcache()


@six.python_2_unicode_compatible
class XNATBaseListing(Mapping, Sequence):
    def __init__(self, parent, field_name, secondary_lookup_field=None, xsi_type=None, **kwargs):
        # Cache fields
        self._cache = {}
        self.caching = True

        # Save the parent and field name
        self.parent = parent
        self.field_name = field_name

        # Copy parent xnat session for future use
        self._xnat_session = parent.xnat_session

        # Get the lookup field before type hints, they can ruin it for abstract types
        if secondary_lookup_field is None:
            if xsi_type is not None:
                secondary_lookup_field = self.xnat_session.XNAT_CLASS_LOOKUP.get(xsi_type).SECONDARY_LOOKUP_FIELD

        # Make it possible to override the xsi_type for the contents
        if self.field_name not in TYPE_HINTS:
            self._xsi_type = xsi_type
        else:
            self._xsi_type = TYPE_HINTS[field_name]

        # If Needed, try again
        if secondary_lookup_field is None:
            secondary_lookup_field = self.xnat_session.XNAT_CLASS_LOOKUP.get(self._xsi_type).SECONDARY_LOOKUP_FIELD

        self.secondary_lookup_field = secondary_lookup_field

    def sanitize_name(self, name):
        name = re.sub('[^0-9a-zA-Z]+', '_', name)

        # Change CamelCaseString to camel_case_string
        # Note that addID would become add_id
        name = re.sub("[A-Z]+", lambda x: '_' + x.group(0).lower(), name)
        if name[0] == '_':
            name = name[1:]

        # Avoid multiple underscores (replace them by single underscore)
        name = re.sub("__+", '_', name)

        # Avoid overwriting keywords TODO: Do we want this, as a property it is not a huge problem?
        if keyword.iskeyword(name):
            name += '_'

        return name

    @property
    def xnat_session(self):
        return self._xnat_session

    @abstractproperty
    def data_maps(self):
        """
        The generator function (should be cached) of all the data access
        properties. They are all generated from the same data, so their
        caching is shared.
        """

    @property
    def data(self):
        """
        The data mapping using the primary key
        """
        return self.data_maps[0]

    @property
    def key_map(self):
        """
        The data mapping using the secondary key
        """
        return self.data_maps[1]

    @property
    def non_unique_keys(self):
        """
        Set of non_unique keys
        """
        return self.data_maps[2]

    @property
    def listing(self):
        """
        The listing view of the data
        """
        return self.data_maps[3]

    @abstractproperty
    def xnat_session(self):
        pass

    def __str__(self):
        if self.secondary_lookup_field is not None:
            content = ', '.join('({}, {}): {}'.format(k, getattr(v, self.sanitize_name(self.secondary_lookup_field)), v) for k, v in self.items())
            content = '{{{}}}'.format(content)
        else:
            content = ', '.join(str(v) for v in self.values())
            content = '[{}]'.format(content)
        return '<{} {}>'.format(type(self).__name__, content)

    def __repr__(self):
        return str(self)

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self.listing[item]

        try:
            return self.data[item]
        except KeyError:
            try:
                if item in self.non_unique_keys:
                    raise KeyError('There are multiple items with that key in'
                                   ' this collection! To avoid problem you need'
                                   ' to use the ID.')
                return self.key_map[item]
            except KeyError:
                raise KeyError('Could not find ID/label {} in collection!'.format(item))

    def __iter__(self):
        for index, item in enumerate(self.listing):
            if hasattr(item, 'id') and item.id in self.data:
                yield item.id
            elif self.secondary_lookup_field is not None and hasattr(item, self.secondary_lookup_field):
                yield getattr(item, self.secondary_lookup_field)
            else:
                yield index

    def __len__(self):
        return len(self.listing)

    @property
    def uri(self):
        return self._uri

    @property
    def xnat_session(self):
        return self._xnat_session

    def clearcache(self):
        self.parent.clearcache()
        self._cache.clear()


class XNATListing(XNATBaseListing):
    def __init__(self, uri, filter=None, **kwargs):
        # Important for communication, needed before superclass is called
        self._uri = uri

        super(XNATListing, self).__init__(**kwargs)

        # Manager the filters
        self._used_filters = filter or {}

    @property
    @caching
    def data_maps(self):
        columns = 'ID,URI'
        if self.secondary_lookup_field is not None:
            columns = '{},{}'.format(columns, self.secondary_lookup_field)
        if self._xsi_type is None:
            columns += ',xsiType'

        query = dict(self.used_filters)
        query['columns'] = columns
        result = self.xnat_session.get_json(self.uri, query=query)

        try:
            result = result['ResultSet']['Result']
        except KeyError:
            raise exceptions.XNATValueError('Query GET from {} returned invalid data: {}'.format(self.uri, result))

        for entry in result:
            if 'URI' not in entry and 'ID' not in entry:
                # HACK: This is a Resource, that misses the URI and ID field (let's fix that)
                entry['ID'] = entry['xnat_abstractresource_id']
                entry['URI'] = '{}/{}'.format(self.uri, entry['xnat_abstractresource_id'])
            elif 'ID' not in entry:
                # HACK: This is a File and it misses an ID field and has Name (let's fix that)
                entry['ID'] = entry['Name']
                entry['fieldname'] = type(self.parent).__name__
                if entry['URI'].startswith(self.parent.uri):
                    entry['path'] = entry['URI'].replace(self.parent.uri, '', 1)
                else:
                    entry['path'] = re.sub(r'^.*/resources/{}/files/'.format(self.parent.id), '', entry['URI'], 1)
            else:
                entry['URI'] = '{}/{}'.format(self.uri, entry['ID'])

        # Post filter result if server side query did not work
        if self.used_filters:
            result = [x for x in result if all(fnmatch.fnmatch(x[k], v) for k, v in self.used_filters.items() if k in x)]

        # Create object dictionaries
        id_map = {}
        key_map = {}
        listing = []
        non_unique = {None}
        for x in result:
            # HACK: xsi_type of resources is called element_name... yay!
            if self.secondary_lookup_field is not None:
                secondary_lookup_value = x.get(self.secondary_lookup_field)
                new_object = self.xnat_session.create_object(x['URI'],
                                                             type_=x.get('xsiType', x.get('element_name', self._xsi_type)),
                                                             id_=x['ID'],
                                                             fieldname=x.get('fieldname'),
                                                             **{self.secondary_lookup_field: secondary_lookup_value})
                if secondary_lookup_value in key_map:
                    non_unique.add(secondary_lookup_value)
                key_map[secondary_lookup_value] = new_object
            else:
                new_object = self.xnat_session.create_object(x['URI'],
                                                             type_=x.get('xsiType', x.get('element_name', self._xsi_type)),
                                                             id_=x['ID'],
                                                             fieldname=x.get('fieldname'))

            listing.append(new_object)
            id_map[x['ID']] = new_object

        return id_map, key_map, non_unique, listing

    def tabulate(self, columns=None, filter=None):
        """
        Create a table (tuple of namedtuples) from this listing. It is possible
        to choose the columns and add a filter to the tabulation.

        :param tuple columns: names of the variables to use for columns
        :param dict filter: update filters to use (form of {'variable': 'filter*'}),
                             setting this option will try to merge the filters and
                             throw an error if that is not possible.
        :return: tabulated data
        :rtype: tuple
        :raises ValueError: if the new filters conflict with the object filters
        """
        if columns is None:
            columns = ('DEFAULT',)

        if filter is None:
            filter = self.used_filters
        else:
            filter = self.merge_filters(self.used_filters, filter)

        query = dict(filter)
        query['columns'] = ','.join(columns)

        result = self.xnat_session.get_json(self.uri, query=query)
        if len(result['ResultSet']['Result']) > 0:
            result_columns = list(result['ResultSet']['Result'][0].keys())

            # Retain requested order
            if columns != ('DEFAULT',):
                result_columns = [x for x in columns if x in result_columns]

            # Replace all non-alphanumeric characters with an underscore
            result_columns = {s: re.sub('[^0-9a-zA-Z]+', '_', s) for s in result_columns}
            rowtype = namedtuple('TableRow', list(result_columns.values()))

            # Replace all non-alphanumeric characters in each key of the keyword dictionary
            return tuple(rowtype(**{result_columns[k]: v for k, v in x.items() if k in result_columns}) for x in result['ResultSet']['Result'])
        else:
            return ()

    @property
    def used_filters(self):
        return self._used_filters

    @staticmethod
    def merge_filters(old_filters, extra_filters):
        # First check for conflicting filters
        for key in extra_filters:
            if key in old_filters and old_filters[key] != extra_filters[key]:
                raise ValueError('Trying to redefine filter {key}={oldval} to {key}={newval}'.format(key=key,
                                                                                                     oldval=old_filters[key],
                                                                                                     newval=extra_filters[key]))

        new_filters = dict(old_filters)
        new_filters.update(extra_filters)

        return new_filters

    def filter(self, filters=None, **kwargs):
        """
        Create a new filtered listing based on this listing. There are two way
        of defining the new filters. Either by passing a dict as the first
        argument, or by adding filters as keyword arguments.

        For example::
          >>> listing.filter({'ID': 'A*'})
          >>> listing.filter(ID='A*')

        are equivalent.

        :param dict filters: a dictionary containing the filters
        :param str kwargs: keyword arguments containing the filters
        :return: new filtered XNATListing
        :rtype: XNATListing
        """
        if filters is None:
            filters = kwargs

        new_filters = self.merge_filters(self.used_filters, filters)
        return XNATListing(uri=self.uri,
                           xnat_session=self.xnat_session,
                           parent=self.parent,
                           field_name=self.field_name,
                           secondary_lookup_field=self.secondary_lookup_field,
                           xsi_type=self._xsi_type,
                           filter=new_filters)


class XNATSimpleListing(XNATBaseListing, MutableMapping, MutableSequence):
    def __str__(self):
        if self.secondary_lookup_field is not None:
            content = ', '.join('{!r}: {!r}'.format(key, value) for key, value in self.items())
            content = '{{{}}}'.format(content)
        else:
            content = ', '.join(repr(v) for v in self.values())
            content = '[{}]'.format(content)
        return '<{} {}>'.format(type(self).__name__, content)

    def __iter__(self):
        for key in self.key_map:
            yield key

    @property
    def xnat_session(self):
        return self.parent.xnat_session

    @property
    def fulldata(self):
        for child in self.parent.fulldata['children']:
            if child['field'] == self.field_name:
                return child['items']
        return []

    @property
    @caching
    def data_maps(self):
        id_map = {}
        key_map = {}
        listing = []
        non_unique_keys = set()

        for index, element in enumerate(self.fulldata):
            if self.secondary_lookup_field is not None:
                key = element['data_fields'][self.secondary_lookup_field]
            else:
                key = index

            try:
                value = element['data_fields'][self.field_name.split('/')[-1]]
            except KeyError:
                continue

            if key in key_map:
                non_unique_keys.add(key)
                key_map[key] = None
            elif self.secondary_lookup_field is not None:
                key_map[key] = value

            listing.append(value)

        return id_map, key_map, non_unique_keys, listing

    def __setitem__(self, key, value):
        query = {'xsiType': self.parent.__xsi_type__,
                 '{type_}/{fieldname}[{lookup}={key}]/{fieldpart}'.format(type_=self.parent.__xsi_type__,
                                                                          fieldname=self.field_name,
                                                                          lookup=self.secondary_lookup_field,
                                                                          fieldpart=self.field_name.split('/')[-1],
                                                                          key=key): value}
        self.xnat_session.put(self.parent.fulluri, query=query)

        # Remove cache and make sure the reload the data
        self.clearcache()

    def __delitem__(self, key):
        query = {
            'xsiType': self.parent.__xsi_type__,
            '{type_}/{fieldname}[{lookup}={key}]/{fieldpart}'.format(type_=self.parent.__xsi_type__,
                                                                     fieldname=self.field_name,
                                                                     lookup=self.secondary_lookup_field,
                                                                     fieldpart=self.field_name.split('/')[-1],
                                                                     key=key): 'NULL',
            '{type_}/{fieldname}[{lookup}={key}]/{lookup}'.format(type_=self.parent.__xsi_type__,
                                                                  fieldname=self.field_name,
                                                                  lookup=self.secondary_lookup_field,
                                                                  key=key): 'NULL',
        }
        self.xnat_session.put(self.parent.fulluri, query=query)

        # Remove cache and make sure the reload the data
        self.clearcache()

    def insert(self, index, value):
        pass


class XNATSubListing(XNATBaseListing, MutableMapping, MutableSequence):
    def __getitem__(self, item):
        try:
            return super(XNATSubListing, self).__getitem__(item)
        except (IndexError, KeyError):
            cls = self.xnat_session.XNAT_CLASS_LOOKUP[self._xsi_type]
            object = cls(uri=self.parent.uri, id_=item, datafields={}, parent=self, fieldname=item)
            return object

    @property
    def xnat_session(self):
        return self.parent.xnat_session

    @property
    def fulldata(self):
        for child in self.parent.fulldata['children']:
            if child['field'] == self.field_name or child['field'].startswith(self.field_name + '/'):
                return child['items']
        return []

    @property
    def uri(self):
        return self.parent.fulluri

    @property
    def fulluri(self):
        return self.parent.fulluri

    @property
    @caching
    def data_maps(self):
        id_map = {}
        key_map = {}
        listing = []
        non_unique_keys = set()

        for index, element in enumerate(self.fulldata):
            if self.secondary_lookup_field is not None:
                key = element['data_fields'][self.secondary_lookup_field]
            else:
                key = index

            try:
                xsi_type = element['meta']['xsi:type']
            except KeyError:
                xsi_type = self._xsi_type

            # XNAT seems to like to sometimes give a non-defined XSI type back
            #  (e.g. 'xnat:fieldDefinitionGroup_field'), make sure the XNAT
            # reply contains a valid XSI
            if xsi_type not in self.xnat_session.XNAT_CLASS_LOOKUP:
                xsi_type = self._xsi_type

            cls = self.xnat_session.XNAT_CLASS_LOOKUP[xsi_type]
            object = cls(uri=self.parent.uri,
                         id_=key,
                         datafields=element['data_fields'],
                         parent=self,
                         fieldname=key)

            if key in key_map:
                non_unique_keys.add(key)
                key_map[key] = None
            elif self.secondary_lookup_field is not None:
                key_map[key] = object

            listing.append(object)

        return id_map, key_map, non_unique_keys, listing

    @property
    def __xsi_type__(self):
        return self._xsi_type

    @property
    def xpath(self):
        return '{}/{}'.format(self.parent.xpath, self.field_name)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        # Determine XPATH of item to remove
        if isinstance(key, int):
            xpath = '{}[{}]'.format(self.xpath,
                                   key)
        else:
            xpath = '{}[{}={}]'.format(self.xpath,
                                      self.secondary_lookup_field,
                                      key)

        # Get correct xsi type
        if self.parent is not None:
            xsi_type = self.parent.__xsi_type__
        else:
            xsi_type = self.__xsi_type__

        query = {
            'xsiType': xsi_type,
            xpath: 'NULL'
        }

        self.xnat_session.put(self.fulluri, query=query)
        self.clearcache()

    def insert(self, index, value):
        pass
