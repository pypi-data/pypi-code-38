# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import functools
import collections
import copy
import weakref
import six
import numpy as np

from . import data_manager
from .icons import SvgIcon
from . import plugins
from . import editor_type
from . import scales
from . import patterns
from sympathy.utils import uuid_generator


COLOR_SCALES = ['cubehelix', 'rainbow', 'blues', 'yellow-green-blue', 'summer',
                'pink', 'brown and blue', 'red and blue']


class NodeTags(object):
    """
    Tags for giving nodes different properties. Used for updating bounded
    things.
    """

    data_reference = 0
    root = 1
    editable = 2
    is_container = 3
    is_rearrangable = 4
    is_deletable = 5


def reference_setter(root, property_, value):
    """
    Setter function for ID which needs to be updated.
    :param root:  Root node.
    :param value: Parameter node.
    """
    old_value = property_.editor.get()

    def update_references(node):
        if (NodeTags.data_reference in node.tags and
                node.editor.get() == old_value):
            node.editor.set(value)
        for child in node.children:
            update_references(child)

    property_.set(value)
    update_references(root)


def remove_node(node):
    """
    Remove node from its parent.
    :param node: Node to be removed.
    """
    if node.parent is not None:
        node.parent.remove_child(node)


def insert_node(node, parent_node, position=None):
    """
    Insert node with the given parent. An exception is thrown if the node type
    is not allowed as a child of the parent node.
    :param node: Node to be added as child.
    :param parent_node: Parent-to-be of node.
    :param position: Position to insert node at.
    """
    if node.__class__ not in parent_node.valid_children:
        raise TypeError('{} is not valid child of {}'.
                        format(node.__class__, parent_node.__class__))
    if position is None:
        parent_node.insert_child(len(parent_node.children), node)
    else:
        parent_node.insert_child(position, node)
    node.parent = parent_node


def move_node(node, new_parent_node, position=None):
    """
    Move node to new parent node.
    :param node: Node to move.
    :param new_parent_node: New parent node.
    :param position: Child position at new parent.
    """
    remove_node(node)
    insert_node(node, new_parent_node, position)


def is_parent_same_node(parent, node):
    """
    Check if the parent, or any of its parents, is equal to the given node.
    :param parent: Parent to start checking for.
    :param node: Node to check for equality.
    :return: True if there is a parent which is equal to the node.
    """
    if parent is None:
        return False
    if parent == node:
        return True
    return is_parent_same_node(parent.parent, node)


# TODO(stefan): These functions should probably be related to the default
#               data structure of each class instead.
def create_empty_data():
    """
    Create empty data structure.
    :return: Dictionary containing empty data structure.
    """
    s = {
        'type': 'root',
        'sytype': 'report',
        'version': 1,
        'signals': [],
        'scales': [],
        'pages': []
    }
    return s


def create_empty_scale(model_node):
    """
    Create empty scale.
    :param model_node: A model node to access model.
    """
    # Find a free unique scale name.
    scale_list = list_of_scales(model_node, filter_type_compatibility=False)
    n = 1
    scale_id = 'scale1'
    while scale_id in scale_list:
        n += 1
        scale_id = 'scale{}'.format(n)

    s = {
        'id': scale_id,
        'type': 'linear',
        'domain': [-1, 1],
        'extent': False,
        'range': [-1, 1],
    }
    return s


def list_of_scales(property_node, filter_type_compatibility=True):
    """
    Generate a list of available scales.
    :param property_node: A node in the data model, must be Property to filter.
    :param filter_type_compatibility: Keep items which are compatible.
    :return: List of strings with name of scales.
    """
    if filter_type_compatibility:
        assert (isinstance(property_node, Property))
    scale_node_list = property_node.find_all_nodes_with_class(RootScale)
    scale_list = []
    if filter_type_compatibility:
        property_is_color = isinstance(
            property_node.editor, (editor_type.Color, editor_type.ColorScale))
    for scale_node in scale_node_list:
        properties = scale_node.properties_as_dict()
        range_value = properties['range'].get()
        if filter_type_compatibility:
            try:
                is_color = patterns.re_color.match(range_value[0]) is not None
            except TypeError:
                is_color = False
            if ((property_is_color and is_color) or
                    not (property_is_color or is_color)):
                scale_list.append(properties['id'].get())
        else:
            scale_list.append(properties['id'].get())
    return scale_list


def compress_signals(data_dict):
    """
    Compress signal list by removing entries in the signals list which cannot
    be found in the rest of the document.
    :param data_dict: data dict
    :return: compressed list of signals
    """
    found_signals = set()

    def search(signal_name, node):
        if isinstance(node, six.string_types):
            if node == signal_name:
                found_signals.add(signal_name)
        elif isinstance(node, collections.Sequence):
            for item in node:
                search(signal_name, item)
        elif isinstance(node, collections.Mapping):
            for value in six.itervalues(node):
                search(signal_name, value)

    for signal in data_dict['signals']:
        search(signal, data_dict['pages'])

    return list(found_signals)


class AbstractNode(object):
    """Abstract base for all nodes."""

    icon = SvgIcon.blank
    # TODO(stefan): Replace this with some kind of schema for flexibility.
    valid_children = frozenset()
    default_data = None
    weak_parent = None

    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        self.children = []
        self.properties = []
        self.tags = set()
        self.init()

    def init(self):
        pass

    @property
    def parent(self):
        return self.weak_parent() if self.weak_parent is not None else None

    @parent.setter
    def parent(self, value):
        self.weak_parent = weakref.ref(value) if value is not None else None

    @classmethod
    def create_empty_instance(cls, parent=None):
        if cls.default_data is not None:
            return cls(copy.deepcopy(cls.default_data), parent=parent)

    def find_node_by_python_id(self, python_id):
        """
        Find object instance of node given its Python id.
        :param python_id: Python id.
        :return: Object if found, None otherwise.
        """
        current_node = self.root_node()
        if id(current_node) == python_id:
            return current_node

        def search(x):
            for n in x.children:
                if id(n) == python_id:
                    return n
                else:
                    result = search(n)
                    if result is not None:
                        return result
            return None

        return search(current_node)

    def root_node(self):
        """
        Find root node.
        :return: Root node.
        """
        if NodeTags.root in self.tags:
            return self
        else:
            return self.parent.root_node()

    def root_data(self):
        """
        Find data of root node.
        :return: Root node data.
        """
        return self.root_node().data

    def find_node(self, node_class, node_id, parent_node=None):
        """
        Search recursively for a node with the given class and ID.
        :param node_class: Class of node.
        :param node_id: String containing ID to search for.
        :param parent_node: Node to search from.
        :return: Found node or None.
        """
        if parent_node is None:
            parent_node = self.root_node()

        for child in parent_node.children:
            if isinstance(child, node_class) and child.data['id'] == node_id:
                return child
            if child.has_children():
                sub_child = self.find_node(node_class, node_id, child)
                if sub_child is not None:
                    return sub_child
        return None

    def find_all_nodes_with_class(self, node_class, parent_node=None):
        """
        Search recursively for all nodes of a given class.
        :param node_class: Class of node.
        :param parent_node: Node to search from.
        :return: List of found nodes.
        """
        found = []
        if parent_node is None:
            parent_node = self.root_node()

        for child in parent_node.children:
            if isinstance(child, node_class):
                found.append(child)
            if child.has_children():
                sub_child = self.find_all_nodes_with_class(node_class, child)
                found.extend(sub_child)
        return found

    def find_child_property(self, property_id):
        """
        Search for child property among children of this node.
        :param property_id: Id of property.
        :return: Property object or None.
        """
        for p in self.properties:
            if p.property == property_id:
                return p
        return None

    def properties_as_dict(self):
        """
        Return all properties which are direct children as a dict.
        :return: Dict with properties.
        """
        property_dict = collections.OrderedDict()
        for p in self.properties:
            property_dict[p.property] = p
        return property_dict

    def remove_child(self, node):
        raise NotImplementedError()

    def insert_child(self, position, node):
        raise NotImplementedError()

    @property
    def label(self):
        """Return label to be visualized in tree."""
        raise NotImplementedError

    def has_children(self):
        """Return True if the node has any children."""
        return self.row_count() > 0

    def row_count(self):
        """Return the number of children."""
        return len(self.children)

    def child(self, row):
        """Return child number."""
        return self.children[row]

    def index(self, child):
        """Return index of child."""
        return self.children.index(child)


class AbstractLeaf(AbstractNode):
    """Convenience class describing a leaf node."""

    def row_count(self):
        return 0


class Property(AbstractLeaf):
    """A general property which can be edited."""

    def __init__(self, parameters, parent=None):
        """
        Property constructor.
        :param parameters: Dictionary containing label, property, icon,
                           editor, data, getter_function and setter_function.
                           'label' visual label for property.
                           'property' is property name.
                           'icon' is icon of property.
                           'editor' is editor specification for property.
                           'data' is pointer to parent object in data
                           structure where property can be found.
                           'getter' is getter function of value (optional).
                           'setter' is setter function of value (optional).
                           'scale_bindable' is True if it is possible to bind
                           the property to a scale (optional).
                           'scale_binding' is a scales.ScaleBinding object
                           (optional).
        :param parent: Parent object.
        """
        super(Property, self).__init__(parameters['data'], parent)
        self._label = parameters['label']
        self.property = parameters['property']
        self.icon = parameters['icon']
        self.getter = parameters.get('getter', None)
        self.setter = parameters.get('setter', None)
        self.tags.add(NodeTags.editable)

        self.scale_binding = parameters.get('scale_binding', None)
        self.scale_bindable = parameters.get('scale_bindable', False)
        # Used as a memory if enabling a scale again.
        self.last_scale_binding = self.scale_binding

        # Editors has to be initialized last since they depend on consistent
        # data in this object.
        self.editor = parameters['editor']
        self.editor.property_object = self
        self.editor.init()

    @property
    def label(self):
        return self._label

    def get(self):
        if self.is_bindable:
            return (self.data[self.property]['value']
                    if self.getter is None else self.getter())
        return (self.data.get(self.property, None)
                if self.getter is None else self.getter())

    def set(self, value):
        if self.setter is None:
            if self.is_bindable:
                self.data[self.property]['value'] = value
            else:
                self.data[self.property] = value
        else:
            self.setter(value)

    def set_scale_binding(self, data_name, scale_name):
        if not self.scale_bindable:
            raise RuntimeError('Binding a scale is not possible on this '
                               'property.')
        # TODO(stefan): Check that the scale is valid.
        self.scale_binding = scales.ScaleBinding(data_name, scale_name)
        self.last_scale_binding = self.scale_binding

        self.data[self.property]['binding'] = (
            None if self.scale_binding is None else
            self.scale_binding.as_dict())

    def clear_scale_binding(self):
        self.scale_binding = None
        self.data[self.property]['binding'] = None

    def has_valid_binding(self):
        # TODO(stefan): Add type constraint (numeric or color).
        if self.scale_binding is None:
            return False
        data_list = data_manager.data_source.signal_list()
        if self.scale_binding.data_id not in data_list:
            return False
        scale_list = list_of_scales(self)
        if self.scale_binding.scale_id not in scale_list:
            return False
        return True

    @property
    def is_bindable(self):
        return self.scale_bindable

    @property
    def has_binding(self):
        return self.scale_binding is not None

    def invalidate_scale(self, scale_name):
        """Invalidate a scale by e.g. removing a reference to it."""
        if (self.scale_binding is not None and
                self.scale_binding.scale_id == scale_name):
            self.clear_scale_binding()
            self.last_scale_binding = None
        else:
            # TODO(stefan): This could be dangerous.
            if self.get() == scale_name:
                self.set('')


class Root(AbstractNode):
    """Root node."""

    def init(self):
        self.valid_children = {RootScales, Pages}
        self.tags.add(NodeTags.root)
        self.children = []

        # Build up children member gradually
        if self.data:
            root_scales = RootScales(self.data['scales'], self)
            self.children = (root_scales,)
            pages = Pages(self.data['pages'], self)
            self.children = (root_scales, pages)


class RootScales(AbstractNode):
    """Container of all defined scales in root."""

    icon = SvgIcon.scales

    def init(self):
        self.valid_children = {RootScale}
        self.children = [RootScale(data, self) for data in self.data]

    @property
    def label(self):
        return 'Scales'

    def remove_child(self, node):
        self.data.remove(node.data)
        self.children.remove(node)
        node.parent = None

        def search_and_replace(value, n):
            for p in n.properties:
                p.invalidate_scale(value)
            for child in n.children:
                search_and_replace(value, child)

        # Also find all instances of the scale in the data tree and clear them.
        scale_id = node.data['id']
        search_and_replace(scale_id, self.root_node())

    def insert_child(self, position, node):
        self.data.insert(position, node.data)
        self.children.insert(position, node)


class RootScale(AbstractNode):
    """Definition of scale in Root -> Scales -> ..."""

    icon = SvgIcon.scales

    SCALE_PROPERTIES = (
        ('Id', 'id', SvgIcon.text, editor_type.String),
        ('Type', 'type', SvgIcon.config, editor_type.ImmutableList),
        ('Domain', 'domain', SvgIcon.ruler, editor_type.String),
        ('Range', 'range', SvgIcon.ruler, editor_type.String),
        ('Extent', 'extent', SvgIcon.blank, editor_type.Boolean)
    )

    def init(self):
        self.tags.add(NodeTags.is_deletable)

        for label_, property_, icon, editor in self.SCALE_PROPERTIES:
            if property_ == 'type':
                # TODO(stefan): This data should not be hard coded.
                options = lambda: scales.SCALE_TYPES  # noqa
            else:
                options = lambda: None  # noqa

            prop = Property({'label': label_,
                             'property': property_,
                             'icon': icon,
                             'editor': editor(options),
                             'data': self.data},
                            parent=self)

            if property_ == 'id':
                prop.editor.set = functools.partial(
                    reference_setter, self.root_node(), prop)
                prop.editor.tags.add(
                    editor_type.EditorTags.force_update_after_edit)
            elif property_ in ('domain', 'range', 'extent'):
                prop.editor.tags.add(
                    editor_type.EditorTags.force_rebuild_after_edit)

            self.properties.append(prop)

    @property
    def label(self):
        return 'Scale ({})'.format(self.data['id'])

    def create_scale(self, extent_data=None):
        p = self.properties_as_dict()
        if p['extent'].get() and extent_data is None:
            raise ValueError('extent_data must be provided when extent is '
                             'enabled.')
        if not p['extent'].get():
            return scales.create_scale(p['type'].get(),
                                       p['domain'].get(),
                                       p['range'].get())
        else:
            domain = np.linspace(extent_data.min(),
                                 extent_data.max(),
                                 len(p['range'].get()))
            return scales.create_scale(p['type'].get(),
                                       domain,
                                       p['range'].get())


class Pages(AbstractNode):
    """Root node for all pages. Root -> Pages"""

    icon = SvgIcon.pages

    def init(self):
        self.valid_children = {Page}
        self.tags.add(NodeTags.is_container)

        for page in self.data:
            self.children.append(
                VIEW_TO_CLASS[page['type']](page, parent=self))

    @property
    def label(self):
        return 'Pages'

    def remove_child(self, node):
        self.data.remove(node.data)
        self.children.remove(node)

    def insert_child(self, position, node):
        self.data.insert(position, node.data)
        self.children.insert(position, node)


class Page(AbstractNode):
    """Page definition. Root -> Pages -> ..."""

    icon = SvgIcon.page
    # Check rebuild_widgets in gui.py for comments regarding adding a unique
    # identifier to each page.
    default_data = {
        'type': 'page',
        'title': 'New Page',
        'content': None
    }

    def init(self):
        # Make sure that the page has a unique identifier.
        self.data.setdefault('uuid', uuid_generator.generate_uuid())

        # Storage for page thumbnail.
        self.data.setdefault('thumbnail')

        self.tags.add(NodeTags.is_deletable)

        self.valid_children = {Layout}
        content = self.data['content']
        if content is not None:
            self.children.append(
                VIEW_TO_CLASS[content[0]['type']](content[0], parent=self))
        self.tags.add(NodeTags.is_container)
        self.tags.add(NodeTags.is_rearrangable)

        prop = Property({'label': 'Title',
                         'property': 'title',
                         'icon': SvgIcon.label,
                         'editor': editor_type.String(),
                         'data': self.data},
                        parent=self)
        # this line only updates the page tree view
        prop.editor.tags.add(editor_type.EditorTags.force_update_after_edit)
        self.properties.append(prop)

    @property
    def uuid(self):
        return self.data['uuid']

    def update_uuid(self):
        self.data['uuid'] = uuid_generator.generate_uuid()

    @property
    def label(self):
        return self.data['title']

    @property
    def thumbnail(self):
        return self.data['thumbnail']

    @thumbnail.setter
    def thumbnail(self, value):
        self.data['thumbnail'] = value

    def insert_child(self, position, node):
        if len(self.children) == 1:
            raise RuntimeError('A page may only have one child.')
        self.data['content'] = [node.data]
        self.children.insert(position, node)

    def remove_child(self, node):
        self.data['content'] = None
        self.children.remove(node)


class Layout(AbstractNode):
    """Definition of layout in a page."""

    icon = SvgIcon.layout
    default_data = {
        'type': 'layout',
        'kind': 'horizontal',
        'items': None
    }
    layout_kinds = [
        'horizontal',
        'vertical'
    ]

    def init(self):
        self.tags.add(NodeTags.is_rearrangable)
        self.tags.add(NodeTags.is_deletable)

        self.valid_children = {Layout, Graph, TextBox, Image}

        if self.data['items'] is None:
            self.data['items'] = []

        editor = editor_type.ImmutableList(lambda: self.layout_kinds)
        editor.tags.add(editor_type.EditorTags.force_rebuild_after_edit)

        self.properties.append(Property({'label': 'Kind',
                                         'property': 'kind',
                                         'icon': SvgIcon.blank,
                                         'editor': editor,
                                         'data': self.data},
                                        parent=self))
        for item in self.data['items']:
            self.children.append(VIEW_TO_CLASS[item['type']](item, self))
        self.tags.add(NodeTags.is_container)
        self.tags.add(NodeTags.is_rearrangable)

    @property
    def label(self):
        return 'Layout ({})'.format(self.data['kind'])

    def remove_child(self, node):
        self.data['items'].remove(node.data)
        self.children.remove(node)

    def insert_child(self, position, node):
        self.data['items'].insert(position, node.data)
        self.children.insert(position, node)


class TextBox(AbstractNode):
    """Free text box."""

    icon = SvgIcon.text
    default_data = {
        'type': 'textbox',
        'id': 'new-textbox',
        'text': '<Replace me>',
        'halign': 'center',
        'valign': 'center',
        'width': 0,
        'height': 0
    }

    TEXTBOX_NODE_PROPERTIES = (
        ('Id', 'id', SvgIcon.text, editor_type.String),
        ('Horizontal Alignment', 'halign', SvgIcon.blank,
            editor_type.ImmutableList),
        ('Vertical Alignment', 'valign', SvgIcon.blank,
            editor_type.ImmutableList),
        ('Width', 'width', SvgIcon.text, editor_type.Integer),
        ('Height', 'height', SvgIcon.text, editor_type.Integer),
        ('Text (HTML allowed)', 'text', SvgIcon.text,
            editor_type.MultiLineString)
    )

    def init(self):
        self.tags.add(NodeTags.is_deletable)
        self.tags.add(NodeTags.is_rearrangable)

        for label, property_, icon, editor_class in (
                self.TEXTBOX_NODE_PROPERTIES):
            if property_ in ('halign',):
                editor = editor_class(lambda: ('left', 'center', 'right'))
            elif property_ in ('valign',):
                editor = editor_class(lambda: ('top', 'center', 'bottom'))
            else:
                editor = editor_class()
            prop = Property({'label': label,
                             'property': property_,
                             'icon': icon,
                             'editor': editor,
                             'data': self.data})
            if property_ in ('id', 'text'):
                editor.tags.add(editor_type.EditorTags.force_update_after_edit)
            if property_ in ('width', 'height'):
                editor.value_range = {'min': 0, 'max': 100000, 'step': 10}
            self.properties.append(prop)

    @property
    def label(self):
        return 'Textbox ({})'.format(self.data['id'])


class Image(AbstractNode):
    """Static image node."""

    icon = SvgIcon.picture
    default_data = {
        'type': 'image',
        'id': 'new-image',
        'image': ''
    }

    IMAGE_NODE_PROPERTIES = (
        ('Id', 'id', SvgIcon.text, editor_type.String),
        ('Image', 'image', SvgIcon.picture, editor_type.Image)
    )

    def init(self):
        self.tags.add(NodeTags.is_deletable)
        self.tags.add(NodeTags.is_rearrangable)

        for label, property_, icon, editor_class in (
                self.IMAGE_NODE_PROPERTIES):
            editor = editor_class()
            prop = Property({'label': label,
                             'property': property_,
                             'icon': icon,
                             'editor': editor,
                             'data': self.data})
            if property_ in ('id',):
                editor.tags.add(editor_type.EditorTags.force_update_after_edit)
            if property_ in ('image',):
                editor.tags.add(
                    editor_type.EditorTags.force_rebuild_after_edit)
            self.properties.append(prop)

    @property
    def label(self):
        return 'Image ({})'.format(self.data['id'])


class Graph(AbstractNode):
    """Definition of a graph in a page."""

    icon = SvgIcon.plot
    default_data = {
        'type': 'graph',
        'id': 'new-graph',
        'title': 'New Graph',
        'width': 400,
        'height': 400,
        'grid': False,
        'projection': 'cartesian',
        'dimensions': [
            [
                {
                    'id': 'x-axis',
                    'title': '',
                    'extent': True,
                    'min': 0.0,
                    'max': 1.0,
                    'scale_type': 'linear'
                }
            ],
            [
                {
                    'id': 'y-axis',
                    'title': '',
                    'extent': True,
                    'min': 0.0,
                    'max': 1.0,
                    'scale_type': 'linear'
                }
            ]
        ],
        'layers': []
    }
    projection_options = [
        'cartesian',
        'polar'
    ]

    GRAPH_NODE_PROPERTIES = (
        ('Id', 'id', SvgIcon.text, editor_type.String),
        ('Title', 'title', SvgIcon.text, editor_type.String),
        ('Width', 'width', SvgIcon.width, editor_type.Integer),
        ('Height', 'height', SvgIcon.height, editor_type.Integer),
        ('Grid', 'grid', SvgIcon.grid, editor_type.Boolean),
        ('Projection', 'projection', SvgIcon.projection,
         editor_type.ImmutableList)
    )

    def init(self):
        self.valid_children = {GraphLayers, GraphDimensions}
        self.tags.add(NodeTags.is_rearrangable)
        self.tags.add(NodeTags.is_deletable)

        for label, property_, icon, editor_class in self.GRAPH_NODE_PROPERTIES:
            if property_ == 'projection':
                # TODO(stefan): Extract this data out of code.
                options = lambda: self.projection_options  # noqa
            else:
                options = lambda: None  # noqa
            editor = editor_class(options)
            if property_ in ('projection',):
                editor.tags.add(
                    editor_type.EditorTags.force_rebuild_after_edit)
            if property_ in ('id',):
                editor.tags.add(editor_type.EditorTags.force_update_after_edit)
            prop = Property({'label': label,
                             'property': property_,
                             'icon': icon,
                             'editor': editor,
                             'data': self.data},
                            parent=self)
            if property_ in ('width', 'height'):
                editor.value_range = {'min': 0, 'max': 100000, 'step': 10}
            self.properties.append(prop)

        self.children.append(
            GraphDimensions(self.data['dimensions'], parent=self))
        self.children.append(GraphLayers(self.data['layers'], parent=self))

    @property
    def label(self):
        return 'Graph ({})'.format(self.data['id'])

    def layers(self):
        """Return a list of all layer objects."""
        layer_parent = None
        for child in self.children:
            if isinstance(child, GraphLayers):
                layer_parent = child

        if layer_parent is None:
            return None

        layers = []

        for child in layer_parent.children:
            if isinstance(child, GraphLayer):
                layers.append(child)

        return layers


class GraphDimensions(AbstractNode):
    """Container for dimensions of graph."""

    icon = SvgIcon.coordinates

    def init(self):
        self.valid_children = {GraphDimension}
        self.children = [GraphDimension(dimension, data, parent=self)
                         for dimension, data in enumerate(self.data)]

    @property
    def label(self):
        return 'Dimensions'

    def remove_child(self, node):
        self.data.remove(node.data)
        self.children.remove(node)

    def insert_child(self, position, node):
        self.data.insert(position, node.data)
        self.children.insert(position, node)


class GraphDimension(AbstractNode):
    """Definition of a graph dimension."""

    def __init__(self, dimension, data, parent):
        super(GraphDimension, self).__init__(data, parent)
        self.dimension_number = dimension
        dim = (SvgIcon.x_axis, SvgIcon.y_axis, SvgIcon.z_axis)
        self.icon = (dim[dimension] if dimension < 3 else SvgIcon.n_axis)

    def init(self):
        self.valid_children = {GraphAxis}
        self.children = [GraphAxis(data, parent=self) for data in self.data]

    @property
    def label(self):
        return 'Dimension {}'.format(self.dimension_number + 1)


class GraphAxis(AbstractNode):
    icon = SvgIcon.ruler

    AXIS_NODE_PROPERTIES = (
        ('Id', 'id', SvgIcon.text, editor_type.String),
        ('Title', 'title', SvgIcon.text, editor_type.String),
        ('Fit to data', 'extent', SvgIcon.blank, editor_type.Boolean),
        ('Min', 'min', SvgIcon.scales, editor_type.Float),
        ('Max', 'max', SvgIcon.scales, editor_type.Float),
        ('Scale', 'scale_type', SvgIcon.blank, editor_type.ImmutableList)
    )

    def __init__(self, data, parent):
        # Update old data model to newer model:
        if 'scale' in data:
            scale_id = data['scale']
            del data['scale']
            scale_model = parent.root_node().find_node(RootScale, scale_id)
            if scale_model:
                data['min'] = scale_model.data['domain'][0]
                data['max'] = scale_model.data['domain'][-1]
                data['extent'] = scale_model.data.get('extent', True)
                data['scale_type'] = scale_model.data['type']
            else:
                data['min'] = 0.0
                data['max'] = 1.0
                data['extent'] = True
                data['scale_type'] = 'linear'

        super(GraphAxis, self).__init__(data, parent)

    def init(self):
        for label, property_, icon, editor in self.AXIS_NODE_PROPERTIES:
            if property_ == 'scale_type':
                options = lambda: ['linear', 'log']  # noqa
            else:
                options = lambda: None  # noqa
            prop = Property({'label': label,
                             'property': property_,
                             'icon': icon,
                             'editor': editor(options),
                             'data': self.data},
                            parent=self)
            if property_ == 'id':
                # An id-change here should only propagate to stuff within
                # the graph, not the root.
                prop.editor.set = functools.partial(
                    reference_setter, self.parent.parent.parent, prop)
                prop.editor.tags.add(
                    editor_type.EditorTags.force_update_after_edit)

            self.properties.append(prop)

    @property
    def label(self):
        return 'Axis ({})'.format(self.data['id'])


class GraphLayers(AbstractNode):
    """Container for layers in graph."""

    icon = SvgIcon.layers

    def init(self):
        self.valid_children = {GraphLayer}
        self.children = [GraphLayer(data, parent=self) for data in self.data]
        self.tags.add(NodeTags.is_container)

    @property
    def label(self):
        return 'Layers'

    def remove_child(self, node):
        self.data.remove(node.data)
        self.children.remove(node)

    def insert_child(self, position, node):
        self.data.insert(position, node.data)
        self.children.insert(position, node)


class GraphLayer(AbstractNode):
    """Container for a layer."""

    icon = SvgIcon.layer
    layer = None
    # default_data = None   This is set before instantiated.

    def init(self):
        self.valid_children = {GraphLayerData}
        self.tags.add(NodeTags.is_rearrangable)
        self.tags.add(NodeTags.is_deletable)

        # First add all data specification nodes to the children.
        self.children = [GraphLayerData(self.data['data'], parent=self)]

        layer_type = self.data['type']
        try:
            # Fetch Layer class using the plugin framework for the given
            # layer type.
            layer = plugins.layer_modules[layer_type].layer.Layer()
        except KeyError:
            raise ValueError('Unknown layer type {}'.format(layer_type))
        layer_properties = layer.create_properties(layer_model=self,
                                                   property_class=Property)
        self.properties.extend(list(layer_properties.values()))

    @property
    def label(self):
        return '{} ({})'.format(
            self.data.get('name', '---'), self.data['type'])

    def extract_data_and_properties(self):
        """Convenience method for extracting data and properties from layer
        model.
        """
        # Extract all data source properties. Assuming one source per
        # dimension.
        data_source_properties = []
        # Loop through all children.
        for child_ in self.children:
            # If we have data...
            if isinstance(child_, GraphLayerData):
                # ...go through all dimensions...
                for data_dimension in child_.children:
                    # ...and all its properties...
                    for data_dimension_property in data_dimension.properties:
                        # ...and extract all data sources.
                        if data_dimension_property.property == 'source':
                            data_source_properties.append(
                                data_dimension_property)
        try:
            data = [data_manager.data_source.data(x.get())
                    for x in data_source_properties]
        except KeyError:
            data = [np.array([]) for _ in data_source_properties]
        except AttributeError:
            data = []
        if len(data_source_properties) == 0:
            data_source_properties = None
        return data, data_source_properties

    def extent_of_layer_data(self, dimension):
        """
        Extract extent (data range) of layer data for the given dimension.
        :param dimension: Dimension to extract extent for.
        :return: Tuple with (min, max). (0, 1) if the extent couldn't be
                 calculated.
        """
        for c1 in self.children:
            if isinstance(c1, GraphLayerData):
                try:
                    c_dim = c1.children[dimension]
                except IndexError:
                    return 0, 1
                properties = c_dim.properties_as_dict()
                data_source = properties['source'].get()
                try:
                    data = data_manager.data_source.data(data_source)
                except AttributeError:
                    return 0, 1
                try:
                    min_, max_ = np.nanmin(data), np.nanmax(data)
                except (ValueError, TypeError):
                    pass
                else:
                    if min_ is not None and max_ is not None:
                        if min_ == max_:
                            # zero length axes are no fun, so add a little bit
                            # wiggle room.
                            min_ = min_ - 0.5
                            max_ = max_ + 0.5
                        return min_, max_

        # Arbitrary default values to avoid breaking calculations.
        return 0, 1


class GraphLayerData(AbstractNode):
    """
    Data container containing information regarding what data is represented
    in a layer.
    """

    icon = SvgIcon.data

    def init(self):
        self.valid_children = {GraphLayerDataDimension}
        self.children = [GraphLayerDataDimension(dimension, data, parent=self)
                         for dimension, data in enumerate(self.data)]

    @property
    def label(self):
        return 'Data'


class GraphLayerDataDimension(AbstractNode):
    """Dimension binding for data in a layer."""

    BINDING_PROPERTIES = (
        ('Data Source', 'source', 'link', editor_type.DataSource),
        ('Axis', 'axis', 'ruler', editor_type.ImmutableList)
    )

    def __init__(self, dimension, data, parent):
        self.dimension = dimension
        super(GraphLayerDataDimension, self).__init__(data, parent)
        dim = (SvgIcon.x_axis, SvgIcon.y_axis, SvgIcon.z_axis)
        self.icon = (dim[dimension] if dimension < 3 else SvgIcon.n_axis)

    def init(self):
        for label, property_, icon, editor in self.BINDING_PROPERTIES:
            if property_ == 'source':
                options = lambda: [x['id'] for x in self.root_data()['data']]  # noqa
            elif property_ == 'axis':
                options = lambda: [x['id'] for x in  # noqa
                                   self.parent.parent.parent.parent.data[
                                       'dimensions'][self.dimension]]
            else:
                options = lambda: None  # noqa
            prop = Property({'label': label,
                             'property': property_,
                             'icon': icon,
                             'editor': editor(options),
                             'data': self.data},
                            parent=self)
            if property_ == 'source':
                prop.tags.add(NodeTags.data_reference)
                # Update is done by backend.
            elif property_ == 'axis':
                # Default to first available axis for this dimension
                options_list = options()
                if options_list and not prop.get():
                    prop.editor.set(options_list[0])

                prop.tags.add(NodeTags.data_reference)
                prop.editor.tags.add(
                    editor_type.EditorTags.force_rebuild_after_edit)
            self.properties.append(prop)

    @property
    def label(self):
        return 'Dimension {}'.format(
            self.dimension + 1)


class Label(AbstractLeaf):
    icon = SvgIcon.label

    @property
    def label(self):
        return 'Label ({})'.format(self.data['id'])


VIEW_TO_CLASS = {
    'layout': Layout,
    'pages': Pages,
    'page': Page,
    'textbox': TextBox,
    'image': Image,
    'graph': Graph,
    'layer': GraphLayer
}

NODE_DEPENDENCIES = {
    Page: ('pages',),
    Layout: ('page', 'layout'),
    TextBox: ('page', 'layout', 'textbox'),
    Image: ('page', 'layout', 'image'),
    Graph: ('page', 'layout', 'graph'),
    GraphLayer: ('page', 'layout', 'graph', 'layer')
}
