# copyright 2004-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of rql.
#
# rql is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# rql is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with rql. If not, see <http://www.gnu.org/licenses/>.
"""Base classes for RQL syntax tree nodes.

Note: this module uses __slots__ to limit memory usage.
"""

__docformat__ = "restructuredtext en"

import sys

from rql.utils import VisitableMixIn


class BaseNode(VisitableMixIn):
    __slots__ = ('parent',)

    def __str__(self):
        s = self.as_string()
        s = s.encode('unicode_escape') if sys.version_info < (3,) else s
        return s

    def as_string(self, kwargs=None):
        """Return the tree as an encoded rql string."""
        raise NotImplementedError()

    def initargs(self, stmt):
        """Return list of arguments to give to __init__ to clone this node.

        I don't use __getinitargs__ because I'm not sure it should interfer with
        copy/pickle
        """
        return ()

    @property
    def root(self):
        """Return the root node of the tree"""
        return self.parent.root

    @property
    def stmt(self):
        """Return the Select node to which this node belong"""
        return self.parent.stmt

    @property
    def scope(self):
        """Return the scope node to which this node belong (eg Select or Exists
        node)
        """
        return self.parent.scope

    def get_nodes(self, klass):
        """Return the list of nodes of a given class in the subtree.

        :type klass: a node class (Relation, Constant, etc.)
        :param klass: the class of nodes to return

        :rtype: list
        """
        stack = [self]
        result = []
        while stack:
            node = stack.pop()
            if isinstance(node, klass):
                result.append(node)
            else:
                stack += node.children
        return result

    def iget_nodes(self, klass):
        """Return an iterator over nodes of a given class in the subtree.

        :type klass: a node class (Relation, Constant, etc.)
        :param klass: the class of nodes to return

        :rtype: iterator
        """
        stack = [self]
        while stack:
            node = stack.pop()
            if isinstance(node, klass):
                yield node
            else:
                stack += node.children

    def is_equivalent(self, other):
        if other.__class__ is not self.__class__:
            return False
        for i, child in enumerate(self.children):
            try:
                if not child.is_equivalent(other.children[i]):
                    return False
            except IndexError:
                return False
        return True

    def index_path(self):
        if self.parent is None:
            return []
        myindex = self.parent.children.index(self)
        parentindexpath = self.parent.index_path()
        parentindexpath.append(myindex)
        return parentindexpath

    def go_to_index_path(self, path):
        if not path:
            return self
        return self.children[path[0]].go_to_index_path(path[1:])

    def copy(self, stmt):
        """Create and return a copy of this node and its descendant.

        stmt is the root node, which should be use to get new variables
        """
        new = self.__class__(*self.initargs(stmt))
        for child in self.children:
            new.append(child.copy(stmt))
        return new


class Node(BaseNode):
    """Class for nodes of the tree which may have children (almost all...)"""
    __slots__ = ('children',)

    def __init__(self):
        self.parent = None
        self.children = []

    def append(self, child):
        """add a node to children"""
        self.children.append(child)
        child.parent = self

    def remove(self, child):
        """Remove a child node. Return the removed node, its old parent and
        index in the children list.
        """
        index = self.children.index(child)
        del self.children[index]
        parent = child.parent
        child.parent = None
        return child, parent, index

    def insert(self, index, child):
        """insert a child node"""
        self.children.insert(index, child)
        child.parent = self

    def replace(self, old_child, new_child):
        """replace a child node with another"""
        i = self.children.index(old_child)
        self.children.pop(i)
        self.children.insert(i, new_child)
        new_child.parent = self
        return old_child, self, i


class BinaryNode(Node):
    __slots__ = ()

    def __init__(self, lhs=None, rhs=None):
        Node.__init__(self)
        if lhs is not None:
            self.append(lhs)
        if rhs is not None:
            self.append(rhs)

    def remove(self, child):
        """Remove the child and replace this node with the other child."""
        index = self.children.index(child)
        return self.parent.replace(self, self.children[not index])

    def get_parts(self):
        """Return the left hand side and the right hand side of this node."""
        return self.children[0], self.children[1]


class LeafNode(BaseNode):
    """Class optimized for leaf nodes."""
    __slots__ = ()

    @property
    def children(self):
        return ()

    def copy(self, stmt):
        """Create and return a copy of this node and its descendant.

        stmt is the root node, which should be use to get new variables.
        """
        return self.__class__(*self.initargs(stmt))
