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
"""Analyze of the RQL syntax tree to get possible types for RQL variables.

"""
from __future__ import print_function

__docformat__ = "restructuredtext en"

import os

from six import StringIO, string_types
from six.moves import zip

from rql import TypeResolverException, nodes


try:
    pure = bool(os.environ.get('RQL_USE_PURE_PYTHON_ANALYSE', 0))
    if pure:
        raise ImportError
    from rql import rql_solve
except ImportError:
    rql_solve = None
    import warnings
    warnings.filterwarnings(action='ignore', module='logilab.constraint.propagation')
    from logilab.constraint import Repository, Solver, fd

    # Gecode solver not available
# rql_solve = None # uncomment to force using logilab-constraint


class ConstraintCSPProblem(object):
    def __init__(self):
        self.constraints = []
        self.domains = {}
        self.scons = []
        self.output = StringIO()

    def debug(self):
        print("Domains:", self.domains)
        print("Constraints:", self.constraints)
        print("Scons:", self.scons)

    def get_output(self):
        return self.output.getvalue()

    def printer(self, *msgs):
        self.output.write(' '.join(str(msg) for msg in msgs))
        self.output.write('\n')

    def solve(self):
        repo = Repository(self.domains.keys(), self.domains, self.get_constraints())
        solver = Solver(printer=self.printer)
        # used for timing
        # import time
        # t0=time.time()
        sols = solver.solve(repo, verbose=(True or self.debug))
        # print("RUNTIME:", time.time()-t0)
        return sols

    def add_var(self, name, values):
        self.domains[name] = fd.FiniteDomain(values)

    def end_domain_definition(self):
        pass

    def get_domains(self):
        return self.domains

    def get_constraints(self):
        return self.constraints

    def add_expr(self, vars, expr):
        self.constraints.append(fd.make_expression(vars, expr))
        self.scons.append(expr)

    def var_has_type(self, var, etype):
        assert isinstance(etype, string_types)
        self.add_expr((var,), '%s == %r' % (var, etype))

    def var_has_types(self, var, etypes):
        etypes = tuple(etypes)
        for t in etypes:
            assert isinstance(t, string_types)
        if len(etypes) == 1:
            cstr = '%s == "%s"' % (var, etypes[0])
        else:
            cstr = '%s in %s ' % (var, etypes)
        self.add_expr((var,), cstr)

    def vars_have_same_types(self, varnames, types):
        self.add_expr(varnames, '%s in %s' % ('=='.join(varnames), types))

    def or_and(self, equalities):
        orred = set()
        variables = set()
        for orred_expr in equalities:
            anded = set()
            for vars, types in orred_expr:
                types = tuple(types)
                for t in types:
                    assert isinstance(t, string_types)
                if len(types) == 1:
                    anded.add('%s == "%s"' % ('=='.join(vars), types[0]))
                else:
                    anded.add('%s in %s' % ('=='.join(vars), types))
                for var in vars:
                    variables.add(var)
            orred.add('(' + ' and '.join(list(anded)) + ')')
        expr = " or ".join(list(orred))
        self.add_expr(tuple(variables), expr)


# GECODE based constraint solver
_AND = 0  # symbolic values
_OR = 1
_EQ = 2
_EQV = 3

OPSYM = {
    _AND: "and",
    _OR: "or",
    _EQ: "eq",
    _EQV: "eqv"
}


class GecodeCSPProblem(object):
    """Builds an internal representation of the constraint
    that will be passed to the rql_solve module which implements
    a gecode-based solver

    The internal representation is a tree builds with lists of lists
    the first item of the list is the node type (_AND,_OR,_EQ,_EQV)

    an example : ["and", [ "eq",0,0 ], ["or", ["eq", 1, 1], ["eq", 1, 2] ] ]

    means Var(0) == Value(0) and ( Var(1)==Val(1) or Var(1) == Val(2)

    TODO: at the moment the solver makes no type checking on the structure
    of the tree thus can crash badly if something wrong is handled to it
    this should not happend as the building of the tree is done internally
    but it should be fixed anyways.
    When fixing that we should also replace string nodes by integers
    """

    def __init__(self):
        self.constraints = []
        self.op = [_AND]
        self.domains = {}       # maps var name -> var value
        self.variables = {}     # maps var name -> var index
        self.ivariables = []    # maps var index-> var name
        self.values = {}        # maps val name -> val index
        self.all_values = set()  # this gets turned into a list later
        self.idx_domains = []   # maps var index -> list of val index
        self.ivalues = {}       # only used for debugging

    def debug(self):
        self.ivalues = {}
        for val_name, val_num in self.values.items():
            self.ivalues[val_num] = val_name
        print("Domains:", self.domains)
        print("Ops:", self.pretty_print_ops(self.op))
        print("Variables:", self.variables)
        print("Values:", self.values)

    def pretty_print_ops(self, ops):
        if ops[0] in (_AND, _OR):
            res = [OPSYM[ops[0]], '(']
            for op in ops[1:]:
                res.append(self.pretty_print_ops(op))
                res.append(',')
            res.append(')')
            return "".join(res)
        elif ops[0] == _EQ:
            return "%s==%s" % (self.ivariables[ops[1]], self.ivalues[ops[2]])
        elif ops[0] == _EQV:
            res = [self.ivariables[k] for k in ops[1:]]
            return '~='.join(res)

    def get_output(self):
        return ""

    def solve(self):
        constraints = self.op

        # used for timing
        # import time
        # t0=time.time()

        sols = rql_solve.solve(self.idx_domains, len(self.all_values), constraints)
        rql_sols = []
        for s in sols:
            r = {}
            for var, val in zip(self.ivariables, s):
                r[var] = self.all_values[val]
            rql_sols.append(r)
        # print("RUNTIME:", time.time()-t0)
        return rql_sols

    def add_var(self, name, values):
        assert name not in self.variables
        self.all_values.update(values)
        self.variables[name] = len(self.variables)
        self.ivariables.append(name)
        self.domains[name] = values

    def end_domain_definition(self):
        # maps integer->value
        self.all_values = list(self.all_values)
        # maps value->integer
        self.values = dict([(v, i) for i, v in enumerate(self.all_values)])
        # print(self.values)
        # print(self.domains)
        for var_name in self.ivariables:
            val_domain = self.domains[var_name]
            idx_domain = [self.values[val] for val in val_domain]
            self.idx_domains.append(idx_domain)

    def and_eq(self, var, value):
        self.op.append([_EQ, self.variables[var], self.values[value]])

    def equal_vars(self, varnames):
        if len(varnames) > 1:
            self.op.append([_EQV] + [self.variables[v] for v in varnames])

    def var_has_type(self, var, etype):
        self.and_eq(var, etype)

    def var_has_types(self, var, etypes):
        for t in etypes:
            assert isinstance(t, string_types)
        if len(etypes) == 1:
            self.and_eq(var, tuple(etypes)[0])
        else:
            orred = [_OR]
            for t in etypes:
                try:
                    orred.append([_EQ, self.variables[var], self.values[t]])
                except KeyError:
                    # key error may be raised by self.values[t] if self.values
                    # reflects constraints from subqueries
                    continue
            self.op.append(orred)

    def vars_have_same_types(self, varnames, types):
        self.equal_vars(varnames)
        for var in varnames:
            self.var_has_types(var, types)

    def or_and(self, equalities):
        orred = [_OR]
        for orred_expr in equalities:
            anded = [_AND]
            for vars, types in orred_expr:
                self.equal_vars(vars)
                for t in types:
                    assert isinstance(t, string_types)
                for var in vars:
                    if len(types) == 1:
                        anded.append([_EQ, self.variables[var], self.values[types[0]]])
                    else:
                        or2 = [_OR]
                        for t in types:
                            or2.append([_EQ, self.variables[var], self.values[t]])
                        anded.append(or2)
            orred.append(anded)
        self.op.append(orred)


if rql_solve is None:
    CSPProblem = ConstraintCSPProblem
else:
    CSPProblem = GecodeCSPProblem

# CSPProblem = ConstraintCSPProblem


class ETypeResolver(object):
    """Resolve variables types according to the schema.

    CSP modelisation:
     * variable    <-> RQL variable
     * domains     <-> different entity's types defined in the schema
     * constraints <-> relations between (RQL) variables
    """
    var_solkey = 'possibletypes'

    def __init__(self, schema, uid_func_mapping=None):
        """
        :Parameters:
         * `schema`: an object describing entities and relations that implements
           the ISchema interface.
         * `uid_func_mapping`: a dictionary where keys are strings representing an
           attribute used as a Unique IDentifier and values are methods that
           accept attribute values and return entity's types.
           [mapping from relation to function taking rhs value as argument
           and returning an entity type].
        """
        self.debug = 0
        self.set_schema(schema)
        if uid_func_mapping is None:
            self.uid_func_mapping = {}
            self.uid_func = None
        else:
            self.uid_func_mapping = uid_func_mapping
            self.uid_func = next(iter(uid_func_mapping.values()))

    def set_schema(self, schema):
        self.schema = schema
        # default domains for a variable
        self._base_domain = set(str(etype) for etype in schema.entities())
        self._nonfinal_domain = set(str(etype) for etype in schema.entities()
                                    if not etype.final)

    def solve(self, node, constraints):
        # debug info
        if self.debug > 1:
            print("- AN1 -"+'-'*80)
            print(node)
            print("CONSTRAINTS:")
            constraints.debug()

        sols = constraints.solve()

        if not sols:
            rql = node.as_string(kwargs=self.kwargs)
            ex_msg = 'Unable to resolve variables types in "%s"' % (rql,)
            if True or self.debug:
                ex_msg += '\n%s' % (constraints.get_output(),)
            raise TypeResolverException(ex_msg)
        node.set_possible_types(sols, self.kwargs, self.var_solkey)

    def _visit(self, node, constraints=None):
        """Recurse down the tree.

            * node: rql node to process
            * constraints: a XxxCSPProblem object.
        """
        func = getattr(self, 'visit_%s' % node.__class__.__name__.lower())
        if constraints is None:
            func(node)
        elif func(node, constraints) is None:
            for c in node.children:
                self._visit(c, constraints)

    def _uid_node_types(self, valnode):
        types = set()
        for cst in valnode.iget_nodes(nodes.Constant):
            assert cst.type
            if cst.type == 'Substitute':
                self.deambiguifiers.add(cst.value)
            cst.uidtype = self.uid_func(cst.eval(self.kwargs))
            types.add(cst.uidtype)
        return types

    def _init_stmt(self, node):
        pb = CSPProblem()
        # set domain for all the variables
        for var in node.defined_vars.values():
            pb.add_var(var.name, self._base_domain)
        # no variable short cut
        return pb

    def _extract_constraint(self, constraints, var, term, get_target_types):
        if self.uid_func:
            alltypes = set()
            for etype in self._uid_node_types(term):
                for targettypes in get_target_types(etype):
                    alltypes.add(targettypes)
        else:
            alltypes = get_target_types()
        domain = constraints.domains[var]
        constraints.var_has_types(var, [str(t) for t in alltypes if t in domain])

    def visit(self, node, uid_func_mapping=None, kwargs=None, debug=False):
        # FIXME: not thread safe
        self.debug = debug
        if uid_func_mapping is not None:
            assert len(uid_func_mapping) <= 1
            self.uid_func_mapping = uid_func_mapping
            self.uid_func = next(iter(uid_func_mapping.values()))
        self.kwargs = kwargs
        self.deambiguifiers = set()
        self._visit(node)
        if uid_func_mapping is not None:
            self.uid_func_mapping = None
            self.uid_func = None
        return self.deambiguifiers

    def visit_union(self, node):
        for select in node.children:
            self._visit(select)

    def visit_insert(self, node):
        if not node.defined_vars:
            node.set_possible_types([{}])
            return
        constraints = self._init_stmt(node)
        constraints.end_domain_definition()
        for etype, variable in node.main_variables:
            if node.TYPE == 'delete' and etype == 'Any':
                continue
            assert etype in self.schema, etype
            var = variable.name
            constraints.var_has_type(var, etype)
        for relation in node.main_relations:
            self._visit(relation, constraints)
        # get constraints from the restriction subtree
        if node.where is not None:
            self._visit(node.where, constraints)
        self.solve(node, constraints)

    visit_delete = visit_insert

    def visit_set(self, node):
        if not node.defined_vars:
            node.set_possible_types([{}])
            return
        constraints = self._init_stmt(node)
        constraints.end_domain_definition()
        for relation in node.main_relations:
            self._visit(relation, constraints)
        # get constraints from the restriction subtree
        if node.where is not None:
            self._visit(node.where, constraints)
        self.solve(node, constraints)

    def visit_select(self, node):
        if not (node.defined_vars or node.aliases):
            node.set_possible_types([{}])
            return
        for subquery in node.with_:  # resolve subqueries first
            self.visit_union(subquery.query)
        constraints = self._init_stmt(node)
        for ca in node.aliases.values():
            etypes = set(stmt.selection[ca.colnum].get_type(sol, self.kwargs)
                         for stmt in ca.query.children for sol in stmt.solutions)
            constraints.add_var(ca.name, etypes)
        constraints.end_domain_definition()
        if self.uid_func:
            # check rewritten uid const
            for consts in node.stinfo['rewritten'].values():
                if not consts:
                    continue
                uidtype = self.uid_func(consts[0].eval(self.kwargs))
                for const in consts:
                    const.uidtype = uidtype
        # get constraints from the restriction subtree
        if node.where is not None:
            self._visit(node.where, constraints)
        elif not node.with_:
            varnames = [v.name for v in node.get_selected_variables()]
            if varnames:
                # add constraint on real relation types if no restriction
                types = [eschema.type for eschema in self.schema.entities()
                         if not eschema.final]
                constraints.vars_have_same_types(varnames, types)
        self.solve(node, constraints)

    def visit_relation(self, relation, constraints):
        """extract constraints for an relation according to it's  type"""
        if relation.is_types_restriction():
            self.visit_type_restriction(relation, constraints)
            return None
        rtype = relation.r_type
        lhs, rhs = relation.get_parts()
        if rtype == 'identity' and relation.neged(strict=True):
            return None
        if rtype in self.uid_func_mapping:
            if isinstance(relation.parent, nodes.Not) or relation.operator() != '=':
                # non final entity types
                etypes = self._nonfinal_domain
            else:
                etypes = self._uid_node_types(rhs)
            if etypes:
                constraints.var_has_types(lhs.name, etypes)
                return None
        if isinstance(rhs, nodes.Comparison):
            rhs = rhs.children[0]
        rschema = self.schema.rschema(rtype)
        if isinstance(lhs, nodes.Constant):  # lhs is a constant node (simplified tree)
            if not isinstance(rhs, nodes.VariableRef):
                return None
            self._extract_constraint(constraints, rhs.name, lhs, rschema.objects)
        elif isinstance(rhs, nodes.Constant) and not rschema.final:
            # rhs.type is None <-> NULL
            if not isinstance(lhs, nodes.VariableRef) or rhs.type is None:
                return None
            self._extract_constraint(constraints, lhs.name, rhs, rschema.subjects)
        elif not isinstance(lhs, nodes.VariableRef):
            # XXX: check relation is valid
            return None
        elif isinstance(rhs, nodes.VariableRef):
            lhsvar = lhs.name
            rhsvar = rhs.name
            lhsdomain = constraints.domains[lhsvar]
            # filter according to domain necessary for column aliases
            rhsdomain = constraints.domains[rhsvar]
            res = []
            var_types = []
            same_var = (rhsvar == lhsvar)

            for frometype, toetypes in rschema.associations():
                fromtype = str(frometype)
                if fromtype in lhsdomain:
                    totypes = set(str(t) for t in toetypes)
                    ptypes = totypes & rhsdomain
                    res.append([([lhsvar], [str(fromtype)]),
                                ([rhsvar], list(ptypes))])
                    if same_var and (fromtype in totypes):  # ptypes ?
                        var_types.append(fromtype)
            constraints.or_and(res)
            if same_var:
                constraints.var_has_types(lhsvar, var_types)
        else:
            # XXX consider rhs.get_type?
            lhsdomain = constraints.domains[lhs.name]
            ptypes = [str(subj) for subj in rschema.subjects()
                      if subj in lhsdomain]
            constraints.var_has_types(lhs.name, ptypes)
        return None

    def visit_type_restriction(self, relation, constraints):
        lhs, rhs = relation.get_parts()
        etypes = set(c.value for c in rhs.iget_nodes(nodes.Constant)
                     if c.type == 'etype')
        if relation.r_type == 'is_instance_of':
            for etype in tuple(etypes):
                for specialization in self.schema.eschema(etype).specialized_by():
                    etypes.add(specialization.type)
        if relation.neged(strict=True):
            etypes = frozenset(t for t in self._nonfinal_domain if t not in etypes)

        constraints.var_has_types(lhs.name, [str(t) for t in etypes])

    def visit_and(self, et, constraints):
        pass

    def visit_or(self, ou, constraints):
        pass

    def visit_not(self, et, constraints):
        pass

    def visit_comparison(self, comparison, constraints):
        pass

    def visit_mathexpression(self, mathexpression, constraints):
        pass

    def visit_function(self, function, constraints):
        pass

    def visit_variableref(self, variableref, constraints):
        pass

    def visit_constant(self, constant, constraints):
        pass

    def visit_keyword(self, keyword, constraints):
        pass

    def visit_exists(self, exists, constraints):
        pass


class ETypeResolverIgnoreTypeRestriction(ETypeResolver):
    """same as ETypeResolver but ignore type restriction relation

    results are stored in as the 'allpossibletypes' key in variable'stinfo
    """
    var_solkey = 'allpossibletypes'

    def visit_type_restriction(self, relation, constraints):
        pass

    def visit_not(self, et, constraints):
        child = et.children[0]
        if isinstance(child, nodes.Relation) and \
           not self.schema.rschema(child.r_type).final:
            return True
