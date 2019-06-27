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
"""Comparing syntax trees.

"""
from __future__ import print_function

__docformat__ = "restructuredtext en"


from six.moves import range

from rql.nodes import VariableRef, Variable, Function, Relation, Comparison


def compare_tree(request1, request2):
    """Compares 2 RQL requests.

    :rtype: bool
    :return: True if both requests would return the same results.
    """
    return make_canon_dict(request1) == make_canon_dict(request2)


def make_canon_dict(rql_tree, verbose=0):
    """Return a canonical representation of the request as a dictionnary."""
    allvars = {}
    canon = {
        'all_variables': allvars,
        'selected': [],
        'restriction': {},
        }

    canon = RQLCanonizer().visit(rql_tree, canon)

    # forge variable name
    for var, name_parts in allvars.values():
        name_parts.sort()
        var.name = ':'.join(name_parts)
    sort(canon)
    if verbose:
        print('CANON FOR', rql_tree)
        from pprint import pprint
        pprint(canon)
    return canon


def sort(canon_dict):
    """Remove the all_variables entry and sort other entries in place."""
    del canon_dict['all_variables']
    canon_dict['selection'].sort()
    for values in canon_dict['restriction'].values():
        values.sort()


class SkipChildren(Exception):
    """Signal indicating to ignore the current child."""


class RQLCanonizer(object):
    """Build a dictionnary which represents a RQL syntax tree."""

    def visit(self, node, canon):
        try:
            node.accept(self, canon)
        except SkipChildren:
            return canon
        for c in node.children:
            self.visit(c, canon)
        return canon

    def visit_select(self, select, canon):
        allvars = canon['all_variables']
        for var in select.defined_vars.values():
            allvars[var] = (Variable(var.name), [])
        canon['selection'] = l = []
        selected = select.selected
        for i in range(len(selected)):
            node = selected[i]
            if isinstance(node, VariableRef):
                node = node.variable
                allvars[node][1].append(str(i))
                l.append(allvars[node][0])
            else:  # Function
                l.append(node)
                for var in node.iget_nodes(VariableRef):
                    var.parent.replace(var, allvars[var.variable][0])

    def visit_group(self, group, canon):
        canon['group'] = group

    def visit_sort(self, sort, canon):
        canon['sort'] = sort

    def visit_sortterm(self, sortterm, canon):
        pass

    def visit_and(self, et, canon):
        pass

    def visit_or(self, ou, canon):
        canon_dict = {}
        keys = []
        for expr in ou.get_nodes(Relation):
            key = '%s%s' % (expr.r_type, expr._not)
            canon_dict.setdefault(key, []).append(expr)
            keys.append(key)
        keys.sort()
        r_type = ':'.join(keys)
        r_list = canon['restriction'].setdefault(r_type, [])
        done = {}
        for key in keys:
            if key in done:
                continue
            done[key] = None
            for expr in canon_dict[key]:
                self.manage_relation(expr, canon, r_list)
        raise SkipChildren()

    def manage_relation(self, relation, canon, r_list):
        lhs, rhs = relation.get_parts()
        # handle special case of the IN function
        func = rhs.children[0]
        if isinstance(func, Function) and func.name == 'IN':
            if not relation._not:
                base_key = '%s%s' % (relation.r_type, relation._not)
                if not canon['restriction'][base_key]:
                    del canon['restriction'][base_key]
                key = ':'.join([base_key] * len(func.children))
                r_list = canon['restriction'].setdefault(key, [])
            for e in func.children:
                eq_expr = Relation(relation.r_type, relation._not)
                eq_expr.append(lhs)
                eq_expr.append(Comparison('=', e))
                self.manage_relation(eq_expr, canon, r_list)
                # restaure parent attribute to avoid problem later
                e.parent = func
                lhs.parent = relation
            return
        # build a canonical representation for this relation
        lhs_expr_reminder = make_lhs_reminder(lhs, canon)
        rhs_expr_reminder = make_rhs_reminder(rhs, canon)
        reminder = (lhs_expr_reminder, rhs_expr_reminder)
        # avoid duplicate
        if reminder in r_list:
            return
        r_list.append(reminder)
        # make a string which represents this relation (we'll use it later
        # to build variables' name)
        expr_reminder = relation.r_type
        lhs_vars = lhs.get_nodes(VariableRef)
        if not lhs_vars:
            expr_reminder = "%s_%s" % (lhs, expr_reminder)
        rhs_vars = rhs.get_nodes(VariableRef)
        if not rhs_vars:
            expr_reminder = "%s_%s" % (expr_reminder, rhs)

        for var in lhs_vars + rhs_vars:
            var = var.variable
            canon['all_variables'][var][1].append(expr_reminder)

    def visit_relation(self, relation, canon):
        key = '%s%s' % (relation.r_type, relation._not)
        r_list = canon['restriction'].setdefault(key, [])
        self.manage_relation(relation, canon, r_list)

    def visit_comparison(self, comparison, canon):
        """do nothing for this node type"""

    def visit_mathexpression(self, mathexpression, canon):
        """do nothing for this node type"""

    def visit_function(self, function, canon):
        """do nothing for this node type"""

    def visit_variableref(self, varref, canon):
        varref.parent.replace(varref,
                              canon['all_variables'][varref.variable][0])

    def visit_constant(self, constante, canon):
        """do nothing for this node type"""

    def visit_union(self, *args):
        raise NotImplementedError('union comparison not implemented')


def make_lhs_reminder(lhs, canon):
    """Return a reminder for a relation's left hand side
    (i.e a VariableRef object).
    """
    try:
        lhs = canon['all_variables'][lhs.variable][0]
    except (KeyError, IndexError):
        pass
    return ('=', lhs)


def make_rhs_reminder(rhs, canon):
    """Return a reminder for a relation's right hand side
    (i.e a Comparison object).
    """
    child = rhs.children[0]
    try:
        child = canon['all_variables'][child.variable][0]
    except AttributeError:
        pass
    return (rhs.operator, child)
