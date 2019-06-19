# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Library of the nodes
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import json
import os
import collections
import logging
import six

import PySide.QtCore as QtCore

from sympathy.platform import node_result
from sympathy.utils.prim import open_url, uri_to_path, localuri
from sympathy.utils.tag import LibraryTags
from sympathy.utils import port as port_util
from sympathy.types import types
import Gui.datatypes as datatypes
import Gui.settings as settings
from . import library_manager
from . import util


node_id = 0
core_logger = logging.getLogger('core')


@six.python_2_unicode_compatible
class PortDefinition(object):
    def __init__(self, name, description, datatype, scheme, index,
                 requires_input_data=False):
        super(PortDefinition, self).__init__()
        self._name = name
        self._description = description
        if isinstance(datatype, datatypes.DataType):
            self._datatype = datatype
        else:
            self._datatype = datatypes.DataType.from_str(datatype)

        self.generics = types.generics(self._datatype.datatype)

        self._scheme = scheme
        self._index = index
        self._requires_input_data = requires_input_data

    @classmethod
    def from_definition(cls, definition):
        name = definition['name']
        description = definition['description']
        type_ = definition.get('type') or definition['datatype']
        datatype = datatypes.DataType.from_str(type_)
        scheme = definition['scheme']
        index = definition['index']
        requires_input_data = definition.get('requiresdata', True)
        return cls(name, description, datatype, scheme, index,
                   requires_input_data)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def datatype(self):
        return self._datatype

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def requires_input_data(self):
        return self._requires_input_data

    @property
    def file_list(self):
        return self._file_list

    @file_list.setter
    def file_list(self, value):
        self._file_list = value

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        self._scheme = value

    def __str__(self):
        return 'PortDefinition: {}/{} {}'.format(
            self._name, self._description, self._index)


class AnyTypePortDefinition(PortDefinition):
    def __init__(self):
        super(AnyTypePortDefinition, self).__init__(
            'Port', 'Port', datatypes.Any, 'hdf5', -1, False)


class ParameterModel(object):
    def __init__(self):
        super(ParameterModel, self).__init__()
        self._data = {'type': 'group'}
        self._type = 'json'

    @classmethod
    def from_dict(cls, dictionary):
        instance = cls()
        instance.build_from_dict(dictionary)
        return instance

    @classmethod
    def from_json(cls, json_data):
        instance = cls()
        instance.build_from_json(json_data)
        return instance

    def to_dict(self):
        return self._data

    def to_ordered_dict(self):
        def key_fn(item):
            """
            Place scalar values first, in alphabetical order. Place lists after
            that. Place dictionaries with 'order' keys after that based on
            'order'. Lastly, place dictionaries without an 'order' key.
            """
            if isinstance(item[1], (
                    six.string_types, int, float, bool, type(None))):
                return (0, item[0])
            elif isinstance(item[1], list):
                return (1, item[0])
            elif isinstance(item[1], dict):
                try:
                    return (2, item[1]['order'])
                except (KeyError, TypeError):
                    return (3, item[0])
            else:
                return (4, item[0])

        def sort_dict(parameter_dict):
            if isinstance(parameter_dict, dict):
                items = [(k, sort_dict(v))
                         for k, v in parameter_dict.items()]
                return collections.OrderedDict(
                    sorted(items, key=key_fn))
            else:
                return parameter_dict

        return sort_dict(self._data)

    def json(self):
        return json.dumps(self._data)

    def build_from_json(self, parameters):
        self.build_from_dict(json.loads(parameters))

    def build_from_dict(self, parameters):
        if parameters is None:
            return
        if 'data' in parameters:
            self._data = parameters['data']
            self._type = parameters['type']

    def is_empty(self, ignore_group=False):
        if ignore_group:
            res = len(self._data) <= 1
        else:
            res = len(self._data) == 0
        return res

    def equal_to(self, other_parameter_model):
        """
        Compares this parameter model to another parameter model and returns
        true if all "value" and "list" keys are equal.
        :param other_parameter_model: Parameter model to compare.
        :return: True if equal.
        """
        def compare_values_and_lists(a_dict1, a_dict2):
            """Compare keys and the values at the keys 'value' and 'list'."""
            if set(a_dict1.keys()) != set(a_dict2.keys()):
                yield False
                return

            for k, v in a_dict1.items():
                if k in a_dict2:
                    try:
                        if 'value' in v:
                            yield v['value'] == a_dict2[k]['value']
                        if 'value_names' in v:
                            yield v['value_names'] == a_dict2[k]['value_names']
                        if 'list' in v:
                            yield v['list'] == a_dict2[k]['list']
                        if 'mode' in v:
                            yield v['mode'] == a_dict2[k]['mode']
                    except TypeError:
                        pass
                    if isinstance(v, collections.Mapping):
                        for i in compare_values_and_lists(v, a_dict2[k]):
                            yield i

        return all(compare_values_and_lists(self.to_dict(),
                                            other_parameter_model.to_dict()))


class LibraryInterface(object):
    def __init__(self):
        super(LibraryInterface, self).__init__()
        self._uri = None
        self._name = None
        self._libraries = None
        self._nodes = None
        self._parent = None

    def add_library(self, library):
        raise NotImplementedError('Not implemented for interface')

    def is_valid(self):
        raise NotImplementedError('Not implemented for interface')

    @property
    def uri(self):
        return self._uri

    @property
    def name(self):
        return self._name

    def hierarchical_name(self):
        raise NotImplementedError('Not implemented for interface')

    @property
    def libraries(self):
        return self._libraries

    @property
    def nodes(self):
        return self._nodes

    @property
    def tags(self):
        return self._tags

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value


class LibraryNodeInterface(object):

    def __init__(self):
        super(LibraryNodeInterface, self).__init__()
        self._name = None
        self._hierarchical_name = None
        self._author = None
        self._description = None
        self._copyright = None
        self._version = None
        self._tags = None
        self._library = None
        self._has_svg_icon = None
        self._has_docs = None
        self._html_docs = None
        self._html_base_uri = None
        self._svg_icon_data = None
        self._node_identifier = None
        self._icon = None
        self._parameter_model = None
        self._parent = None
        self._source_uri = None
        self._class_name = None
        self._inputs = None
        self._outputs = None
        self._path = None
        self._parent = None
        self._type = None
        self._deprecated = None
        self._needs_validate = True
        self._ok = True
        self._port_definition = {}

    @property
    def name(self):
        return self._name

    @property
    def hierarchical_name(self):
        return self._hierarchical_name

    @property
    def author(self):
        return self._author

    @property
    def description(self):
        return self._description

    @property
    def copyright(self):
        return self._copyright

    @property
    def deprecated(self):
        return self._deprecated

    @property
    def version(self):
        return self._version

    @property
    def tags(self):
        return self._tags

    @property
    def library(self):
        return self._library

    @property
    def has_svg_icon(self):
        return self._has_svg_icon

    @property
    def has_docs(self):
        return self._has_docs

    @property
    def html_docs(self):
        return self._html_docs

    @property
    def html_base_uri(self):
        return self._html_base_uri

    @property
    def svg_icon_data(self):
        return self._svg_icon_data

    @property
    def node_identifier(self):
        return self._node_identifier

    @property
    def icon(self):
        return self._icon

    @property
    def parameter_model(self):
        return self._parameter_model

    @parameter_model.setter
    def parameter_model(self, value):
        self._parameter_model = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def source_uri(self):
        return self._source_uri

    @property
    def class_name(self):
        return self._class_name

    @property
    def reload(self):
        raise NotImplementedError('Not implemented for interface')

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def type(self):
        return self._type

    @property
    def ok(self):
        return self._ok

    @property
    def path(self):
        return self._path

    @property
    def needs_validate(self):
        return self._needs_validate

    @property
    def port_definition(self):
        return self._port_definition


class LibraryNode(LibraryNodeInterface):

    def __init__(self, parent_library):
        super(LibraryNode, self).__init__()

    def reload(self):
        pass

    # Complete mock-up at this point
    @classmethod
    def from_uri(cls, uri, library):
        node = cls(library)
        node._uri = uri
        definition = ''
        node._set_definition(definition)
        return node

    @classmethod
    def from_definition(cls, parent_library, definition):
        node = cls(parent_library)
        node._name = definition['label']
        node._type = definition['type']

        node._author = definition['author']
        node._description = definition['description']
        node._copyright = definition['copyright']
        node._version = definition['version']
        node._tags = definition.get('tags', None)
        node._deprecated = definition.get('deprecated')
        node._needs_validate = definition.get('validate', True)

        try:
            node._library = definition['library']
        except KeyError:
            # If node definition doesn't include library keyword (probably
            # means that the node definitions was read from a 1.0 workflow)
            # and the node is not found in any known library set it
            # library to an empty string.
            node._library = ''
        try:
            node._source_uri = definition['file']
        except KeyError:
            node._source_uri = ''
            core_logger.warn('Node "%s" not found in libraries.',
                             node._name)
            node._needs_validate = False
            node._ok = False
        node._icon = definition.get('icon', None)

        if not node._icon:
            node._icon = localuri(util.icon_path('missing.svg'))

        try:
            with open_url(node._icon, 'rb') as f:
                svg_data = f.read()
            node._has_svg_icon = True
            node._svg_icon_data = QtCore.QByteArray(svg_data)
        except Exception as e:
            print('Could not open icon file {} ({})'.format(node._icon,
                  node._source_uri))
            print(e)

        node._html_base_uri = definition.get('docs', '')
        node._node_identifier = definition['id']
        node._parameter_model = ParameterModel.from_dict(
            definition['parameters'])
        node._class_name = definition.get('class', None)
        node._path = [
            part for part in os.path.dirname(
                uri_to_path(node._source_uri)[
                    len(uri_to_path(node._library)):]).split(os.path.sep)
            if len(part) > 0]
        node._inputs = []
        node._port_definition = definition['ports']

        inputs = definition['ports'].get('inputs', [])
        outputs = definition['ports'].get('outputs', [])
        inputs, outputs = port_util.instantiate(inputs, outputs, {})

        node._inputs = []
        for idx, port in enumerate(inputs):

            node._inputs.append(PortDefinition(
                port.get('name', ''), port['description'], port['type'],
                port['scheme'], idx, port.get('requiresdata', False)))

        node._outputs = []
        for idx, port in enumerate(outputs):
            node._outputs.append(PortDefinition(
                port.get('name', ''), port['description'], port['type'],
                port['scheme'], idx, port.get('requiresdata', False)))

        return node

    def _set_definition(self, definition):
        global node_id
        self._name = 'Node #{}'.format(node_id)
        self._author = 'Greger Cronquist <greger.cronquist@combine.se>'
        self._description = 'A node'
        self._copyright = (
            '(c) Copyright 2013 Combine Control Systems AB')
        self._version = '1.0'
        self._has_svg_icon = False
        self._has_docs = False
        self._html_docs = None
        self._html_base_uri = None
        self._svg_icon_data = None
        self._node_identifier = 'org.sysess.node_example_{}'.format(node_id)
        self._icon = None
        self._parameter_model = ParameterModel()
        self._parent = None
        self._source_uri = None
        self._class_name = 'NodeExample{}'.format(node_id)
        self._outputs = []
        for idx in range((node_id % 3)):
            self._inputs.append(PortDefinition('port{}'.format(idx),
                                'Input Port {}'.format(idx), 'Table', 'hdf5',
                                               idx, False))
        self._outputs = []
        for idx in range(((node_id + 1) % 3)):
            self._outputs.append(PortDefinition('port{}'.format(idx),
                                                'Output Port {}'.format(idx),
                                                'Table', 'hdf5', idx, False))
        node_id += 1


class Library(LibraryInterface):

    def __init__(self, name=None):
        super(Library, self).__init__()
        self.clear()
        self._name = name
        self._nodes = []

    def add_library(self, library):
        self._libraries.append(library)
        library.parent = self

    def add_node(self, node):
        self._nodes.append(node)
        node.parent = self

    def is_valid(self):
        return True

    def hierarchical_name(self):
        pass

    @property
    def name(self):
        return self._name

    @classmethod
    def from_uri(cls, uri, parent=None):
        library = cls()
        library._uri = uri
        # # library._parent = parent
        # # TODO(stefan): What is this???
        # for idx in range(10):
        #     node = LibraryNode(library)
        #     node._set_definition('A definition')
        #     library._nodes.append(node)
        # definition = ''
        library._set_definition('')
        return library

    @classmethod
    def from_dict(cls, dictionary, parent=None):
        library = cls()
        library._uri = 'Unknown'

        for definition in dictionary.values():
            try:
                node = LibraryNode.from_definition(library, definition)
                library._nodes.append(node)
            except:
                core_logger.warn('Node "%s" could not be added to library.',
                                 (definition or {}).get('id'))
        library._set_definition('')

        try:
            node = six.next(iter(dictionary.values()))
            name = node['file'][len(node['library']):].split('/')[1]
            library._name = name.title()
            library._uri = node['library']
        except (KeyError, StopIteration):
            pass
        return library

    def _set_definition(self, definition):
        self._name = 'Unknown'

    def clear(self):
        self._libraries = []
        self._nodes = []
        self._name = ''
        self._parent = None
        self._uri = ''


class RootLibrary(Library):
    def __init__(self):
        super(RootLibrary, self).__init__()
        self._tags = None

    def set_tags(self, tags):
        self._tags = tags

    def clear(self):
        super(RootLibrary, self).clear()
        self._tags = None


class LibraryManager(QtCore.QObject):
    library_added = QtCore.Signal()
    output_message = QtCore.Signal(six.text_type)
    library_output = QtCore.Signal(six.text_type, node_result.NodeResult)
    library_aliases = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(LibraryManager, self).__init__(parent)
        self._root_library = RootLibrary()
        self._node_registry = {}
        self._root_library._name = 'Root'
        self._library_manager = None
        self._library_data = None

    def reload_library(self):
        """Reload libraries using the library manager"""
        settings_instance = settings.instance()
        install_folder = settings_instance['install_folder']

        self._library_manager = library_manager.LibraryManager(
            install_folder,
            settings_instance['storage_folder'],
            util.python_paths(),
            util.library_paths(),
            settings_instance['temp_folder'],
            settings_instance['session_folder'])

        tags, lib, aliases = self.get_library_data()
        self.library_output.emit(
            'Library Creator',
            self._library_manager.library_creator_result())
        self.set_library_data(tags, lib, aliases)

    def set_library_data(self, tags, lib, aliases):
        self.clear()
        self._library_data = (tags, lib, aliases)
        library = Library.from_dict(lib)
        if tags:
            tags = LibraryTags.from_dict(tags)
        else:
            tags = None

        for k, v in aliases.items():
            datatypes.register_datatype(k, v['icon'])

        self._root_library.set_tags(tags)
        self._root_library.add_library(library)
        self._register_library(library)
        self.library_added.emit()
        self.library_aliases.emit(aliases)

    def get_library_data(self, update=True):
        if not update and self._library_data:
            return self._library_data

        tags = self._library_manager.library_tags()
        lib = self._library_manager.library_by_nodeid()
        aliases = self._library_manager.typealiases()
        return tags, lib, aliases

    def reload_documentation(self, venv=False, folder=None):
        self._library_manager.create_library_doc(
            self._root_library, venv, folder=folder)

    def get_documentation_builder(self):
        return self._library_manager.get_documentation_builder(
            self._root_library)

    def add_library(self, library_uri):
        library = Library.from_uri(library_uri)
        self._register_library(library)
        self._root_library.add_library(library)

    def set_tags(self, tags):
        self._tags = tags

    def clear(self):
        self._node_registry.clear()
        self._root_library.clear()
        self._root_library._name = 'Root'
        self._root_library._tags = None

    def _in_libraries(node):
        pass

    def is_in_library(self, node_identifier, libraries=None):
        node = self._node_registry.get(node_identifier)
        if node is not None:
            return libraries is None or (
                os.path.normcase(os.path.abspath(
                    os.path.dirname(uri_to_path(node.library))))
                in libraries)
        return False

    def library_node_from_definition(self, node_identifier, definition):
        try:
            node = LibraryNode.from_definition(None, definition)
            return node
        except:
            core_logger.warn('Node "%s" could not be added to library.',
                             node_identifier)

    def library_node(self, node_identifier):
        return self._node_registry[node_identifier]

    def register_node(self, node_identifier, node):
        if node_identifier not in self._node_registry:
            self._node_registry[node_identifier] = node

    def unregister_node(self, node_identifier):
        if node_identifier in self._node_registry:
            del self._node_registry[node_identifier]

    def root(self):
        return self._root_library

    def typealiases(self):
        return self._library_manager.typealiases()

    def _register_library(self, library):
        for node in library.nodes:
            self.register_node(node.node_identifier, node)

        for library_ in library.libraries:
            self._register_library(library_)
