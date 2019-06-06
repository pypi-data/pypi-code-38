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
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod, abstractproperty
import collections
import contextlib
import inspect
import keyword
import os
import re
from xml.etree import ElementTree

from . import core
from . import xnatbases
from .datatypes import TYPE_TO_PYTHON
from .constants import SECONDARY_LOOKUP_FIELDS, FIELD_HINTS, CORE_REST_OBJECTS
from .utils import pythonize_class_name, pythonize_attribute_name, full_class_name


FILE_HEADER = '''
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
import os
import tempfile  # Needed by generated code
from gzip import GzipFile  # Needed by generated code
from tarfile import TarFile  # Needed by generated code
from zipfile import ZipFile  # Needed by generated code
from six import BytesIO  # Needed by generated code

from xnat import search
from xnat.core import XNATObject, XNATNestedObject, XNATSubObject, XNATListing, XNATSimpleListing, XNATSubListing, caching
from xnat.utils import mixedproperty, RequestsFileLike

try:
    PYDICOM_LOADED = True
    import pydicom
except ImportError:
    PYDICOM_LOADED = False


SESSION = None


def current_session():
    return SESSION


# These mixins are to set the xnat_session automatically in all created classes
class XNATObjectMixin(XNATObject):
    @mixedproperty
    def xnat_session(self):
        return current_session()

    @classmethod
    def query(cls, *constraints):
        query = search.Query(cls, cls.xnat_session)

        # Add in constraints immediatly
        if len(constraints) > 0:
            query = query.filter(*constraints)

        return query


class XNATNestedObjectMixin(XNATNestedObject):
    @mixedproperty
    def xnat_session(self):
        return current_session()


class XNATSubObjectMixin(XNATSubObject):
    @mixedproperty
    def xnat_session(self):
        return current_session()


class FileData(XNATObjectMixin):
    SECONDARY_LOOKUP_FIELD = "{file_secondary_lookup}"
    _XSI_TYPE = 'xnat:fileData'

    def __init__(self, uri=None, xnat_session=None, id_=None, datafields=None, parent=None, fieldname=None, overwrites=None, path=None):
        super(FileData, self).__init__(uri=uri,
                                       xnat_session=xnat_session,
                                       id_=id_,
                                       datafields=datafields,
                                       parent=parent,
                                       fieldname=fieldname,
                                       overwrites=overwrites)

        if path is not None:
            self._path = path

    @property
    def path(self):
        return self._path

    def delete(self):
        self.xnat_session.delete(self.uri)

    def download(self, *args, **kwargs):
        self.xnat_session.download(self.uri, *args, **kwargs)

    def download_stream(self, *args, **kwargs):
        self.xnat_session.download_stream(self.uri, *args, **kwargs)
        
    def open(self):
        uri = self.xnat_session._format_uri(self.uri)
        request = self.xnat_session.interface.get(uri, stream=True)
        return RequestsFileLike(request)

    @property
    @caching
    def size(self):
        response = self.xnat_session.head(self.uri, allow_redirects=True)
        return response.headers['Content-Length']


# Empty class lookup to place all new lookup values
XNAT_CLASS_LOOKUP = {{
    "xnat:fileData": FileData,
}}


# The following code represents the data structure of the XNAT server
# It is automatically generated using
{schemas}


'''

# TODO: Add more fields to FileData from [Name, Size, URI, cat_ID, collection, file_content, file_format, tile_tags]?
# TODO: Add display identifiers support (DONE?)
# <xs:annotation>
# <xs:appinfo>
# <xdat:element displayIdentifiers="label"/>
# </xs:appinfo>
# <xs:documentation>An individual person involved in experimental research</xs:documentation>
# </xs:annotation>
# <xs:sequence>
# TODO: Add XPATHs for setting SubObjects (SEMI-DONE)
# TODO: Make Listings without key and with numeric index possible (inProgress)
# TODO: Fix scan parameters https://groups.google.com/forum/#!topic/xnat_discussion/GBZoamC2ZmY
# TODO: Check the nesting weirdness in petScanDataParametersFramesFrames (DONE?)
# TODO: Figure out the object/subobject/semi-subobject mess.
# TODO: Move all system function to use a __ prefix


class ClassPrototype(object):
    def __init__(self, parser, name, logger, field_name=None, parent_class=None, simple=False):
        self.parser = parser
        self.name = name  # This is the XSI type
        self.logger = logger

        self.field_name = field_name
        self.parent_class = parent_class
        self.parent_property = None

        self.attributes = collections.OrderedDict()
        self.base_class = None
        self.display_identifier = None
        self.abstract = False
        self._simple = simple

        self._writer = None
        self.source_schema = self.parser.current_schema

    def __repr__(self):
        return "<ClassPrototype {}>".format(self.name)

    def root_base_class(self, topxsd=False):
        base = self.base_class
        if self.base_class is None:
            return self.name

        while not base.startswith('XNAT'):
            try:
                cls = self.parser.class_list[base]
            except KeyError:
                self.logger.debug('Class list: {}'.format(
                    self.parser.class_list.keys())
                )
                raise

            if cls.base_class is None:
                return base

            if topxsd and cls.base_class.startswith('XNAT'):
                return base

            base = cls.base_class

        return base

    @property
    def simple(self):
        root_base = self.root_base_class(topxsd=True)
        root_base = self.parser.class_list.get(root_base, self)
        if root_base is self:
            return self._simple
        else:
            return root_base.simple

    @property
    def class_type(self):
        if self.simple:
            return 'Simple'
        if self.field_name is not None:
            return 'SubObject'
        elif self.name in CORE_REST_OBJECTS:
            return 'Object'
        else:
            if self.base_class is not None:
                root_base = self.root_base_class(topxsd=True)
                return self.parser.class_list[root_base].class_type
            else:
                return 'NestedObject'

    @property
    def writer(self):
        if self._writer is None:
            writers = {
                'Object': ObjectClassWriter,
                'SubObject': SubObjectClassWriter,
                'NestedObject': NestedObjectClassWriter,
                'Simple': SimpleClassWriter,
            }

            self._writer = writers[self.class_type](self)

        return self._writer

    def tostring(self):
        """
        Generate a string of the code for this class. We do this by finding the
        appropriate writer (depending on the type of class we are generating)
        and then delegating the actual generation to the writer.
        """
        return self.writer.tostring()


class AttributePrototype(object):
    def __init__(self, parser, name, logger, type=None, parent_class=None, parent_property=None,
                 min_occur=None, max_occur=None):
        self.parser = parser
        self.name = name
        self.logger = logger
        self.type = type
        self.parent_class = parent_class
        self.parent_property = parent_property
        self.field_name = None

        # Set initial values for possible additions
        self.restrictions = collections.OrderedDict()
        self.element_class = None
        self.min_occur = min_occur
        self.max_occur = max_occur
        self.docstring = None
        self.display_identifier = None

        self._writer = None

    @property
    def clean_name(self):
        return pythonize_attribute_name(self.name)

    @property
    def property_type(self):
        if self.max_occur is not None and (self.max_occur == 'unbounded' or int(self.max_occur) > 1):
            return 'listing'
        if isinstance(self.type, str):
            if self.type.startswith('xs:'):
                return 'property'
            else:
                return 'subobject'
        else:
            return 'subobject'

    @property
    def writer(self):
        if self._writer is None:
            writers = {
                'constant': ConstantWriter,
                'listing': ListingPropertyWriter,
                'property': PropertyWriter,
                'subobject': SubObjectPropertyWriter,
            }

            self._writer = writers[self.property_type](self)

        return self._writer

    def tostring(self):
        """
        Generate a string of the code for this property. We do this by finding the
        appropriate writer (depending on the type of property we are generating)
        and then delegating the actual generation to the writer.
        """
        return self.writer.tostring()

    def __repr__(self):
        return "<AttributePrototype [{}] {}>".format(self.property_type, self.name)


class BaseWriter(object):
    __metaclass__ = ABCMeta

    def __init__(self, prototype):
        self.prototype = prototype

    @abstractmethod
    def tostring(self):
        """String version"""

    @property
    def logger(self):
        return self.prototype.logger


class BaseClassWriter(BaseWriter):
    def __init__(self, prototype):
        super(BaseClassWriter, self).__init__(prototype=prototype)

    # Give easy access to prototypes attributes
    @property
    def parser(self):
        return self.prototype.parser

    @property
    def name(self):
        return self.prototype.name

    @property
    def field_name(self):
        return self.prototype.field_name

    @property
    def parent_class(self):
        return self.prototype.parent_class

    @property
    def parent_property(self):
        return self.prototype.parent_property

    @property
    def attributes(self):
        return self.prototype.attributes

    @property
    def base_class(self):
        if self.prototype.base_class is None:
            return self.default_base_class

        return self.prototype.base_class

    @property
    def display_identifier(self):
        if self.prototype.display_identifier is None and self.name in SECONDARY_LOOKUP_FIELDS:
            return SECONDARY_LOOKUP_FIELDS[self.name]
        else:
            return self.prototype.display_identifier

    @display_identifier.setter
    def display_identifier(self, value):
        self._display_identifier = value

    @property
    def abstract(self):
        return self.prototype.abstract

    @property
    def simple(self):
        return self.prototype.simple

    @property
    def source_schema(self):
        return self.prototype.source_schema

    # Convenience methods that can be shared along writers
    def get_base_template(self):
        if hasattr(xnatbases, self.python_name):
            return getattr(xnatbases, self.python_name)

    def _pythonize_name(self, name):
        return pythonize_class_name(name)

    @property
    def python_name(self):
        return pythonize_class_name(self.name)

    @property
    def python_base_class(self):
        return pythonize_class_name(self.base_class)

    @property
    def python_parent_class(self):
        return pythonize_class_name(self.parent_class)

    def hasattr(self, name):
        base = self.get_base_template()

        if base is not None:
            return hasattr(base, name)
        else:
            base = self.parser.class_list.get(self.base_class)
            if base is not None:
                if isinstance(base, ClassPrototype):
                    return base.writer.hasattr(name)
                else:
                    return base.hasattr(name)
            else:
                base = self.get_super_class()
                return hasattr(base, name)

    def get_super_class(self):
        if hasattr(core, self.python_base_class):
            return getattr(core, self.python_base_class)

    # Shared functional blocks
    def tostring(self):
        header = self.header()
        properties = '\n\n'.join(self.print_property(p) for p in self.attributes.values() if not self.hasattr(p.clean_name))

        return '{}{}'.format(header, properties)

    def print_property(self, prop):
        data = prop.tostring()
        if prop.name == SECONDARY_LOOKUP_FIELDS.get(self.name, '!None'):
            head, tail = data.split('\n', 1)
            data = '{}\n    @caching\n{}'.format(head, tail)
        return data

    def header(self):
        base = self.get_base_template()
        if base is not None:
            base_source = inspect.getsource(base)
            base_source = re.sub(r'class {}\(XNATBaseObject\):'.format(self.python_name), 'class {}({}):'.format(self.python_name, self.python_base_class), base_source)
            header = base_source.strip() + '\n\n    # END HEADER\n'
        else:
            header = '# No base template found for {}\n'.format(self.python_name)
            header += "class {name}({base}):\n".format(name=self.python_name, base=self.python_base_class)

        header += "    # Abstract: {}\n".format(self.abstract)
        header += "    # Simple: {}\n".format(self.simple)
        header += "    # Object class: {}\n".format(self.default_base_class)
        header += "    # Source schema: {}\n".format(self.source_schema)

        if self.display_identifier is not None:
            header += "    _DISPLAY_IDENTIFIER = '{}'\n".format(self.display_identifier)

        if 'fields' in self.attributes:
            header += "    _HAS_FIELDS = True\n"

        if self.parent_class is not None:
            header += "    #_PARENT_CLASS = {}\n".format(self.python_parent_class)
            header += "    _FIELD_NAME = '{}'\n".format(self.field_name)
        elif self.name in FIELD_HINTS:
            header += "    _CONTAINED_IN = '{}'\n".format(FIELD_HINTS[self.name])

        header += "    _XSI_TYPE = '{}'\n\n".format(self.name)

        header += "    @classmethod\n" \
                  "    def __register__(cls, target):\n" \
                  "        target['{}'] = cls\n\n".format(self.name)

        if self.name in SECONDARY_LOOKUP_FIELDS:
            header += self.init

        if self.display_identifier is not None:
            header += ("    @property\n"
                       "    def __display_identifier(self):\n"
                       "        return self.{}\n\n".format(self.display_identifier))

        return header

    # Abstract stuff that needs to be reimplemented by subclasses
    @abstractproperty
    def default_base_class(self):
        """
        The default base class if none is supplied
        """


class SimpleClassWriter(BaseClassWriter):
    @property
    def base_class(self):
        return "XNATSubObjectMixin"

    def create_listing(self, field_name, secondary_lookup):
        return """
        # Automatically generated PropertyListing, by {element_class_name} (SimpleClassWriter)
        # Secondary lookup: '{secondary_lookup}'
        return XNATSimpleListing(
            parent=self,
            field_name='{field_name}',
            secondary_lookup_field={secondary_lookup}
        )""".format(field_name=field_name,
                    secondary_lookup=secondary_lookup,
                    element_class_name=self.name)

    @property
    def default_base_class(self):
        return 'XNATSubObjectMixin'


class SubObjectClassWriter(BaseClassWriter):
    def create_listing(self, field_name, secondary_lookup):
        return """
        # Automatically generated PropertyListing, by {element_class_name} (SubObjectClassWriter)
        # Secondary lookup: '{secondary_lookup}'
        return XNATSubListing(parent=self,
                              field_name='{field_name}',
                              secondary_lookup_field={secondary_lookup},
                              xsi_type='{type_}')""".format(field_name=field_name,
                                                            secondary_lookup=secondary_lookup,
                                                            element_class_name=self.name,
                                                            type_=self.name)

    @property
    def xsi_type_registration(self):
        result = 'xnatpy:' + self.name

        return result

    @property
    def default_base_class(self):
        return 'XNATSubObjectMixin'


class NestedObjectClassWriter(BaseClassWriter):
    @property
    def default_base_class(self):
        return 'XNATNestedObjectMixin'

    @property
    def xsi_type_registration(self):
        return self.xsi_type

    def create_listing(self, field_name, secondary_lookup):
        if secondary_lookup is None:
            secondary_lookup = self.display_identifier

        if '/' in field_name:
            field_name = field_name.split('/')[0]

        return """
        # Automatically generated PropertyListing, by {element_class_name} (NestedObjectClassWriter)
        # Secondary lookup: '{secondary_lookup}'
        return XNATSubListing(uri=self.fulluri + '/{field_name}',
                                 parent=self,
                                 field_name='{field_name}',
                                 secondary_lookup_field={secondary_lookup},
                                 xsi_type='{type_}')""".format(field_name=field_name,
                                                               secondary_lookup=secondary_lookup,
                                                               element_class_name=self.name,
                                                               type_=self.name)


class ObjectClassWriter(BaseClassWriter):
    def __repr__(self):
        return '<ObjectClassWriter {}({})>'.format(self.name, self.base_class)

    def create_listing(self, field_name, secondary_lookup):
        if secondary_lookup is None:
            secondary_lookup = self.display_identifier

        if '/' in field_name:
            field_name = field_name.split('/')[0]

        return """
        # Automatically generated PropertyListing, by {element_class_name} (ObjectClassWriter)
        # Secondary lookup: '{secondary_lookup}'
        return XNATListing(uri=self.fulluri + '/{field_name}',
                           parent=self,
                           field_name='{field_name}',
                           secondary_lookup_field={secondary_lookup},
                           xsi_type='{type_}')""".format(field_name=field_name,
                                                         secondary_lookup=secondary_lookup,
                                                         element_class_name=self.name,
                                                         type_=self.name)

    @property
    def default_base_class(self):
        return 'XNATObjectMixin'

    @property
    def init(self):
        return \
"""    def __init__(self, uri=None, xnat_session=None, id_=None, datafields=None, parent=None, {lookup}=None, **kwargs):
        super({name}, self).__init__(uri=uri, xnat_session=xnat_session, id_=id_, datafields=datafields, parent=parent, {lookup}={lookup}, **kwargs)
        if {lookup} is not None:
            self._cache['{lookup}'] = {lookup}

""".format(name=self.python_name, lookup=SECONDARY_LOOKUP_FIELDS[self.name])


class AttributeWriter(BaseWriter):
    # Give easy access to prototypes attributes
    @property
    def parser(self):
        return self.prototype.parser

    @property
    def name(self):
        return self.prototype.name

    @property
    def clean_name(self):
        return self.prototype.clean_name

    @property
    def type(self):
        return self.prototype.type

    @property
    def parent_class(self):
        return self.prototype.parent_class

    @property
    def parent_property(self):
        return self.prototype.parent_property

    @property
    def restrictions(self):
        return self.prototype.restrictions

    @property
    def element_class(self):
        return self.prototype.element_class

    @property
    def min_occurs(self):
        return self.prototype.min_occur

    @property
    def max_occurs(self):
        return self.prototype.max_occur

    @property
    def docstring(self):
        return self.prototype.docstring

    @property
    def display_identifier(self):
        return self.prototype.display_identifier

    @property
    def field_name(self):
        return self.prototype.field_name

    # Actual funcions
    def __repr__(self):
        parent = self.parent_class.name if self.parent_class else None
        element = self.element_class.name if self.element_class else None

        return '<{} {} (parent: {}, element: {})>'.format(type(self).__name__,
                                                          self.name,
                                                          parent,
                                                          element)

    def restrictions_code(self):
        if len(self.restrictions) > 0:
            data = '\n        # Restrictions for value'
            if 'min' in self.restrictions:
                data += "\n        if value < {min}:\n            raise ValueError('{name} has to be greater than or equal to {min}')\n".format(name=self.name, min=self.restrictions['min'])
            if 'max' in self.restrictions:
                data += "\n        if value > {max}:\n            raise ValueError('{name} has to be smaller than or equal to {max}')\n".format(name=self.name, max=self.restrictions['max'])
            if 'maxlength' in self.restrictions:
                data += "\n        if len(value) > {maxlength}:\n            raise ValueError('length {name} has to be smaller than or equal to {maxlength}')\n".format(name=self.name, maxlength=self.restrictions['maxlength'])
            if 'minlength' in self.restrictions:
                data += "\n        if len(value) < {minlength}:\n            raise ValueError('length {name} has to be larger than or equal to {minlength}')\n".format(name=self.name, minlength=self.restrictions['minlength'])
            if 'enum' in self.restrictions:
                data += "\n        if value not in [{enum}]:\n            raise ValueError('{name} has to be one of: {enum}')\n".format(name=self.name, enum=', '.join('"{}"'.format(x.replace("'", "\\'")) for x in self.restrictions['enum']))

            return data
        else:
            return ''


class ConstantWriter(AttributeWriter):
    def __init__(self, parser, name, value=None):
        super(ConstantWriter, self).__init__(parser, name)

        self.value = value

    def __str__(self):
        return "    {s.clean_name} = {s.value}".format(s=self)

    def __repr__(self):
        return '<ConstantWriter {}({})>'.format(self.name, self.value)

    @property
    def clean_name(self):
        name = re.sub('[^0-9a-zA-Z]+', '_', self.name)
        name = '_{}'.format(name.upper())

        return name

    def tostring(self):
        return "CONSTANT = 'VALUE'"


class PropertyWriter(AttributeWriter):
    def __repr__(self):
        return '<PropertyWriter {}({})>'.format(self.name, self.type_)

    def tostring(self):
        type_string = ':py:class:`{}`'.format(full_class_name(TYPE_TO_PYTHON.get(self.type, str)))

        docstring_content = self.docstring + '\n\n' if self.docstring else ''
        docstring_content += "\n        Property of type: {}".format(type_string)
        docstring = '\n        """{}"""'.format(docstring_content)
        return \
    """    @mixedproperty
    def {clean_name}(cls):{docstring}
        # 0 Automatically generated Property, type: {type_}
        return search.SearchField(cls, "{name}")

    @{clean_name}.getter
    def {clean_name}(self):{docstring}
        # Generate automatically, type: {type_}
        return self.get("{name}", type_="{type_}")

    @{clean_name}.setter
    def {clean_name}(self, value):{docstring}{restrictions}
        # Automatically generated Property, type: {type_}
        self.set("{name}", value, type_="{type_}")
        
    @{clean_name}.deleter
    def {clean_name}(self):{docstring}
        # Automatically generated Property, type: {type_}
        self.del_("{name}")""".format(clean_name=self.clean_name,
                                      docstring=docstring,
                                      name=self.name,
                                      type_=self.type,
                                      restrictions=self.restrictions_code())


class SubObjectPropertyWriter(AttributeWriter):
    def __repr__(self):
        return '<SubObjectPropertyWriter {}({})>'.format(self.name, self.type)

    def tostring(self):
        if self.type is None:
            if self.element_class is not None:
                xsi_type = self.element_class.name
                xsi_type_arg = ', "{}"'.format(xsi_type)
            else:
                xsi_type = '_UNKNOWN_'
                xsi_type_arg = ', "{}"'.format(xsi_type)
        else:
            xsi_type = '{}'.format(core.TYPE_HINTS.get(self.name, self.type))
            xsi_type_arg = ', "{}"'.format(xsi_type)

        type_def = self.type or self.element_class

        if type_def:
            if isinstance(type_def, ClassPrototype):
                type_string = 'xnat.classes.{}'.format(pythonize_class_name(type_def.name))
            elif type_def.startswith('xs:'):
                type_string = full_class_name(TYPE_TO_PYTHON.get(type_def, str))
            else:
                type_string = type_def
                if ':' in type_string:
                    type_string.split(':', 1)
                type_string = 'xnat.classes.{}'.format(pythonize_class_name(type_string))

            type_string = ':py:class:`listing <xnat.core.XNATBaseListing>` of :py:class:`{}`'.format(type_string)
        else:
            type_string = 'Unknown'

        docstring_content = self.docstring + '\n\n' if self.docstring else '\n'
        docstring_content += "        Property of type: {}".format(type_string)
        docstring = '\n        """{}"""'.format(docstring_content)

        return \
            """    @mixedproperty
    def {clean_name}(cls):{docstring}
        # 1 Automatically generated Property, type: {type_}
        return XNAT_CLASS_LOOKUP["{xsi_type}"]

    @{clean_name}.getter
    @caching
    def {clean_name}(self):
        # Generated automatically, type: {type_}
        return self.get_object("{name}"{xsi_type_arg})""".format(clean_name=self.clean_name,
                                                                 docstring=docstring,
                                                                 name=self.name,
                                                                 type_=self.type,
                                                                 xsi_type=xsi_type,
                                                                 xsi_type_arg=xsi_type_arg)


class ListingPropertyWriter(AttributeWriter):
    def __repr__(self):
        return '<ListingPropertyWriter {}({})>'.format(self.name, self.type)

    def tostring(self):
        if self.display_identifier is not None:
            secondary_lookup = self.display_identifier
        elif self.type is not None:
            cls = self.parser.class_list.get(self.type)
            if cls is not None:
                if cls.name in SECONDARY_LOOKUP_FIELDS:
                    secondary_lookup = SECONDARY_LOOKUP_FIELDS[cls.name]
                else:
                    secondary_lookup = cls.display_identifier
            else:
                secondary_lookup = None
        else:
            secondary_lookup = None

        if secondary_lookup is not None:
            secondary_lookup = "'{}'".format(secondary_lookup)

        field_name = self.field_name or self.name

        # Get the correct type for in the docstring
        type_def = self.element_class or self.type

        if isinstance(type_def, ClassPrototype):
            type_string = 'xnat.classes.{}'.format(pythonize_class_name(type_def.name))
        elif type_def.startswith('xs:'):
            type_string = full_class_name(TYPE_TO_PYTHON.get(type_def, str))
        else:
            type_string = type_def
            if ':' in type_string:
                type_string.split(':', 1)
            type_string = 'xnat.classes.{}'.format(pythonize_class_name(type_string))

        type_string = ':py:class:`listing <xnat.core.XNATBaseListing>` of :py:class:`{}`'.format(type_string)

        docstring_content = self.docstring + '\n\n        ' if self.docstring else ''
        docstring_content += type_string
        docstring = '\n        """ {} """'.format(docstring_content)

        property_base = '''    @property
    @caching
    def {clean_name}(self):{docstring}'''.format(clean_name=self.clean_name, docstring=docstring)
        if self.element_class is not None:
            element_class = self.element_class
            property_base += element_class.writer.create_listing(secondary_lookup=secondary_lookup, field_name=field_name)
        elif not self.type.startswith('xs:'):
            element_class = self.parser.class_list[self.type]
            property_base += element_class.writer.create_listing(secondary_lookup=secondary_lookup, field_name=field_name)
        else:
            property_base += "\n        # TODO: Implement simple type listing! (type: {})\n".format(self.type) + \
                             "        pass"
        return property_base


class SchemaParser(object):
    def __init__(self, logger, debug=False):
        # Manage XML namespaces
        self.namespaces = {}
        self.namespace_prefixes = {}
        self.target_namespace = ''
        self.current_schema = None

        self.class_list = collections.OrderedDict()
        self.class_list = collections.OrderedDict()
        self.unknown_tags = set()
        self.new_class_stack = [None]
        self.new_property_stack = [None]
        self.property_prefixes = []
        self.debug = debug
        self.schemas = []
        self.class_names = collections.OrderedDict()
        self.logger = logger

    def parse_schema_xmlstring(self, xml, schema_uri):
        self.current_schema = schema_uri
        root = ElementTree.fromstring(xml)

        # Get the namespaces from the XML document (ElementTree loses them, so
        # get them by hand) and register them
        xml_schema_element_match = re.search('<xs:schema([^>]*)>', xml)

        if xml_schema_element_match is None:
            result = []
        else:
            xml_schema_element = xml_schema_element_match.group(1)
            result = re.findall(r'xmlns:(?P<prefix>\w+)="(?P<ns>\S+)"', xml_schema_element)

        for prefix, namespace in result:
            self.logger.debug('Registering namespace: {}  ->  {}'.format(
                prefix, namespace)
            )
            self.namespace_prefixes[namespace] = prefix
            self.namespaces[prefix] = namespace

        # Register schema as being loaded
        self.schemas.append(schema_uri)

        # Parse xml schema
        self.parse(root, toplevel=True)

        if self.debug:
            self.logger.debug('Found {} unknown tags: {}'.format(len(self.unknown_tags),
                                                                 self.unknown_tags))

        self.current_schema = None
        return True

    def parse_schema_file(self, filepath):
        filepath = os.path.abspath(filepath)
        filepath = os.path.normpath(filepath)

        schema_uri = 'file://{}'.format(filepath)

        with open(filepath) as fin:
            data = fin.read()

        self.parse_schema_xmlstring(data, schema_uri=schema_uri)

    def parse_schema_uri(self, xnat_session, schema_uri):
        self.logger.info('=== Retrieving schema from {} ==='.format(schema_uri))

        resp = xnat_session.get(schema_uri, headers={'Accept-Encoding': None})
        data = resp.text

        try:
            return self.parse_schema_xmlstring(data, schema_uri=schema_uri)
        except ElementTree.ParseError as exception:
            if 'action="/j_spring_security_check"' in data:
                self.logger.error('You do not have access to this XNAT server, please check your credentials!')
            elif 'java.lang.IllegalStateException' in data:
                self.logger.error('The server returned an error. You probably do not'
                                  ' have access to this XNAT server, please check your credentials!')
            else:
                self.logger.info('Could not parse schema from {}, no valid XML found'.format(schema_uri))

                if self.debug:
                    self.logger.debug('XML schema request returned the following response: [{}] {}'.format(resp.status_code,
                                                                                                           data))
            return False

    @staticmethod
    def find_schema_uris(text):
        try:
            root = ElementTree.fromstring(text)
        except ElementTree.ParseError:
            raise ValueError('Could not parse xml file')

        schemas_string = root.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', '')
        schemas = [x for x in schemas_string.split() if x.endswith('.xsd')]

        return schemas

    def __iter__(self):
        visited = set()
        nr_previsited = len(visited)
        tries = 0
        yielded_anything = True
        while len(visited) < len(self.class_list) and yielded_anything and tries < 25:
            yielded_anything = False
            for key, value in self.class_list.items():
                if key in visited:
                    continue

                base = value.base_class
                if base is not None and not base.startswith('xs:') and base not in visited:
                    if self.debug:
                        self.logger.debug("Wait with processing {} because base {} is not yet processed".format(
                            value.name, base
                        ))
                    continue

                if value.parent_class is not None and value.parent_class not in visited:
                    if self.debug:
                        self.logger.debug("Wait with processing {} because parent {} is not yet processed".format(
                            value.name, value.parent_class
                        ))
                    continue

                visited.add(key)
                yielded_anything = True
                self.logger.info('Processing {} (base class {})'.format(value.name, value.base_class))
                yield value

            tries += 1

        expected = len(self.class_list) + nr_previsited  # We started with two "visited" classes
        if self.debug:  # and len(visited) < len(self.class_list):
            missed = sorted(set(self.class_list) - visited)
            if self.debug:
                self.logger.debug('Visited: {}, expected: {}'.format(len(visited), expected))
                self.logger.debug('Visited: {}'.format(visited))
                self.logger.info('Missed: {}'.format(missed))
                self.logger.info('Missed base class: {}'.format([self.class_list[x].base_class for x in missed]))
                self.logger.debug('Spent {} iterations'.format(tries))

    @contextlib.contextmanager
    def _descend(self, new_class=None, new_property=None, property_prefix=None):
        if new_class is not None:
            self.new_class_stack.append(new_class)
        if new_property is not None:
            self.new_property_stack.append(new_property)
        if property_prefix is not None:
            self.property_prefixes.append(property_prefix)

        yield

        if new_class is not None:
            self.new_class_stack.pop()
        if new_property is not None:
            self.new_property_stack.pop()
        if property_prefix is not None:
            self.property_prefixes.pop()

    @property
    def _current_class(self):
        return self.new_class_stack[-1]

    @property
    def _current_property(self):
        return self.new_property_stack[-1]

    def parse(self, element, toplevel=False):
        if element.tag in self.PARSERS:
            self.PARSERS[element.tag](self, element)
        else:
            self._parse_unknown(element)

    # TODO: We should check the following restrictions:
    # http://www.w3schools.com/xml/schema_facets.asp

    def _parse_all(self, element):
        self._parse_children(element)

    def _parse_annotation(self, element):
        self._parse_children(element)

    def _parse_attribute(self, element):
        name = element.get('name')
        type_ = element.get('type')

        if self._current_class is not None:
            if name is None:
                if self.debug:
                    self.logger.warning('Encountered attribute without name')
                return

            new_property = AttributePrototype(self, name=name, logger=self.logger,
                                              type=type_, parent_class=self._current_class,
                                              parent_property=self._current_property)

            self._current_class.attributes[name] = new_property

            with self._descend(new_property=new_property):
                self._parse_children(element)

    def _parse_children(self, element):
        for child in list(element):
            self.parse(child)

    def _parse_choice(self, element):
        self._parse_children(element)

    def _parse_complex_content(self, element):
        self._parse_children(element)

    def _parse_complex_type(self, element):
        name = element.get('name')
        parent_class = None
        field_name = None

        if name is None:
            name = 'xnatpy:' + self._current_class.name.split(":", 1)[-1] + self._current_property.name.capitalize()
            parent_class = self._current_class.name
            field_name = self._current_property.name
        else:
            if ':' not in name:
                name = self.target_namespace_prefix + name

        new_class = ClassPrototype(self,
                                   name=name,
                                   logger=self.logger,
                                   field_name=field_name,
                                   parent_class=parent_class)

        if self._current_property is not None:
            self._current_property.element_class = new_class
            new_class.parent_property = self._current_property

        self.class_list[name] = new_class

        # Descend
        with self._descend(new_class=new_class):
            self._parse_children(element)

    def _parse_documentation(self, element):
        if self._current_property is not None:
            self._current_property.docstring = element.text

    def _parse_element(self, element):
        name = element.get('name')
        type_ = element.get('type')

        if name is None:
            abstract = element.get('abstract')
            if abstract is not None:
                self._current_class.abstract = abstract == "true"
            else:
                if self.debug:
                    self.logger.warning('Encountered attribute without name')
            return

        if self._current_class is not None:
            min_occur = element.get('minOccurs')
            max_occur = element.get('maxOccurs')

            new_property = AttributePrototype(self, name=name, logger=self.logger,
                                              type=type_, parent_class=self._current_class,
                                              parent_property=self._current_property,
                                              min_occur=min_occur, max_occur=max_occur)

            self._current_class.attributes[name] = new_property

            with self._descend(new_property=new_property):
                self._parse_children(element)

    def _parse_enumeration(self, element):
        if 'enum' in self._current_property.restrictions:
            self._current_property.restrictions['enum'].append(element.get('value'))
        else:
            self._current_property.restrictions['enum'] = [element.get('value')]

    def _parse_error(self, element):
        raise NotImplementedError('The parser for {} has not yet been implemented'.format(element.tag))

    def _parse_extension(self, element):
        new_base = element.get('base')
        if new_base.startswith('xs:'):
            # Need to create a base object as we do not have this
            previous_base = new_base
            name = new_base[3:].capitalize()
            if self._current_property is not None:
                new_prop = self._current_property.name
                new_base = 'xnatpy:{}{}'.format(new_prop, name)
            else:
                new_prop = self._current_class.name
                new_base = self._current_class.name + name
                new_base = 'xnatpy:{}'.format(new_base.split(':', 1)[1])

            new_base_class = ClassPrototype(self,
                                            name=new_base,
                                            logger=self.logger,
                                            simple=True)

            new_base_class.attributes[new_prop] = AttributePrototype(self,
                                                                     name=new_prop,
                                                                     logger=self.logger,
                                                                     type=previous_base)
            self.class_list[new_base] = new_base_class

        self._current_class.base_class = new_base
        self._parse_children(element)

    def _parse_ignore(self, element):
        pass

    def _parse_max_inclusive(self, element):
        self._current_property.restrictions['max'] = element.get('value')

    def _parse_max_length(self, element):
        self._current_property.restrictions['maxlength'] = element.get('value')

    def _parse_min_inclusive(self, element):
        self._current_property.restrictions['min'] = element.get('value')

    def _parse_min_length(self, element):
        self._current_property.restrictions['minlength'] = element.get('value')

    def _parse_restriction(self, element):
        old_type = self._current_property.type
        new_type = element.get('base')

        if old_type is not None and old_type != new_type:
            raise ValueError('Trying to override a type from a restriction!? (from {} to {})'.format(old_type, new_type))

        self._current_property.type = new_type

        # Parse further restrictions
        self._parse_children(element)

    def _parse_schema(self, element):
        self.target_namespace = element.get("targetNamespace", '')
        if self.target_namespace != '':
            self.target_namespace_prefix = self.namespace_prefixes[self.target_namespace] + ':'
        else:
            self.target_namespace_prefix = ''

        for child in list(element):
            if child.tag in [
                '{http://www.w3.org/2001/XMLSchema}complexType',
                '{http://www.w3.org/2001/XMLSchema}simpleType'
            ]:
                self.parse(child)
            elif child.tag == '{http://www.w3.org/2001/XMLSchema}element':
                name = child.get('name')
                type_ = child.get('type')

                if self.debug:
                    self.logger.debug('Adding {} -> {} to class name map'.format(name, type_))
                self.class_names[type_] = name
            else:
                if self.debug:
                    self.logger.debug('Skipping non-class top-level tag {}'.format(child.tag))

    def _parse_sequence(self, element):
        self._parse_children(element)

    def _parse_simple_content(self, element):
        self._parse_children(element)

    def _parse_simple_type(self, element):
        name = element.get("name")

        # This is not top-level in the schema and just adds restriction
        if name is None:
            self._parse_children(element)
            return

        # This is the top-level of schema and a sort of typedef
        if ':' not in name:
            name = self.target_namespace_prefix + name

        new_class = ClassPrototype(self,
                                   name=name,
                                   logger=self.logger,
                                   simple=False)

        new_property = AttributePrototype(self,
                                          name="value",
                                          logger=self.logger,
                                          type=None)
        new_class.attributes["value"] = new_property

        self.class_list[name] = new_class

        # Descend
        with self._descend(new_class=new_class, new_property=new_property):
            self._parse_children(element)

    def _parse_unknown(self, element):
        self.unknown_tags.add(element.tag)

    def _parse_xdat_element(self, element):
        abstract = element.get("abstract")
        if abstract is not None:
            self._current_class.abstract = abstract == "true"

        display_identifier = element.get("displayIdentifiers")
        if display_identifier is not None:
            if self._current_property is None:
                self._current_class.display_identifier = display_identifier
            else:
                self._current_property.display_identifier = display_identifier

    def _parse_sqlfield(self, element):
        if self.debug:
            self.logger.debug("CLASS: {}, PROP: {}, ELEMENT: {}".format(self._current_class.name, self._current_property.name, element))

    PARSERS = {
        '{http://www.w3.org/2001/XMLSchema}all': _parse_all,
        '{http://www.w3.org/2001/XMLSchema}annotation': _parse_annotation,
        '{http://www.w3.org/2001/XMLSchema}appinfo': _parse_children,
        '{http://www.w3.org/2001/XMLSchema}attribute': _parse_attribute,
        '{http://www.w3.org/2001/XMLSchema}attributeGroup': _parse_error,
        '{http://www.w3.org/2001/XMLSchema}choice': _parse_choice,
        '{http://www.w3.org/2001/XMLSchema}complexContent': _parse_complex_content,
        '{http://www.w3.org/2001/XMLSchema}complexType': _parse_complex_type,
        '{http://www.w3.org/2001/XMLSchema}documentation': _parse_documentation,
        '{http://www.w3.org/2001/XMLSchema}element': _parse_element,
        '{http://www.w3.org/2001/XMLSchema}enumeration': _parse_enumeration,
        '{http://www.w3.org/2001/XMLSchema}extension': _parse_extension,
        '{http://www.w3.org/2001/XMLSchema}import': _parse_ignore,
        '{http://www.w3.org/2001/XMLSchema}group': _parse_error,
        '{http://www.w3.org/2001/XMLSchema}maxInclusive': _parse_max_inclusive,
        '{http://www.w3.org/2001/XMLSchema}maxLength': _parse_max_length,
        '{http://www.w3.org/2001/XMLSchema}minInclusive': _parse_min_inclusive,
        '{http://www.w3.org/2001/XMLSchema}minLength': _parse_min_length,
        '{http://www.w3.org/2001/XMLSchema}restriction': _parse_restriction,
        '{http://www.w3.org/2001/XMLSchema}schema': _parse_schema,
        '{http://www.w3.org/2001/XMLSchema}sequence': _parse_sequence,
        '{http://www.w3.org/2001/XMLSchema}simpleContent': _parse_simple_content,
        '{http://www.w3.org/2001/XMLSchema}simpleType': _parse_simple_type,
        '{http://www.w3.org/2001/XMLSchema}unique': _parse_ignore,
        '{http://nrg.wustl.edu/xdat}element': _parse_xdat_element,
        '{http://nrg.wustl.edu/xdat}field': _parse_children,
        '{http://nrg.wustl.edu/xdat}sqlField': _parse_sqlfield,
    }

    def prune_tree(self):
        to_remove = set()

        for cls in self.class_list.values():
            for property_key, prop in cls.attributes.items():
                element_class = prop.element_class

                if element_class is not None and len(element_class.attributes) == 1:
                    element_property = next(iter(element_class.attributes.values()))

                    if element_property.property_type == 'listing':
                        # Reset parent to current parent
                        parent_class = prop.parent_class

                        element_property.parent_class = parent_class
                        element_property.field_name = '{}/{}'.format(prop.name, element_property.name)
                        element_property.name = prop.name

                        # The new element_class has to be updated to take the place of the old element_class
                        new_element_class = element_property.element_class
                        if new_element_class is not None:
                            new_element_class.name = element_class.name
                            new_element_class.field_name = '{}/{}'.format(element_class.field_name,
                                                                          new_element_class.field_name)
                            new_element_class.parent_class = element_class.parent_class

                        if element_class.name in self.class_list:
                            if self.debug:
                                self.logger.info('Removing class {} from parser, it only has one element!'.format(
                                    element_class.name)
                                )
                            to_remove.add(element_class.name)

                        cls.attributes[property_key] = element_property
                    elif self.debug:
                        self.logger.debug("Ignoring non-listing...")
                        self.logger.debug("Element class: {}".format(element_class.__dict__))

        for key in to_remove:
            del self.class_list[key]

        for cls in self.class_list.values():
            for property_key, prop in cls.attributes.items():
                # Only consider simplifying listings
                if prop.property_type != 'listing':
                    continue

                # If the type is not by element class, no need to check further
                if prop.element_class is None:
                    continue

                if prop.element_class.simple:
                    if self.debug:
                        self.logger.debug('Found simple mapping {}.{} -> {}'.format(cls.name,
                                                                                        property_key,
                                                                                        prop.element_class.name))

                    if len(prop.element_class.attributes) > 2:
                        if self.debug:
                            self.logger.debug(
                                'Too many attributes to simplify (found {} attributed)'.format(
                                    len(prop.element_class.attributes)
                                )
                            )
                        continue

                # Attempt to find listings with simple type

    def write(self, code_file):
        if self.debug:
            self.logger.debug('namespaces: {}'.format(self.namespaces))
            self.logger.debug('namespace prefixes: {}'.format(self.namespace_prefixes))

        self.logger.info('=== Pruning data structure ===')
        before = set(self.class_list.keys())
        if self.debug:
            self.logger.debug('Classed before prune: {}'.format(before))
        self.prune_tree()
        after = set(self.class_list.keys())
        if self.debug:
            self.logger.debug('Classed after prune: {}'.format(after))
            self.logger.info('Classes removed by pruning: {}'.format(sorted(before - after)))

        self.logger.info('=== Writing result ===')
        schemas = '\n'.join('# - {}'.format(s) for s in self.schemas)
        code_file.write(FILE_HEADER.format(schemas=schemas,
                                           file_secondary_lookup=SECONDARY_LOOKUP_FIELDS['xnat:fileData']))

        code_file.write('\n\n\n'.join(c.tostring().strip() for c in self if c.name is not None))
