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
"""RQL Syntax tree annotator"""

__docformat__ = "restructuredtext en"

from logilab.common.graph import has_path
from logilab.database import UnknownFunction

from rql._exceptions import BadRQLQuery
from rql.utils import function_description
from rql.nodes import (Relation, VariableRef, Constant, Not, Exists, Function,
                       And, Comparison, variable_refs, make_relation)


def _var_graphid(subvarname, trmap, select):
    try:
        return trmap[subvarname]
    except KeyError:
        return subvarname + str(id(select))


def bloc_simplification(variable, term):
    try:
        variable.stinfo['blocsimplification'].add(term)
    except KeyError:
        variable.stinfo['blocsimplification'] = set((term,))


class GoTo(Exception):
    """Exception used to control the visit of the tree."""

    def __init__(self, node):
        self.node = node


VAR_SELECTED = 1
VAR_HAS_TYPE_REL = 2
VAR_HAS_UID_REL = 4
VAR_HAS_REL = 8


class STCheckState(object):
    def __init__(self):
        self.errors = []
        self.under_not = []
        self.var_info = {}

    def error(self, msg):
        self.errors.append(msg)

    def add_var_info(self, var, vi):
        try:
            self.var_info[var] |= vi
        except KeyError:
            self.var_info[var] = vi


class RQLSTChecker(object):
    """Check a RQL syntax tree for errors not detected on parsing.

    Some simple rewriting of the tree may be done too:
    * if a OR is used on a symmetric relation
    * IN function with a single child

    use assertions for internal error but specific `BadRQLQuery` exception for
    errors due to a bad rql input
    """

    def __init__(self, schema, special_relations=None, backend=None):
        self.schema = schema
        self.special_relations = special_relations or {}
        self.backend = backend

    def check(self, node):
        state = STCheckState()
        self._visit(node, state)
        if state.errors:
            raise BadRQLQuery('%s\n** %s' % (node, '\n** '.join(state.errors)))
        # if node.TYPE == 'select' and \
        #       not node.defined_vars and not node.get_restriction():
        #    result = []
        #    for term in node.selected_terms():
        #        result.append(term.eval(kwargs))

    def _visit(self, node, state):
        try:
            node.accept(self, state)
        except GoTo as ex:
            self._visit(ex.node, state)
        else:
            for c in node.children:
                self._visit(c, state)
            node.leave(self, state)

    def _visit_selectedterm(self, node, state):
        for i, term in enumerate(node.selection):
            # selected terms are not included by the default visit,
            # accept manually each of them
            self._visit(term, state)

    def _check_selected(self, term, termtype, state):
        """check that variables referenced in the given term are selected"""
        for vref in variable_refs(term):
            # no stinfo yet, use references
            for ovref in vref.variable.references():
                rel = ovref.relation()
                if rel is not None:
                    break
            else:
                msg = 'variable %s used in %s is not referenced by any relation'
                state.error(msg % (vref.name, termtype))

    # statement nodes #########################################################

    def visit_union(self, node, state):
        nbselected = len(node.children[0].selection)
        for select in node.children[1:]:
            if not len(select.selection) == nbselected:
                state.error('when using union, all subqueries should have '
                            'the same number of selected terms')

    def leave_union(self, node, state):
        pass

    def visit_select(self, node, state):
        node.vargraph = {}  # graph representing links between variable
        node.aggregated = set()
        self._visit_selectedterm(node, state)

    def leave_select(self, node, state):
        selected = node.selection
        # check selected variable are used in restriction
        if node.where is not None or len(selected) > 1:
            for term in selected:
                self._check_selected(term, 'selection', state)
                for vref in term.iget_nodes(VariableRef):
                    state.add_var_info(vref.variable, VAR_SELECTED)
        for var in node.defined_vars.values():
            vinfo = state.var_info.get(var, 0)
            if (not (vinfo & VAR_HAS_REL) and (vinfo & VAR_HAS_TYPE_REL)
                    and not (vinfo & VAR_SELECTED)):
                raise BadRQLQuery('unbound variable %s (%s)' % (var.name, selected))
        if node.groupby:
            # check that selected variables are used in groups
            for var in node.selection:
                if isinstance(var, VariableRef) and not any(
                    var.is_equivalent(g) for g in node.groupby
                ):
                    state.error('variable %s should be grouped' % var)
            for group in node.groupby:
                self._check_selected(group, 'group', state)
        if node.distinct and node.orderby:
            # check that variables referenced in the given term are reachable from
            # a selected variable with only ?1 cardinality selected
            selectidx = frozenset(vref.name for term in selected
                                  for vref in term.get_nodes(VariableRef))
            for sortterm in node.orderby:
                for vref in sortterm.term.get_nodes(VariableRef):
                    if vref.name in selectidx:
                        continue
                    for vname in selectidx:
                        try:
                            if self.has_unique_value_path(node, vname, vref.name):
                                break
                        except KeyError:
                            continue  # unlinked variable (usually from a subquery)
                    else:
                        msg = ('can\'t sort on variable %s which is linked to a'
                               ' variable in the selection but may have different'
                               ' values for a resulting row')
                        state.error(msg % vref.name)

    def has_unique_value_path(self, select, fromvar, tovar):
        graph = select.vargraph
        path = has_path(graph, fromvar, tovar)
        if path is None:
            return False
        for var in path:
            try:
                rtype = graph[(fromvar, var)]
                cardidx = 0
            except KeyError:
                rtype = graph[(var, fromvar)]
                cardidx = 1
            rschema = self.schema.rschema(rtype)
            for rdef in rschema.rdefs.values():
                # XXX aggregats handling needs much probably some enhancements...
                if not (var in select.aggregated
                        or (rdef.cardinality[cardidx] in '?1' and
                            (var == tovar or not rschema.final))):
                    return False
            fromvar = var
        return True

    def visit_insert(self, insert, state):
        self._visit_selectedterm(insert, state)

    def leave_insert(self, node, state):
        pass

    def visit_delete(self, delete, state):
        self._visit_selectedterm(delete, state)

    def leave_delete(self, node, state):
        pass

    def visit_set(self, update, state):
        self._visit_selectedterm(update, state)

    def leave_set(self, node, state):
        pass

    # tree nodes ##############################################################

    def visit_exists(self, node, state):
        pass

    def leave_exists(self, node, state):
        pass

    def visit_subquery(self, node, state):
        pass

    def leave_subquery(self, node, state):
        # copy graph information we're interested in
        pgraph = node.parent.vargraph
        for select in node.query.children:
            # map subquery variable names to outer query variable names
            trmap = {}
            for i, vref in enumerate(node.aliases):
                try:
                    subvref = select.selection[i]
                except IndexError:
                    state.error('subquery "%s" has only %s selected terms, needs %s'
                                % (select, len(select.selection), len(node.aliases)))
                    continue
                if isinstance(subvref, VariableRef):
                    trmap[subvref.name] = vref.name
                elif (isinstance(subvref, Function) and subvref.descr().aggregat
                      and len(subvref.children) == 1
                      and isinstance(subvref.children[0], VariableRef)):
                    # XXX ok for MIN, MAX, but what about COUNT, AVG...
                    trmap[subvref.children[0].name] = vref.name
                    node.parent.aggregated.add(vref.name)
            for key, val in select.vargraph.items():
                if isinstance(key, tuple):
                    key = (_var_graphid(key[0], trmap, select),
                           _var_graphid(key[1], trmap, select))
                    pgraph[key] = val
                else:
                    values = pgraph.setdefault(_var_graphid(key, trmap, select), [])
                    values += [_var_graphid(v, trmap, select) for v in val]

    def visit_sortterm(self, sortterm, state):
        term = sortterm.term
        if isinstance(term, Constant):
            for select in sortterm.root.children:
                if len(select.selection) < term.value:
                    state.error('order column out of bound %s' % term.value)
        else:
            stmt = term.stmt
            for tvref in variable_refs(term):
                for vref in tvref.variable.references():
                    if vref.relation() or any(vref.is_equivalent(s) for s in stmt.selection):
                        break
                else:
                    msg = 'sort variable %s is not referenced any where else'
                    state.error(msg % tvref.name)

    def leave_sortterm(self, node, state):
        pass

    def visit_and(self, et, state):
        pass  # assert len(et.children) == 2, len(et.children)

    def leave_and(self, node, state):
        pass

    def visit_or(self, ou, state):
        # assert len(ou.children) == 2, len(ou.children)
        # simplify Ored expression of a symmetric relation
        r1, r2 = ou.children[0], ou.children[1]
        try:
            r1type = r1.r_type
            r2type = r2.r_type
        except AttributeError:
            return  # can't be
        if r1type == r2type and self.schema.rschema(r1type).symmetric:
            lhs1, rhs1 = r1.get_variable_parts()
            lhs2, rhs2 = r2.get_variable_parts()
            try:
                if (lhs1.variable is rhs2.variable and
                        rhs1.variable is lhs2.variable):
                    ou.parent.replace(ou, r1)
                    for vref in r2.get_nodes(VariableRef):
                        vref.unregister_reference()
                    raise GoTo(r1)
            except AttributeError:
                pass

    def leave_or(self, node, state):
        pass

    def visit_not(self, not_, state):
        state.under_not.append(True)

    def leave_not(self, not_, state):
        state.under_not.pop()
        # NOT normalization
        child = not_.children[0]
        if self._should_wrap_by_exists(child):
            not_.replace(child, Exists(child))

    def _should_wrap_by_exists(self, child):
        if isinstance(child, Exists):
            return False
        if not isinstance(child, Relation):
            return True
        if child.r_type == 'identity':
            return False
        rschema = self.schema.rschema(child.r_type)
        if rschema.final:
            return False
        # XXX no exists for `inlined` relation (allow IS NULL optimization)
        # unless the lhs variable is only referenced from this neged relation,
        # in which case it's *not* in the statement's scope, hence EXISTS should
        # be added anyway
        if rschema.inlined:
            references = child.children[0].variable.references()
            valuable = 0
            for vref in references:
                rel = vref.relation()
                if rel is None or not rel.is_types_restriction():
                    if valuable:
                        return False
                    valuable = 1
            return True
        return not child.is_types_restriction()

    def visit_relation(self, relation, state):
        if relation.optional and state.under_not:
            state.error("can't use optional relation under NOT (%s)"
                        % relation.as_string())
        lhsvar = relation.children[0].variable
        if relation.is_types_restriction():
            if relation.optional:
                state.error('can\'t use optional relation on "%s"'
                            % relation.as_string())
            if state.var_info.get(lhsvar, 0) & VAR_HAS_TYPE_REL:
                state.error('can only one type restriction per variable (use '
                            'IN for %s if desired)' % lhsvar.name)
            else:
                state.add_var_info(lhsvar, VAR_HAS_TYPE_REL)
            # special case "C is NULL"
            # if relation.children[1].operator == 'IS':
            #     lhs, rhs = relation.children
            #     #assert isinstance(lhs, VariableRef), lhs
            #     #assert isinstance(rhs.children[0], Constant)
            #     #assert rhs.operator == 'IS', rhs.operator
            #     #assert rhs.children[0].type == None
        else:
            state.add_var_info(lhsvar, VAR_HAS_REL)
            rtype = relation.r_type
            try:
                rschema = self.schema.rschema(rtype)
            except KeyError:
                state.error('unknown relation `%s`' % rtype)
            else:
                if rschema.final and relation.optional not in (None, 'right'):
                    state.error("optional may only be set on the rhs on final relation `%s`"
                                % relation.r_type)
                if self.special_relations.get(rtype) == 'uid' and relation.operator() == '=':
                    if state.var_info.get(lhsvar, 0) & VAR_HAS_UID_REL:
                        state.error('can only one uid restriction per variable '
                                    '(use IN for %s if desired)' % lhsvar.name)
                    else:
                        state.add_var_info(lhsvar, VAR_HAS_UID_REL)

            for vref in relation.children[1].get_nodes(VariableRef):
                state.add_var_info(vref.variable, VAR_HAS_REL)
        try:
            vargraph = relation.stmt.vargraph
            rhsvarname = relation.children[1].children[0].variable.name
        except AttributeError:
            pass
        else:
            vargraph.setdefault(lhsvar.name, []).append(rhsvarname)
            vargraph.setdefault(rhsvarname, []).append(lhsvar.name)
            vargraph[(lhsvar.name, rhsvarname)] = relation.r_type

    def leave_relation(self, relation, state):
        pass
        # assert isinstance(lhs, VariableRef), '%s: %s' % (lhs.__class__,
        #                                                       relation)

    def visit_comparison(self, comparison, state):
        pass  # assert len(comparison.children) in (1,2), len(comparison.children)

    def leave_comparison(self, node, state):
        pass

    def visit_mathexpression(self, mathexpr, state):
        pass  # assert len(mathexpr.children) == 2, len(mathexpr.children)

    def leave_mathexpression(self, node, state):
        pass

    def visit_unaryexpression(self, unaryexpr, state):
        pass  # assert len(unaryexpr.children) == 2, len(unaryexpr.children)

    def leave_unaryexpression(self, node, state):
        pass

    def visit_function(self, function, state):
        try:
            funcdescr = function_description(function.name)
        except UnknownFunction:
            state.error('unknown function "%s"' % function.name)
        else:
            try:
                funcdescr.check_nbargs(len(function.children))
            except BadRQLQuery as ex:
                state.error(str(ex))
            if self.backend is not None:
                try:
                    funcdescr.st_check_backend(self.backend, function)
                except BadRQLQuery as ex:
                    state.error(str(ex))
            if funcdescr.aggregat:
                if isinstance(function.children[0], Function) and \
                       function.children[0].descr().aggregat:
                    state.error('can\'t nest aggregat functions')
            if funcdescr.name == 'IN':
                # assert function.parent.operator == '='
                if len(function.children) == 1:
                    function.parent.append(function.children[0])
                    function.parent.remove(function)
                # else:
                #    assert len(function.children) >= 1

    def leave_function(self, node, state):
        pass

    def visit_variableref(self, variableref, state):
        # assert len(variableref.children)==0
        # assert not variableref.parent is variableref
        pass

    def leave_variableref(self, node, state):
        pass

    def visit_constant(self, constant, state):
        if constant.type != 'etype':
            return
        if constant.value not in self.schema:
            state.error('unknown entity type %s' % constant.value)
        if (isinstance(constant.parent, Function) and
                constant.parent.name == 'CAST'):
            return
        rel = constant.relation()
        if rel is not None and rel.r_type in ('is', 'is_instance_of'):
            return
        state.error('Entity types can only be used inside a CAST() '
                    'or with "is" relation')

    def leave_constant(self, node, state):
        pass


class RQLSTAnnotator(object):
    """Annotate RQL syntax tree to ease further code generation from it.

    If an optional variable is shared among multiple scopes, it's rewritten to
    use identity relation.
    """

    def __init__(self, schema, special_relations=None):
        self.schema = schema
        self.special_relations = special_relations or {}

    def annotate(self, node):
        # assert not node.annotated
        node.accept(self)
        node.annotated = True

    def _visit_stmt(self, node):
        for var in node.defined_vars.values():
            var.prepare_annotation()
        for i, term in enumerate(node.selection):
            for func in term.iget_nodes(Function):
                if func.descr().aggregat:
                    node.has_aggregat = True
                    break
            # register the selection column index
            for vref in term.get_nodes(VariableRef):
                vref.variable.stinfo['selected'].add(i)
                vref.variable.set_scope(node)
        if node.where is not None:
            node.where.accept(self, node)

    visit_insert = visit_delete = visit_set = _visit_stmt

    def visit_union(self, node):
        for select in node.children:
            self.visit_select(select)

    def visit_select(self, node):
        for var in node.aliases.values():
            var.prepare_annotation()
        if node.with_ is not None:
            for subquery in node.with_:
                self.visit_union(subquery.query)
                subquery.query.schema = node.root.schema
        node.has_aggregat = False
        self._visit_stmt(node)
        if node.having:
            # if there is a having clause, bloc simplification of variables used in GROUPBY
            for term in node.groupby:
                for vref in term.get_nodes(VariableRef):
                    bloc_simplification(vref.variable, term)
            try:
                vargraph = node.vargraph
            except AttributeError:
                vargraph = None
            # XXX node.having is a list of size 1
            assert len(node.having) == 1
            for term in node.having[0].get_nodes(Comparison):
                lhsvariables = set(
                    vref.variable
                    for vref in term.children[0].get_nodes(VariableRef)
                )
                rhsvariables = set(
                    vref.variable
                    for vref in term.children[1].get_nodes(VariableRef)
                )
                for var in lhsvariables | rhsvariables:
                    var.stinfo.setdefault('having', []).append(term)
                if vargraph is not None:
                    for v1 in lhsvariables:
                        v1 = v1.name
                        for v2 in rhsvariables:
                            v2 = v2.name
                            if v1 != v2:
                                vargraph.setdefault(v1, []).append(v2)
                                vargraph.setdefault(v2, []).append(v1)
                if term.optional in ('left', 'both'):
                    for var in lhsvariables:
                        if var.stinfo['attrvar'] is not None:
                            optcomps = var.stinfo[
                                'attrvar'
                            ].stinfo.setdefault('optcomparisons', set())
                            optcomps.add(term)
                if term.optional in ('right', 'both'):
                    for var in rhsvariables:
                        if var.stinfo['attrvar'] is not None:
                            optcomps = var.stinfo[
                                'attrvar'
                            ].stinfo.setdefault('optcomparisons', set())
                            optcomps.add(term)

    def rewrite_shared_optional(self, exists, var, identity_rel_scope=None):
        """if variable is shared across multiple scopes, need some tree
        rewriting
        """
        # allocate a new variable
        newvar = var.stmt.make_variable()
        newvar.prepare_annotation()
        for vref in var.references():
            if vref.scope is exists:
                rel = vref.relation()
                vref.unregister_reference()
                newvref = VariableRef(newvar)
                vref.parent.replace(vref, newvref)
                stinfo = var.stinfo
                # update stinfo structure which may have already been
                # partially processed
                if rel in stinfo['rhsrelations']:
                    lhs, rhs = rel.get_parts()
                    if (vref is rhs.children[0]
                            and self.schema.rschema(rel.r_type).final):
                        update_attrvars(newvar, rel, lhs)
                        lhsvar = getattr(lhs, 'variable', None)
                        stinfo['attrvars'].remove((lhsvar, rel.r_type))
                        if stinfo['attrvar'] is lhsvar:
                            if stinfo['attrvars']:
                                stinfo['attrvar'] = next(iter(stinfo['attrvars']))
                            else:
                                stinfo['attrvar'] = None
                    stinfo['rhsrelations'].remove(rel)
                    newvar.stinfo['rhsrelations'].add(rel)
                try:
                    stinfo['relations'].remove(rel)
                    newvar.stinfo['relations'].add(rel)
                except KeyError:
                    pass
                try:
                    stinfo['optrelations'].remove(rel)
                    newvar.add_optional_relation(rel)
                except KeyError:
                    pass
                try:
                    stinfo['blocsimplification'].remove(rel)
                    bloc_simplification(newvar, rel)
                except KeyError:
                    pass
                if stinfo['uidrel'] is rel:
                    newvar.stinfo['uidrel'] = rel
                    stinfo['uidrel'] = None
                if stinfo['typerel'] is rel:
                    newvar.stinfo['typerel'] = rel
                    stinfo['typerel'] = None
        # shared references
        newvar.stinfo['constnode'] = var.stinfo['constnode']
        if newvar.stmt.solutions:  # solutions already computed
            newvar.stinfo['possibletypes'] = var.stinfo['possibletypes']
            for sol in newvar.stmt.solutions:
                sol[newvar.name] = sol[var.name]
        if identity_rel_scope is None:
            rel = exists.add_relation(var, 'identity', newvar)
            identity_rel_scope = exists
        else:
            rel = make_relation(var, 'identity', (newvar,), VariableRef)
            exists.parent.replace(exists, And(exists, Exists(rel)))
        # we have to force visit of the introduced relation
        self.visit_relation(rel, identity_rel_scope)
        return newvar

    # tree nodes ##############################################################

    def visit_exists(self, node, scope):
        node.children[0].accept(self, node)

    def visit_not(self, node, scope):
        node.children[0].accept(self, scope)

    def visit_and(self, node, scope):
        node.children[0].accept(self, scope)
        node.children[1].accept(self, scope)
    visit_or = visit_and

    def visit_relation(self, relation, scope):
        # assert relation.parent, repr(relation)
        lhs, rhs = relation.get_parts()
        # may be a constant once rqlst has been simplified
        lhsvar = getattr(lhs, 'variable', None)
        if relation.is_types_restriction():
            if lhsvar is not None:
                lhsvar.stinfo['typerel'] = relation
            return
        if relation.optional is not None:
            exists = relation.scope
            if not isinstance(exists, Exists):
                exists = None
            if lhsvar is not None:
                if exists is not None and lhsvar.scope is lhsvar.stmt:
                    lhsvar = self.rewrite_shared_optional(exists, lhsvar)
                bloc_simplification(lhsvar, relation)
                if relation.optional == 'both':
                    lhsvar.add_optional_relation(relation)
                elif relation.optional == 'left':
                    lhsvar.add_optional_relation(relation)
            try:
                rhsvar = rhs.children[0].variable
                if exists is not None and rhsvar.scope is rhsvar.stmt:
                    rhsvar = self.rewrite_shared_optional(exists, rhsvar)
                bloc_simplification(rhsvar, relation)
                if relation.optional == 'right':
                    rhsvar.add_optional_relation(relation)
                elif relation.optional == 'both':
                    rhsvar.add_optional_relation(relation)
            except AttributeError:
                # may have been rewritten as well
                pass
        rtype = relation.r_type
        rschema = self.schema.rschema(rtype)
        if lhsvar is not None:
            lhsvar.set_scope(scope)
            lhsvar.stinfo['relations'].add(relation)
            if rtype in self.special_relations:
                key = '%srels' % self.special_relations[rtype]
                if key == 'uidrels':
                    constnode = relation.get_variable_parts()[1]
                    if not (relation.operator() != '=' or
                            # XXX use state to detect relation under NOT/OR
                            # + check variable's scope
                            isinstance(relation.parent, Not) or
                            relation.parent.ored()):
                        if isinstance(constnode, Constant):
                            lhsvar.stinfo['constnode'] = constnode
                        if not isinstance(constnode, VariableRef):
                            lhsvar.stinfo['uidrel'] = relation
                else:
                    lhsvar.stinfo.setdefault(key, set()).add(relation)
            elif rschema.final or rschema.inlined:
                bloc_simplification(lhsvar, relation)
        for vref in rhs.get_nodes(VariableRef):
            var = vref.variable
            var.set_scope(scope)
            var.stinfo['relations'].add(relation)
            var.stinfo['rhsrelations'].add(relation)
            if vref is rhs.children[0] and rschema.final:
                update_attrvars(var, relation, lhs)


def update_attrvars(var, relation, lhs):
    if var.stinfo['relations'] - var.stinfo['rhsrelations']:
        raise BadRQLQuery('variable %s should not be used as rhs of attribute relation %s'
                          % (var.name, relation))
    # stinfo['attrvars'] is set of couple (lhs variable name, relation name)
    # where the `var` attribute variable is used
    lhsvar = getattr(lhs, 'variable', None)
    try:
        var.stinfo['attrvars'].add((lhsvar, relation.r_type))
    except KeyError:
        var.stinfo['attrvars'] = set([(lhsvar, relation.r_type)])
    # give priority to variable which is not in an EXISTS as
    # "main" attribute variable
    if var.stinfo['attrvar'] is None or not isinstance(relation.scope, Exists):
        var.stinfo['attrvar'] = lhsvar or lhs
