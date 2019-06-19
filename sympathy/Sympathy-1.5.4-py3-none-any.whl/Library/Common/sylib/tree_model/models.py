# Copyright (c) 2016, Combine Control Systems AB
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

import copy
import re
import weakref
from collections import OrderedDict

import six

from sylib.icons.utils import SvgIcon, create_icon


class NodeTags(object):
    """
    Tags for giving nodes different properties. Used for updating bounded
    things.
    """
    data_reference = 0
    root = 1
    editable = 2
    copyable = 3
    unique = 4
    is_container = 5
    rearrangable = 6
    deletable = 7


def remove_node(node):
    """
    Remove node from its parent.
    :param node: Node to be removed.
    """
    if node.parent is not None:
        node.parent.remove_child(node)


def insert_node(node, parent_node, position):
    """
    Insert node with the given parent. An exception is thrown if the node type
    is not allowed as a child of the parent node.
    :param node: Node to be added as child.
    :param parent_node: Parent-to-be of node.
    :param position: Position to insert node at.
    """
    if node.__class__ not in parent_node.valid_children():
        raise TypeError('{} is not valid child of {}'.format(
            node.__class__, parent_node.__class__))
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


def insert_into_ordereddict(data, node, position=0):
    """Insert a node into a OrderedDict ``data`` a ``position``."""
    keys = data.keys()
    if node.is_leaf:
        key = node.name
    else:
        key = node.node_type
    if key in keys:
        keys.remove(key)
    keys.insert(position, key)
    data = OrderedDict([(k, data.get(k, node.data)) for k in keys])
    return data


class BaseNode(object):
    """Base node for all nodes."""

    icon = SvgIcon.blank
    default_data = None  # or OrderedDict()
    weak_parent = None
    node_type = None
    is_leaf = False
    description = None
    cls_tags = frozenset()

    NODE_LEAFS = OrderedDict()
    REQUIRED_LEAFS = set()
    STORED_LEAFS = {}

    def __init__(self, data, parent=None):
        self.parent = parent
        self.children = []
        self.inst_tags = set()
        self.init_leafs(data)
        self.init(data)

    @classmethod
    def valid_children(cls):
        return set()

    def init(self, data):
        # Init general stuff here
        pass

    def init_leafs(self, data):
        for leaf, params in six.iteritems(self.NODE_LEAFS):
            l_data = data.pop(leaf, None)
            if l_data is not None or leaf in self.REQUIRED_LEAFS:
                leaf_inst = self.create_leaf(leaf, l_data, params=params)
                leaf_inst.parent = self
                self.children.insert(self.number_of_leafs(), leaf_inst)

    def create_leaf(self, leaf, data=None, params=None):
        if params is None:
            params = self.NODE_LEAFS.get(leaf)
        if data is None:
            data = params['default']
        # add the data to the model if required but not existing
        is_required = leaf in self.REQUIRED_LEAFS
        leaf_cls = RequiredProperty if is_required else Property
        leaf_inst = leaf_cls({'label': params['label'],
                              'name': leaf,
                              'eval': params['eval'],
                              'default': params['default'],
                              'icon': params['icon'],
                              'options': params['options'],
                              'editor': params['editor'],
                              'completer_name': params.get('completer_name',
                                                           'default'),
                              'description': params.get('description', ''),
                              'data': data},
                             parent=None)
        return leaf_inst

    def add_children_to_node(self, data, valid_child_nodes):
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child_data = data.pop(child_cls.node_type)
                child = child_cls(child_data, parent=self)
                self.children.append(child)

    @property
    def parent(self):
        return self.weak_parent() if self.weak_parent is not None else None

    @parent.setter
    def parent(self, parent):
        self.weak_parent = weakref.ref(parent) if parent is not None else None

    @classmethod
    def create_empty_instance(cls, parent=None):
        if cls.default_data is not None:
            return cls(copy.deepcopy(cls.default_data), parent=parent)

    @classmethod
    def prettify_class_name(cls):
        parts = [a for a in re.split(r'([A-Z][a-z]*)', cls.__name__) if a]
        return ' '.join(parts)

    @property
    def tags(self):
        # if class tags have to excluded for certain instances extend this to
        # exclude tags defined as 'exclude_tags' per instance
        return self.cls_tags.union(self.inst_tags)

    def set_data(self, value):
        raise NotImplementedError

    def get_icon(self):
        return create_icon(self.icon)

    def get_leaf_with_name(self, name):
        for c in self.children:
            if c.is_leaf and c.name == name:
                return c
        return None

    def get_child_class_for_type(self, type):
        for c in self.valid_children():
            if c.node_type == type:
                return c
        return None

    def get_insert_position(self, node, position=None):
        """
        Return a valid position for the given node.

        If position is given it will be taken into account. Override if a
        special ordering should be enforced for child nodes/leafs.
        """
        if position is None or position > len(self.children):
            position = len(self.children)
        return position

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
        """Find root node."""
        if NodeTags.root in self.tags:
            return self
        else:
            return self.parent.root_node()

    def find_first_parent_node_with_class(self, node_cls, start_node=None):
        """
        Search for the first occurance of a node_class walking up the tree.
        :param node_cls: Class of node to search for.
        :param start_node: Node to start searching from.
        :return: Found node or None.
        """
        if start_node is None:
            start_node = self
        if start_node is self.root_node():
            return None
        elif isinstance(start_node, node_cls):
            return start_node
        else:
            parent = self.find_first_parent_node_with_class(
                node_cls, start_node.parent)
            return parent

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

    def remove_child(self, node):
        self.children.remove(node)

    def insert_child(self, position, node):
        self.children.insert(position, node)

    def number_of_leafs(self):
        return sum(1 for c in self.children if c.is_leaf)

    @property
    def label(self):
        """Return label to be visualized in tree."""
        return self.prettify_class_name()

    @property
    def tooltip(self):
        return '<p>{}</p>'.format(self.description)

    def extra_label(self):
        return ''

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

    @property
    def editor(self):
        """Return the editor."""
        return None

    def valid_leafs(self):
        return self.NODE_LEAFS.keys()

    def available_leafs(self):
        d = [(p, self.NODE_LEAFS[p]) for p in self.valid_leafs()
             if self.get_leaf_with_name(p) is None]
        return d

    def _get_current_unique_children_types(self):
        return [type(c) for c in self.children if NodeTags.unique in c.tags]

    def get_available_children(self):
        current_uniques = self._get_current_unique_children_types()
        av_children = [c for c in self.valid_children()
                       if c not in current_uniques and not c.is_leaf]
        return av_children

    def export_config(self):
        raise NotImplementedError

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        for child in result.children:
            child.parent = result
        return result


class BaseLeaf(BaseNode):
    """Convenience class describing a leaf node."""

    is_leaf = True

    def __init__(self, data, parent=None):
        self.data = None
        self.name = None
        super(BaseLeaf, self).__init__(data, parent=parent)

    def init(self, data):
        self.data = data

    def init_leafs(self, data):
        pass

    def row_count(self):
        return 0

    @property
    def tooltip(self):
        if self.name:
            return '<p>{}</p>'.format(self.name)
        return None


class Property(BaseLeaf):
    """A general property which can be edited."""

    node_type = 'property'
    cls_tags = frozenset({NodeTags.editable, NodeTags.deletable})

    def __init__(self, parameters, parent=None):
        """
        Property constructor.
        :param parameters: Dictionary containing label, property, icon,
                           editor, data.
                           'label' visual label for property.
                           'name' is the property's name.
                           'icon' is the icon of the property.
                           'editor' is an editor specification of the property.
                           'data' is a pointer to parent object in data
                           structure where property can be found.
        :param parent: Parent object.
        """
        super(Property, self).__init__(parameters['data'], parent=parent)
        self._label = parameters['label']
        self.name = parameters['name']
        self.eval = parameters.get('eval', six.text_type)
        self.icon = parameters.get('icon')
        self.default = parameters.get('default')
        self.options = parameters.get('options')
        self._editor = parameters.get('editor')
        self.completer_name = parameters.get('completer_name', 'default')
        self.description = parameters.get('description',
                                          'No description available')

    def set_data(self, value):
        self.data = six.text_type(value)

    @property
    def tooltip(self):
        return '<p>{}</p>'.format(self.description)

    @property
    def label(self):
        return self._label

    @property
    def editor(self):
        """Return the editor."""
        return self._editor

    def export_config(self):
        return {self.name: self.data}


class RequiredProperty(Property):
    """A property which is not deletable."""
    cls_tags = frozenset({NodeTags.editable})


class BaseRoot(BaseNode):
    """An example Root node."""

    node_type = 'root'
    cls_tags = frozenset({NodeTags.root})
