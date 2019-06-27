# copyright 2004-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""RQL syntax tree nodes.

This module defines all the nodes we can find in a RQL Syntax tree, except
root nodes, defined in the `stmts` module.
"""

__docformat__ = "restructuredtext en"

import sys
from decimal import Decimal
from datetime import datetime, date, time, timedelta

from six import string_types

from rql import CoercionError, RQLException
from rql.base import BaseNode, Node, BinaryNode, LeafNode
from rql.utils import (function_description, uquote, common_parent,
                       VisitableMixIn)

CONSTANT_TYPES = frozenset((None, 'Date', 'Datetime', 'Boolean', 'Float', 'Int',
                            'String', 'Substitute', 'etype'))


ETYPE_PYOBJ_MAP = {bool: 'Boolean',
                   int: 'Int',
                   float: 'Float',
                   Decimal: 'Decimal',
                   str: 'String',
                   datetime: 'Datetime',
                   date: 'Date',
                   time: 'Time',
                   timedelta: 'Interval',
                   }
if sys.version_info < (3,):
    ETYPE_PYOBJ_MAP[long] = 'Int' # noqa
    ETYPE_PYOBJ_MAP[unicode] = 'String' # noqa

KEYWORD_MAP = {'NOW': datetime.now,
               'TODAY': date.today}


def etype_from_pyobj(value):
    """guess yams type from python value"""
    # note:
    # * Password is not selectable so no problem
    # * use type(value) and not value.__class__ since C instances may have no
    #   __class__ attribute
    return ETYPE_PYOBJ_MAP[type(value)]


def variable_ref(var):
    """get a VariableRef"""
    if isinstance(var, Variable):
        return VariableRef(var, noautoref=1)
    assert isinstance(var, VariableRef)
    return var


def variable_refs(node):
    for vref in node.iget_nodes(VariableRef):
        if isinstance(vref.variable, Variable):
            yield vref


class OperatorExpressionMixin(object):

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        return (self.operator,)

    def is_equivalent(self, other):
        if not Node.is_equivalent(self, other):
            return False
        return self.operator == other.operator

    def get_description(self, mainindex, tr):
        """if there is a variable in the math expr used as rhs of a relation,
        return the name of this relation, else return the type of the math
        expression
        """
        try:
            return tr(self.get_type())
        except CoercionError:
            for vref in self.iget_nodes(VariableRef):
                vtype = vref.get_description(mainindex, tr)
                if vtype != 'Any':
                    return tr(vtype)


class HSMixin(object):
    """mixin class for classes which may be the lhs or rhs of an expression"""
    __slots__ = ()

    def relation(self):
        """return the parent relation where self occurs or None"""
        try:
            return self.parent.relation()
        except AttributeError:
            return None

    def get_description(self, mainindex, tr):
        mytype = self.get_type()
        if mytype != 'Any':
            return tr(mytype)
        return 'Any'


# rql st edition utilities ####################################################

def make_relation(var, rel, rhsargs, rhsclass, operator='='):
    """build an relation equivalent to '<var> rel = <cst>'"""
    cmpop = Comparison(operator)
    cmpop.append(rhsclass(*rhsargs))
    relation = Relation(rel)
    if hasattr(var, 'variable'):
        var = var.variable
    relation.append(VariableRef(var))
    relation.append(cmpop)
    return relation


def make_constant_restriction(var, rtype, value, ctype, operator='='):
    if ctype is None:
        ctype = etype_from_pyobj(value)
    if isinstance(value, (set, frozenset, tuple, list, dict)):
        if len(value) > 1:
            rel = make_relation(var, rtype, ('IN',), Function, operator)
            infunc = rel.children[1].children[0]
            for atype in sorted(value):
                infunc.append(Constant(atype, ctype))
            return rel
        value = next(iter(value))
    return make_relation(var, rtype, (value, ctype), Constant, operator)


class EditableMixIn(object):
    """mixin class to add edition functionalities to some nodes, eg root nodes
    (statement) and Exists nodes
    """
    __slots__ = ()

    @property
    def undo_manager(self):
        return self.root.undo_manager

    @property
    def should_register_op(self):
        root = self.root
        # root is None during parsing
        return root is not None and root.should_register_op

    def remove_node(self, node, undefine=False):
        """remove the given node from the tree

        USE THIS METHOD INSTEAD OF .remove to get correct variable references
        handling
        """
        # unregister variable references in the removed subtree
        parent = node.parent
        stmt = parent.stmt
        for varref in node.iget_nodes(VariableRef):
            varref.unregister_reference()
            if undefine and not varref.variable.stinfo['references']:
                stmt.undefine_variable(varref.variable)
        # remove return actually removed node and its parent
        node, parent, index = parent.remove(node)
        if self.should_register_op:
            from rql.undo import RemoveNodeOperation
            self.undo_manager.add_operation(RemoveNodeOperation(node, parent, stmt, index))

    def add_restriction(self, relation):
        """add a restriction relation"""
        r = self.where
        if r is not None:
            newnode = And(r, relation)
            self.set_where(newnode)
            if self.should_register_op:
                from rql.undo import ReplaceNodeOperation
                self.undo_manager.add_operation(ReplaceNodeOperation(r, newnode))
        else:
            self.set_where(relation)
            if self.should_register_op:
                from rql.undo import AddNodeOperation
                self.undo_manager.add_operation(AddNodeOperation(relation))
        return relation

    def add_constant_restriction(self, var, rtype, value, ctype,
                                 operator='='):
        """builds a restriction node to express a constant restriction:

        variable rtype = value
        """
        restr = make_constant_restriction(var, rtype, value, ctype, operator)
        return self.add_restriction(restr)

    def add_relation(self, lhsvar, rtype, rhsvar):
        """builds a restriction node to express '<var> eid <eid>'"""
        return self.add_restriction(make_relation(lhsvar, rtype, (rhsvar,),
                                                  VariableRef))

    def add_eid_restriction(self, var, eid, c_type='Int'):
        """builds a restriction node to express '<var> eid <eid>'"""
        assert c_type in ('Int', 'Substitute'), "Error got c_type=%r in eid restriction" % c_type
        return self.add_constant_restriction(var, 'eid', eid, c_type)

    def add_type_restriction(self, var, etype):
        """builds a restriction node to express : variable is etype"""
        typerel = var.stinfo.get('typerel', None)
        if typerel:
            if typerel.r_type == 'is':
                istarget = typerel.children[1].children[0]
                if isinstance(istarget, Constant):
                    etypes = (istarget.value,)
                else:  # Function (IN)
                    etypes = [et.value for et in istarget.children]
                if isinstance(etype, string_types):
                    restr_etypes = {etype}
                else:
                    restr_etypes = set(etype)
                if restr_etypes - set(etypes):
                    raise RQLException('%r not a subset of %r'
                                       % (restr_etypes, etypes))
                if len(etypes) > 1:
                    # iterate a copy of children because it's modified inplace
                    for child in istarget.children[:]:
                        if child.value not in restr_etypes:
                            typerel.stmt.remove_node(child)
                return typerel
            else:
                assert typerel.r_type == 'is_instance_of'
                typerel.stmt.remove_node(typerel)
        return self.add_constant_restriction(var, 'is', etype, 'etype')


# base RQL nodes ##############################################################

class SubQuery(BaseNode):
    """WITH clause"""
    __slots__ = ('aliases', 'query')

    def __init__(self, aliases=None, query=None):
        if aliases is not None:
            self.set_aliases(aliases)
        if query is not None:
            self.set_query(query)

    def set_aliases(self, aliases):
        self.aliases = aliases
        for node in aliases:
            node.parent = self

    def set_query(self, node):
        self.query = node
        node.parent = self

    def copy(self, stmt):
        return SubQuery([v.copy(stmt) for v in self.aliases], self.query.copy())

    @property
    def children(self):
        return self.aliases + [self.query]

    def as_string(self, kwargs=None):
        return '%s BEING (%s)' % (','.join(v.name for v in self.aliases),
                                  self.query.as_string(kwargs=kwargs))

    def __repr__(self):
        return '%s BEING (%s)' % (','.join(repr(v) for v in self.aliases),
                                  repr(self.query))


class And(BinaryNode):
    """a logical AND node (binary)"""
    __slots__ = ()

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        return '%s, %s' % (self.children[0].as_string(kwargs=kwargs),
                           self.children[1].as_string(kwargs=kwargs))

    def __repr__(self):
        return '%s AND %s' % (repr(self.children[0]), repr(self.children[1]))

    def ored(self, traverse_scope=False, _fromnode=None):
        return self.parent.ored(traverse_scope, _fromnode or self)

    def neged(self, traverse_scope=False, _fromnode=None):
        return self.parent.neged(traverse_scope, _fromnode or self)


class Or(BinaryNode):
    """a logical OR node (binary)"""
    __slots__ = ()

    def as_string(self, kwargs=None):
        return '(%s) OR (%s)' % (self.children[0].as_string(kwargs=kwargs),
                                 self.children[1].as_string(kwargs=kwargs))

    def __repr__(self):
        return '%s OR %s' % (repr(self.children[0]), repr(self.children[1]))

    def ored(self, traverse_scope=False, _fromnode=None):
        return self

    def neged(self, traverse_scope=False, _fromnode=None):
        return self.parent.neged(traverse_scope, _fromnode or self)


class Not(Node):
    """a logical NOT node (unary)"""
    __slots__ = ()

    def __init__(self, expr=None):
        Node.__init__(self)
        if expr is not None:
            self.append(expr)

    def as_string(self, kwargs=None):
        if isinstance(self.children[0], (Exists, Relation)):
            return 'NOT %s' % self.children[0].as_string(kwargs=kwargs)
        return 'NOT (%s)' % self.children[0].as_string(kwargs=kwargs)

    def __repr__(self, encoding=None, kwargs=None):
        return 'NOT (%s)' % repr(self.children[0])

    def ored(self, traverse_scope=False, _fromnode=None):
        # XXX consider traverse_scope ?
        return self.parent.ored(traverse_scope, _fromnode or self)

    def neged(self, traverse_scope=False, _fromnode=None, strict=False):
        return self

    def remove(self, child):
        return self.parent.remove(self)

# def parent_scope_property(attr):
#     def _get_parent_attr(self, attr=attr):
#         return getattr(self.parent.scope, attr)
#     return property(_get_parent_attr)
# # editable compatibility
# for method in ('remove_node', 'add_restriction', 'add_constant_restriction',
#                'add_relation', 'add_eid_restriction', 'add_type_restriction'):
#     setattr(Not, method, parent_scope_property(method))


class Exists(EditableMixIn, BaseNode):
    """EXISTS sub query"""
    __slots__ = ('query',)

    def __init__(self, restriction=None):
        if restriction is not None:
            self.set_where(restriction)
        else:
            self.query = None

    def copy(self, stmt):
        new = self.query.copy(stmt)
        return Exists(new)

    @property
    def children(self):
        return (self.query,)

    def append(self, node):
        assert self.query is None
        self.query = node
        node.parent = self

    def is_equivalent(self, other):
        if self is other:
            return True
        raise NotImplementedError

    def as_string(self, kwargs=None):
        content = self.query and self.query.as_string(kwargs=kwargs)
        return 'EXISTS(%s)' % content

    def __repr__(self):
        return 'EXISTS(%s)' % repr(self.query)

    def set_where(self, node):
        self.query = node
        node.parent = self

    @property
    def where(self):
        return self.query

    def replace(self, oldnode, newnode):
        assert oldnode is self.query
        self.query = newnode
        newnode.parent = self
        return oldnode, self, None

    def remove(self, child):
        return self.parent.remove(self)

    @property
    def scope(self):
        return self

    def ored(self, traverse_scope=False, _fromnode=None):
        if not traverse_scope:
            if _fromnode is not None:  # stop here
                return False
            return self.parent.ored(traverse_scope, self)
        return self.parent.ored(traverse_scope, _fromnode)

    def neged(self, traverse_scope=False, _fromnode=None, strict=False):
        if not traverse_scope:
            if _fromnode is not None:  # stop here
                return False
            return self.parent.neged(self)
        elif strict:
            return isinstance(self.parent, Not)
        return self.parent.neged(traverse_scope, _fromnode)


class Relation(Node):
    """a RQL relation"""
    __slots__ = ('r_type', 'optional',
                 '_q_sqltable', '_q_needcast')  # XXX cubicweb specific

    def __init__(self, r_type, optional=None):
        Node.__init__(self)
        self.r_type = r_type
        self.optional = None
        self.set_optional(optional)

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        return self.r_type, self.optional

    def is_equivalent(self, other):
        if not Node.is_equivalent(self, other):
            return False
        if self.r_type != other.r_type:
            return False
        return True

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        try:
            lhs = self.children[0].as_string(kwargs=kwargs)
            if self.optional in ('left', 'both'):
                lhs += '?'
            rhs = self.children[1].as_string(kwargs=kwargs)
            if self.optional in ('right', 'both'):
                rhs += '?'
        except IndexError:
            return repr(self)  # not fully built relation
        return '%s %s %s' % (lhs, self.r_type, rhs)

    def __repr__(self):
        if self.optional:
            rtype = '%s[%s]' % (self.r_type, self.optional)
        else:
            rtype = self.r_type
        try:
            return 'Relation(%r %s %r)' % (self.children[0], rtype,
                                           self.children[1])
        except IndexError:
            return 'Relation(%s)' % self.r_type

    def set_optional(self, optional):
        assert optional in (None, 'left', 'right')
        if optional is not None:
            if self.optional and self.optional != optional:
                self.optional = 'both'
            else:
                self.optional = optional

    def relation(self):
        """return the parent relation where self occurs or None"""
        return self

    def ored(self, traverse_scope=False, _fromnode=None):
        return self.parent.ored(traverse_scope, _fromnode or self)

    def neged(self, traverse_scope=False, _fromnode=None, strict=False):
        if strict:
            return isinstance(self.parent, Not)
        return self.parent.neged(traverse_scope, _fromnode or self)

    def is_types_restriction(self):
        if self.r_type not in ('is', 'is_instance_of'):
            return False
        rhs = self.children[1]
        if isinstance(rhs, Comparison):
            rhs = rhs.children[0]
        # else: relation used in SET OR DELETE selection
        return ((isinstance(rhs, Constant) and rhs.type == 'etype')
                or (isinstance(rhs, Function) and rhs.name == 'IN'))

    def operator(self):
        """return the operator of the relation <, <=, =, >=, > and LIKE

        (relations used in SET, INSERT and DELETE definitions don't have
         an operator as rhs)
        """
        rhs = self.children[1]
        if isinstance(rhs, Comparison):
            return rhs.operator
        return '='

    def get_parts(self):
        """return the left hand side and the right hand side of this relation
        """
        lhs = self.children[0]
        rhs = self.children[1]
        return lhs, rhs

    def get_variable_parts(self):
        """return the left hand side and the right hand side of this relation,
        ignoring comparison
        """
        lhs = self.children[0]
        rhs = self.children[1].children[0]
        return lhs, rhs

    def change_optional(self, value):
        root = self.root
        if root is not None and root.should_register_op and value != self.optional:
            from rql.undo import SetOptionalOperation
            root.undo_manager.add_operation(SetOptionalOperation(self, self.optional))
        self.set_optional(value)


CMP_OPERATORS = frozenset(('=', '!=', '<', '<=', '>=', '>', 'ILIKE', 'LIKE', 'REGEXP'))


class Comparison(HSMixin, Node):
    """handle comparisons:

     <, <=, =, >=, > LIKE and ILIKE operators have a unique children.
    """
    __slots__ = ('operator', 'optional')

    def __init__(self, operator, value=None, optional=None):
        Node.__init__(self)
        if operator == '~=':
            operator = 'ILIKE'
        assert operator in CMP_OPERATORS, operator
        self.operator = operator
        self.optional = optional
        if value is not None:
            self.append(value)

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        return (self.operator, None, self.optional)

    def set_optional(self, left, right):
        if left and right:
            self.optional = 'both'
        elif left:
            self.optional = 'left'
        elif right:
            self.optional = 'right'

    def is_equivalent(self, other):
        if not Node.is_equivalent(self, other):
            return False
        return self.operator == other.operator

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        if len(self.children) == 0:
            return self.operator
        if len(self.children) == 2:
            lhsopt = rhsopt = ''
            if self.optional in ('left', 'both'):
                lhsopt = '?'
            if self.optional in ('right', 'both'):
                rhsopt = '?'
            return '%s%s %s %s%s' % (self.children[0].as_string(kwargs=kwargs),
                                     lhsopt, self.operator,
                                     self.children[1].as_string(kwargs=kwargs), rhsopt)
        if self.operator == '=':
            return self.children[0].as_string(kwargs=kwargs)
        return '%s %s' % (self.operator,
                          self.children[0].as_string(kwargs=kwargs))

    def __repr__(self):
        return '%s %s' % (self.operator, ', '.join(repr(c) for c in self.children))


class MathExpression(OperatorExpressionMixin, HSMixin, BinaryNode):
    """Mathematical Operators"""
    __slots__ = ('operator',)

    def __init__(self, operator, lhs=None, rhs=None):
        BinaryNode.__init__(self, lhs, rhs)
        self.operator = operator

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        return '(%s %s %s)' % (self.children[0].as_string(kwargs=kwargs),
                               self.operator,
                               self.children[1].as_string(kwargs=kwargs))

    def __repr__(self):
        return '(%r %s %r)' % (self.children[0], self.operator,
                               self.children[1])

    def get_type(self, solution=None, kwargs=None):
        """return the type of object returned by this function if known

        solution is an optional variable/etype mapping
        """
        lhstype = self.children[0].get_type(solution, kwargs)
        rhstype = self.children[1].get_type(solution, kwargs)
        key = (self.operator, lhstype, rhstype)
        try:
            return {('-', 'Date', 'Datetime'): 'Interval',
                    ('-', 'Date', 'TZDatetime'): 'Interval',
                    ('-', 'Date', 'Date'): 'Interval',
                    ('-', 'Datetime', 'Datetime'): 'Interval',
                    ('-', 'Datetime', 'TZDatetime'): 'Interval',
                    ('-', 'Datetime', 'Date'): 'Interval',
                    ('-', 'TZDatetime', 'Datetime'): 'Interval',
                    ('-', 'TZDatetime', 'TZDatetime'): 'Interval',
                    ('-', 'TZDatetime', 'Date'): 'Interval',

                    ('-', 'Date', 'Interval'):     'Datetime',
                    ('+', 'Date', 'Interval'):     'Datetime',
                    ('-', 'Datetime', 'Interval'): 'Datetime',
                    ('+', 'Datetime', 'Interval'): 'Datetime',
                    ('-', 'TZDatetime', 'Interval'): 'TZDatetime',
                    ('+', 'TZDatetime', 'Interval'): 'TZDatetime',
                    }[key]
        except KeyError:
            if lhstype == rhstype and 'Date' not in str(lhstype):
                return rhstype
            if sorted((lhstype, rhstype)) == ['Float', 'Int']:
                return 'Float'
            raise CoercionError(key)


class UnaryExpression(OperatorExpressionMixin, Node):
    """Unary Operators"""
    __slots__ = ('operator',)

    def __init__(self, operator, child=None):
        Node.__init__(self)
        self.operator = operator
        if child is not None:
            self.append(child)

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        return '%s%s' % (self.operator,
                         self.children[0].as_string(kwargs=kwargs))

    def __repr__(self):
        return '%s%r' % (self.operator, self.children[0])

    def get_type(self, solution=None, kwargs=None):
        """return the type of object returned by this expression if known

        solution is an optional variable/etype mapping
        """
        return self.children[0].get_type(solution, kwargs)


class Function(HSMixin, Node):
    """Class used to deal with aggregat functions (sum, min, max, count, avg)
    and latter upper(), lower() and other RQL transformations functions
    """
    __slots__ = ('name',)

    def __init__(self, name):
        Node.__init__(self)
        self.name = name.strip().upper()

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        return (self.name,)

    def is_equivalent(self, other):
        if not Node.is_equivalent(self, other):
            return False
        return self.name == other.name

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        return '%s(%s)' % (self.name, ', '.join(c.as_string(kwargs=kwargs)
                                                for c in self.children))

    def __repr__(self):
        return '%s(%s)' % (self.name, ', '.join(repr(c) for c in self.children))

    def get_type(self, solution=None, kwargs=None):
        """return the type of object returned by this function if known

        solution is an optional variable/etype mapping
        """
        func_descr = self.descr()
        rtype = func_descr.rql_return_type(self)
        if rtype is None:
            # XXX support one variable ref child
            try:
                rtype = solution and solution.get(self.children[0].name)
            except AttributeError:
                pass
        return rtype or 'Any'

    def get_description(self, mainindex, tr):
        return self.descr().st_description(self, mainindex, tr)

    def descr(self):
        """return the type of object returned by this function if known"""
        return function_description(self.name)


class Constant(HSMixin, LeafNode):
    """String, Int, TRUE, FALSE, TODAY, NULL..."""
    __slots__ = ('value', 'type', 'uid', 'uidtype')

    def __init__(self, value, c_type, _uid=False, _uidtype=None):
        assert c_type in CONSTANT_TYPES, "Error got c_type="+repr(c_type)
        LeafNode.__init__(self)  # don't care about Node attributes
        self.value = value
        self.type = c_type
        # updated by the annotator/analyzer if necessary
        self.uid = _uid
        self.uidtype = _uidtype

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        return (self.value, self.type, self.uid, self.uidtype)

    def is_equivalent(self, other):
        if not LeafNode.is_equivalent(self, other):
            return False
        return self.type == other.type and self.value == other.value

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string (an unicode string is
        returned if encoding is None)
        """
        if self.type is None:
            return 'NULL'
        if self.type in ('etype', 'Date', 'Datetime', 'Int', 'Float'):
            return str(self.value)
        if self.type == 'Boolean':
            return self.value and 'TRUE' or 'FALSE'
        if self.type == 'Substitute':
            # XXX could get some type information from self.root().schema()
            #     and linked relation
            if kwargs is not None:
                value = kwargs.get(self.value, '???')
                if isinstance(value, string_types):
                    value = uquote(value)
                else:
                    value = repr(value)
                return value
            return '%%(%s)s' % self.value
        if isinstance(self.value, string_types):
            return uquote(self.value)
        return repr(self.value)

    def __repr__(self):
        s = self.as_string()
        s = s.encode('unicode_escape') if sys.version_info < (3,) else s
        return s

    def eval(self, kwargs):
        if self.type == 'Substitute':
            return kwargs[self.value]
        if self.type in ('Date', 'Datetime'):  # TODAY, NOW
            return KEYWORD_MAP[self.value]()
        return self.value

    def get_type(self, solution=None, kwargs=None):
        if self.uid:
            return self.uidtype
        if self.type == 'Substitute':
            if kwargs is not None:
                return etype_from_pyobj(self.eval(kwargs))
            return 'String'
        return self.type


class VariableRef(HSMixin, LeafNode):
    """a reference to a variable in the syntax tree"""
    __slots__ = ('variable', 'name')

    def __init__(self, variable, noautoref=None):
        LeafNode.__init__(self)  # don't care about Node attributes
        self.variable = variable
        self.name = variable.name
        if noautoref is None:
            self.register_reference()

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        var = self.variable
        if isinstance(var, ColumnAlias):
            newvar = stmt.get_variable(self.name, var.colnum)
        else:
            newvar = stmt.get_variable(self.name)
        newvar.init_copy(var)
        return (newvar,)

    def is_equivalent(self, other):
        if not LeafNode.is_equivalent(self, other):
            return False
        return self.name == other.name

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        return self.name

    def __repr__(self):
        return 'VarRef(%r)' % self.variable

    def register_reference(self):
        self.variable.register_reference(self)

    def unregister_reference(self):
        self.variable.unregister_reference(self)

    def get_type(self, solution=None, kwargs=None):
        return self.variable.get_type(solution, kwargs)

    def get_description(self, mainindex, tr):
        return self.variable.get_description(mainindex, tr)

    def root_selection_index(self):
        """return the index of this variable reference *in the root selection*
        if it's selected, else None
        """
        myidx = self.variable.selected_index()
        if myidx is None:
            return None
        stmt = self.stmt
        union = stmt.parent
        if union.parent is None:
            return myidx
        # first .parent is the SubQuery node, we want the Select node
        parentselect = union.parent.parent
        for ca in parentselect.aliases.values():
            if ca.query is union and ca.colnum == myidx:
                caidx = ca.selected_index()
                if caidx is None:
                    return None
                return parentselect.selection[caidx].root_selection_index()


class SortTerm(Node):
    """a sort term bind a variable to the boolean <asc>
    if <asc> ascendant sort
    else descendant sort
    """
    __slots__ = ('asc',)

    def __init__(self, variable, asc=1, copy=None):
        Node.__init__(self)
        self.asc = asc
        if copy is None:
            self.append(variable)

    def initargs(self, stmt):
        """return list of arguments to give to __init__ to clone this node"""
        return (None, self.asc, True)

    def is_equivalent(self, other):
        if not Node.is_equivalent(self, other):
            return False
        return self.asc == other.asc

    def as_string(self, kwargs=None):
        if self.asc:
            return '%s' % self.term
        return '%s DESC' % self.term

    def __repr__(self):
        if self.asc:
            return '%r ASC' % self.term
        return '%r DESC' % self.term

    @property
    def term(self):
        return self.children[0]


###############################################################################

class Referenceable(VisitableMixIn):
    __slots__ = ('name', 'stinfo', 'stmt')

    def __init__(self, name):
        self.name = name.strip()
        # used to collect some global information about the syntax tree
        self.stinfo = {
            # link to VariableReference objects in the syntax tree
            'references': set(),
            }
        # reference to the selection
        self.stmt = None

    @property
    def schema(self):
        return self.stmt.root.schema

    def init_copy(self, old):
        # should copy variable's possibletypes on copy
        if not self.stinfo.get('possibletypes'):
            self.stinfo['possibletypes'] = old.stinfo.get('possibletypes')

    def as_string(self, kwargs=None):
        """return the tree as an encoded rql string"""
        return self.name

    def register_reference(self, vref):
        """add a reference to this variable"""
        self.stinfo['references'].add(vref)

    def unregister_reference(self, vref):
        """remove a reference to this variable"""
        try:
            self.stinfo['references'].remove(vref)
        except KeyError:
            # this may occur on hairy undoing
            pass

    def references(self):
        """return all references on this variable"""
        return tuple(self.stinfo['references'])

    def prepare_annotation(self):
        self.stinfo.update({
            'scope': None,
            # relations where this variable is used on the lhs/rhs
            'relations': set(),
            'rhsrelations': set(),
            # selection indexes if any
            'selected': set(),
            # type restriction (e.g. "is" / "is_instance_of") where this
            # variable is used on the lhs
            'typerel': None,
            # uid relations (e.g. "eid") where this variable is used on the lhs
            'uidrel': None,
            # if this variable is an attribute variable (ie final entity), link
            # to the (prefered) attribute owner variable
            'attrvar': None,
            # constant node linked to an uid variable if any
            'constnode': None,
            })
        # remove optional st infos
        for key in ('optrelations', 'blocsimplification', 'ftirels'):
            self.stinfo.pop(key, None)

    def _set_scope(self, key, scopenode):
        if scopenode is self.stmt or self.stinfo[key] is None:
            self.stinfo[key] = scopenode
        elif not (self.stinfo[key] is self.stmt or scopenode is self.stinfo[key]):
            self.stinfo[key] = common_parent(self.stinfo[key], scopenode).scope

    def set_scope(self, scopenode):
        self._set_scope('scope', scopenode)

    def get_scope(self):
        return self.stinfo['scope']
    scope = property(get_scope, set_scope)

    def add_optional_relation(self, relation):
        try:
            self.stinfo['optrelations'].add(relation)
        except KeyError:
            self.stinfo['optrelations'] = set((relation,))

    def get_type(self, solution=None, kwargs=None):
        """return entity type of this object, 'Any' if not found"""
        if solution:
            return solution[self.name]
        if self.stinfo['typerel']:
            rhs = self.stinfo['typerel'].children[1].children[0]
            if isinstance(rhs, Constant):
                return str(rhs.value)
        schema = self.schema
        if schema is not None:
            for rel in self.stinfo['rhsrelations']:
                try:
                    lhstype = rel.children[0].get_type(solution, kwargs)
                    return schema.eschema(lhstype).destination(rel.r_type)
                except Exception:  # CoertionError, AssertionError :(
                    pass
        return 'Any'

    def get_description(self, mainindex, tr, none_allowed=False):
        """return :
        * the name of a relation where this variable is used as lhs,
        * the entity type of this object if specified by a 'is' relation,
        * 'Any' if nothing nicer has been found...

        give priority to relation name
        """
        if mainindex is not None:
            if mainindex in self.stinfo['selected']:
                return ', '.join(sorted(
                    tr(etype) for etype in self.stinfo['possibletypes']))
        rtype = frtype = None
        schema = self.schema
        for rel in self.stinfo['relations']:
            if schema is not None:
                rschema = schema.rschema(rel.r_type)
                if rschema.final:
                    if self.name == rel.children[0].name:
                        # ignore final relation where this variable is used as subject
                        continue
                    # final relation where this variable is used as object
                    frtype = rel.r_type
            rtype = rel.r_type
            lhs, rhs = rel.get_variable_parts()
            # use getattr, may not be a variable ref (rewritten, constant...)
            rhsvar = getattr(rhs, 'variable', None)
            if mainindex is not None:
                # relation to the main variable, stop searching
                lhsvar = getattr(lhs, 'variable', None)
                context = None
                if lhsvar is not None and mainindex in lhsvar.stinfo['selected']:
                    if len(lhsvar.stinfo['possibletypes']) == 1:
                        context = next(iter(lhsvar.stinfo['possibletypes']))
                    return tr(rtype, context=context)
                if rhsvar is not None and mainindex in rhsvar.stinfo['selected']:
                    if len(rhsvar.stinfo['possibletypes']) == 1:
                        context = next(iter(rhsvar.stinfo['possibletypes']))
                    if schema is not None and rschema.symmetric:
                        return tr(rtype, context=context)
                    return tr(rtype + '_object', context=context)
            if rhsvar is self:
                rtype += '_object'
        if frtype is not None:
            return tr(frtype)
        if mainindex is None and rtype is not None:
            return tr(rtype)
        if none_allowed:
            return None
        return ', '.join(sorted(
            tr(etype) for etype in self.stinfo['possibletypes']))

    def selected_index(self):
        """return the index of this variable in the selection if it's selected,
        else None
        """
        if not self.stinfo['selected']:
            return None
        return next(iter(self.stinfo['selected']))

    def main_relation(self):
        """Return the relation where this variable is used in the rhs.

        It is useful for cases where this variable is final and we are
        looking for the entity to which it belongs.
        """
        for ref in self.references():
            rel = ref.relation()
            if rel is None:
                continue
            if rel.r_type != 'is' and self.name != rel.children[0].name:
                return rel
        return None

    def valuable_references(self):
        """return the number of "valuable" references :
        references is in selection or in a non type (is) relations
        """
        stinfo = self.stinfo
        return len(stinfo['selected']) + len(stinfo['relations'])


class ColumnAlias(Referenceable):
    __slots__ = ('colnum', 'query',
                 '_q_sql', '_q_sqltable')  # XXX cubicweb specific

    def __init__(self, alias, colnum, query=None):
        super(ColumnAlias, self).__init__(alias)
        self.colnum = int(colnum)
        self.query = query

    def __repr__(self):
        return 'alias %s' % self.name

    def get_type(self, solution=None, kwargs=None):
        """return entity type of this object, 'Any' if not found"""
        vtype = super(ColumnAlias, self).get_type(solution, kwargs)
        if vtype == 'Any':
            for select in self.query.children:
                vtype = select.selection[self.colnum].get_type(solution, kwargs)
                if vtype != 'Any':
                    return vtype
        return vtype

    def get_description(self, mainindex, tr):
        """return entity type of this object, 'Any' if not found"""
        vtype = super(ColumnAlias, self).get_description(mainindex, tr,
                                                         none_allowed=True)
        if vtype is None:
            vtypes = set()
            for select in self.query.children:
                vtype = select.selection[self.colnum].get_description(mainindex, tr)
                if vtype is not None:
                    vtypes.add(vtype)
            if vtypes:
                return ', '.join(sorted(vtype for vtype in vtypes))
        return vtype


class Variable(Referenceable):
    """
    a variable definition, should not be directly added to the syntax tree (use
    VariableRef instead)

    collects information about a variable use in a syntax tree
    """
    __slots__ = ('_q_invariant', '_q_sql', '_q_sqltable')  # XXX ginco specific

    def __repr__(self):
        return '%s' % self.name
