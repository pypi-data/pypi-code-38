# copyright 2004-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Miscellaneous utilities for RQL."""

from logilab.database import SQL_FUNCTIONS_REGISTRY, FunctionDescr, CAST
from logilab.common.decorators import monkeypatch

from rql._exceptions import BadRQLQuery

__docformat__ = "restructuredtext en"

UPPERCASE = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def decompose_b26(index, table=UPPERCASE):
    """Return a letter (base-26) decomposition of index."""
    div, mod = divmod(index, 26)
    if div == 0:
        return table[mod]
    return decompose_b26(div-1) + table[mod]


class rqlvar_maker(object):
    """Yields consistent RQL variable names.

    :param stop: optional argument to stop iteration after the Nth variable
                 default is None which means 'never stop'
    :param defined: optional dict of already defined vars
    """
    # NOTE: written a an iterator class instead of a simple generator to be
    #       picklable

    def __init__(self, stop=None, index=0, defined=None, aliases=None):
        self.index = index
        self.stop = stop
        self.defined = defined
        self.aliases = aliases

    def __iter__(self):
        return self

    def __next__(self):
        while self.stop is None or self.index < self.stop:
            var = decompose_b26(self.index)
            self.index += 1
            if self.defined is not None and var in self.defined:
                continue
            if self.aliases is not None and var in self.aliases:
                continue
            return var
        raise StopIteration()

    next = __next__


KEYWORDS = set(('INSERT', 'SET', 'DELETE',
                'UNION', 'WITH', 'BEING',
                'WHERE', 'AND', 'OR', 'NOT',
                'IN', 'LIKE', 'ILIKE', 'EXISTS', 'DISTINCT',
                'TRUE', 'FALSE', 'NULL', 'TODAY',
                'GROUPBY', 'HAVING', 'ORDERBY', 'ASC', 'DESC',
                'LIMIT', 'OFFSET'))


RQL_FUNCTIONS_REGISTRY = SQL_FUNCTIONS_REGISTRY.copy()


@monkeypatch(FunctionDescr)
def st_description(self, funcnode, mainindex, tr):
    return '%s(%s)' % (
        tr(self.name),
        ', '.join(sorted(child.get_description(mainindex, tr)
                         for child in iter_funcnode_variables(funcnode))))


@monkeypatch(FunctionDescr)
def st_check_backend(self, backend, funcnode):
    if not self.supports(backend):
        raise BadRQLQuery("backend %s doesn't support function %s" % (backend, self.name))


@monkeypatch(FunctionDescr)
def rql_return_type(self, funcnode):
    return self.rtype


@monkeypatch(CAST)
def st_description(self, funcnode, mainindex, tr):
    return self.rql_return_type(funcnode)


@monkeypatch(CAST)
def rql_return_type(self, funcnode):
    return funcnode.children[0].value


def iter_funcnode_variables(funcnode):
    for term in funcnode.children:
        try:
            yield term.variable.stinfo['attrvar'] or term
        except AttributeError:
            yield term


def is_keyword(word):
    """Return true if the given word is a RQL keyword."""
    return word.upper() in KEYWORDS


def common_parent(node1, node2):
    """return the first common parent between node1 and node2

    algorithm :
     1) index node1's parents
     2) climb among node2's parents until we find a common parent
    """
    # index node1's parents
    node1_parents = set()
    while node1:
        node1_parents.add(node1)
        node1 = node1.parent
    # climb among node2's parents until we find a common parent
    while node2:
        if node2 in node1_parents:
            return node2
        node2 = node2.parent
    raise Exception('DUH!')


def register_function(funcdef):
    RQL_FUNCTIONS_REGISTRY.register_function(funcdef)
    SQL_FUNCTIONS_REGISTRY.register_function(funcdef)


def function_description(funcname):
    """Return the description (:class:`FunctionDescr`) for a RQL function."""
    return RQL_FUNCTIONS_REGISTRY.get_function(funcname)


def quote(value):
    """Quote a string value."""
    res = ['"']
    for char in value:
        if char == '"':
            res.append('\\')
        res.append(char)
    res.append('"')
    return ''.join(res)


def uquote(value):
    """Quote a unicode string value."""
    res = ['"']
    for char in value:
        if char == u'"':
            res.append(u'\\')
        res.append(char)
    res.append(u'"')
    return u''.join(res)


class VisitableMixIn(object):

    def accept(self, visitor, *args, **kwargs):
        visit_id = self.__class__.__name__.lower()
        visit_method = getattr(visitor, 'visit_%s' % visit_id)
        return visit_method(self, *args, **kwargs)

    def leave(self, visitor, *args, **kwargs):
        visit_id = self.__class__.__name__.lower()
        visit_method = getattr(visitor, 'leave_%s' % visit_id)
        return visit_method(self, *args, **kwargs)


class RQLVisitorHandler(object):
    """Handler providing a dummy implementation of all callbacks necessary
    to visit a RQL syntax tree.
    """

    def visit_union(self, union):
        pass

    def visit_insert(self, insert):
        pass

    def visit_delete(self, delete):
        pass

    def visit_set(self, update):
        pass

    def visit_select(self, selection):
        pass

    def visit_sortterm(self, sortterm):
        pass

    def visit_and(self, et):
        pass

    def visit_or(self, ou):
        pass

    def visit_not(self, not_):
        pass

    def visit_relation(self, relation):
        pass

    def visit_comparison(self, comparison):
        pass

    def visit_mathexpression(self, mathexpression):
        pass

    def visit_function(self, function):
        pass

    def visit_variableref(self, variable):
        pass

    def visit_constant(self, constant):
        pass
