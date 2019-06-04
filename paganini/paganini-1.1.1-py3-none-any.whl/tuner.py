import cvxpy
import sympy
import numpy as np

from scipy import sparse

from math import gcd
from enum import Enum

from collections import Counter

def is_number(n):
    return isinstance(n, (int,float))

def is_positive(n):
    return is_number(n) and n > 0

class Exp:
    """ Class of algebraic expressions (monomials) used to define in an
    algebraic specifications. An expression is represented using a
    multiplicative coefficient (constant) and a map of variable indices with
    their respective non-negative exponents."""

    def __init__(self, mul_coeff = 1, variables = {}):
        self._mul_coeff = mul_coeff
        self.variables = variables

    def __pow__(self, n):
        """ Expression exponentiation."""
        assert is_positive(n), 'Positive exponent required.'

        xs = dict(self.variables)
        for v in self.variables:
            xs[v] *= n # (a^b)^c = a^(b * c)

        return Exp(self._mul_coeff ** n, xs)

    def __mul__(self, other):
        """ Multiplication of algebraic expressions."""
        if not isinstance(other, Exp):
            other = Exp(other)

        x, y = Counter(self.variables), Counter(other.variables)
        return Exp(self._mul_coeff * other._mul_coeff, dict(x + y))

    __rmul__ = __mul__ # make multiplication commute again

    def __add__(self, other):
        """ Expression addition."""
        return Polynomial(self) + other

    __radd__ = __add__ # make addition commute again

    def __sub__(self, other):
        """ Expression subtraction."""
        return Polynomial(self) - other

    def spec(self):
        """ Returns a list of pairs describing the expression. The first
        component denotes a variable whereas the second one denotes its
        respective exponent. The represented expression can be recovered by
        multiplying all of the variables (with their exponents) and the
        multiplicative coefficient."""
        return self.variables.items()

    def is_constant(self):
        """ Checks if the monomial represents a constant."""
        return len(self.variables) == 0

class VariableType(Enum):
    PLAIN = 1 # regular, plain variables, e.g. Z.
    TYPE  = 2 # variables corresponding to some types, e.g. having definitions.

class Variable(Exp):
    """ Class of variables. Note that each variable is also an expression."""

    def __init__(self, tuning_value = None):
        super(Variable,self).__init__(1,{})

        self.variables[self] = 1
        self.value = None # tuning value
        self.idx   = None

        self.type  = VariableType.PLAIN
        self.tuning_value = tuning_value

    def _type_variable(self):
        """ Checks if the variable defines a type."""
        return self.type == VariableType.TYPE

class Operator(Enum):
    """ Enumeration of supported constraint signs."""
    LEQ       = 1 # less or equal
    GEQ       = 2 # greater or equal
    UNBOUNDED = 3 # unbounded operator

class Constraint:
    """ Supported constraints for classes such as SEQ."""
    def __init__(self, operator, value):
        self.operator = operator
        self.value    = value

    @staticmethod
    def normalise(constraint = None):

        if constraint is None:
            return Constraint(Operator.UNBOUNDED, 0)
        else:
            return constraint

def leq(n):
    """ Creates a less or equal constraint for the given input."""
    assert n >= 0, "Negative constraints are not supported."
    return Constraint(Operator.LEQ, n)

def geq(n):
    """ Creates a greater or equal constraint for the given input."""
    assert n >= 0, "Negative constraints are not supported."
    return Constraint(Operator.GEQ, n)

class Seq(Variable):
    """ Class of sequence variables."""

    def __init__(self, expressions, constraint = None):
        super(Seq,self).__init__()

        if not isinstance(expressions, Polynomial):
            expressions = Polynomial(expressions)

        self.definition = expressions
        self.constraint = Constraint.normalise(constraint)
        self.type = VariableType.TYPE # make sure its a type variable

    def register(self, spec):
        spec._seq_variables.append(self)

    def unfold(self, spec):

        if self.constraint.operator == Operator.UNBOUNDED:
            # note: Seq(expr) = 1 + expr * Seq(expr).
            spec.add(self, 1 + self.definition * self)

        elif self.constraint.operator == Operator.LEQ:
            # note: Seq(expr)_{<= k} = 1 + expr + expr^2 + ... + expr^k.
            xs = list(range(1, self.constraint.value + 1))
            spec.add(self, 1 + Polynomial([self.definition ** k for k in xs]))

        else: # constraint.operator == Operator.GEQ
            # note: Seq(expr)_{>= k} = expr^k + expr^{k+1} + ...
            #                        = expr^k (1 + expr^2 + expr^3 + ...)
            #                        = expr^k Seq(expr).

            seq = Seq(self.definition)
            seq.unfold(spec)

            spec.add(self, self.definition ** constraint.value * seq)

class MSet(Variable):
    """ Class of multiset variables."""

    def __init__(self, expressions):
        super(MSet,self).__init__()
        self.definition = expressions
        self.type = VariableType.TYPE # make sure its a type variable

    def register(self, spec):
        spec._mset_variables.append(self)

    def unfold(self, spec):
        pass

class Cyc(Variable):
    """ Class of cycle variables."""

    def __init__(self, expressions):
        super(Cyc,self).__init__()
        self.definition = expressions
        self.type = VariableType.TYPE # make sure its a type variable

    def register(self, spec):
        spec._cyc_variables.append(self)

    def _unfold(self, spec):
        pass

def to_polynomial(xs):

    if is_number(xs): # explicit cast
        xs = Polynomial([Exp(xs)])

    elif isinstance(xs, Exp): # explicit cast
        xs = Polynomial([xs])

    return xs

def to_monomials(xs):
    return [xs] if isinstance(xs, Exp) else xs

class Polynomial:
    """ Class of polonomials of algebraic expressions."""

    def __init__(self, monomials):
        self._monomials = to_monomials(monomials)

    def __mul__(self, other):
        """ Polynomial multiplication."""
        other = to_polynomial(other)

        outcome = [] # naive but works
        for a in self._monomials:
            for b in other._monomials:
                outcome.append(a * b)

        return Polynomial(outcome)

    __rmul__ = __mul__ # make multiplication commute again

    def __pow__(self, n):
        """ Naive exponentiation of polynomials."""
        assert is_positive(n), 'Positive exponent required'

        if n == 1:
            return Polynomial(self._monomials)

        if n % 2 == 1:
            return self * self ** (n - 1)
        else:
            other = self ** (n >> 1)
            return other * other

    def __add__(self, other):
        """ Polynomial addition."""
        other = to_polynomial(other)

        # FIXME: Consider a representation without monomial duplicates.
        return Polynomial(self._monomials + other._monomials)

    __radd__ = __add__ # make addition commute again

    def __sub__(self, other):
        """ Polynomial subtraction."""
        if is_number(other):
            return self + (-other)

        other = to_monomials(other)
        other = Polynomial(other)

        xs = [-1 * e for e in other._monomials]
        return self + Polynomial(xs)

    def __iter__(self):
        return iter(self._monomials)

class Type(Enum):
    """ Enumeration of supported system types."""
    ALGEBRAIC = 1
    RATIONAL  = 2

class Params:
    """ CVXPY solver parameters initalised with some defaults."""

    def __init__(self, sys_type):
        self.verbose   = True
        if sys_type == Type.RATIONAL:
            self.sys_type  = Type.RATIONAL
            self.solver    = cvxpy.SCS
            self.max_iters = 2500
            self.eps       = 1.e-20
            self.norm      = 40
        else:
            self.sys_type  = Type.ALGEBRAIC
            self.solver    = cvxpy.ECOS
            self.max_iters = 100
            self.feastol   = 1.e-20

def phi(n):
    """ Euler's totient function."""
    assert n >= 0, 'Negative integer.'

    out = 0
    for i in range(1, n + 1):
        if gcd(n, i) == 1:
            out += 1

    return out

class Specification:
    """ Class representing algebraic combinatorial systems."""

    def __init__(self, truncate = 10):

        self._counter            = 0
        self._equations          = {}

        self._seq_variables      = []

        self._mset_variables     = []
        self._msets              = {} # (truncated) MSet equations.

        self._cyc_variables      = []
        self._cycs               = {} # (truncated) Cyc equations.

        self._powers             = {} # accounts for expressions like T(Z^i).

        self._all_variables      = {} # index to variable map.
        self._tuning_variables   = set()

        self.truncate            = truncate # series truncation threshold.

    def variable(self, x = None):
        v = Variable(x)
        self._register_variable(v)
        return v

    def type_variable(self, x = None):
        var = self.variable(x)
        var.type = VariableType.TYPE
        return var

    def _register_variable(self, v):
        """ Registers the given variable in the specification."""
        assert isinstance(v, Variable), 'Variable required.'

        if hasattr(v, 'definition'): # note: convention.
            self._register_expressions(v.definition)

        idx = self._counter
        if not idx in self._all_variables:
            self._counter += 1

            v.idx = idx
            self._all_variables[idx] = v
            if v.tuning_value is not None:
                self._tuning_variables.add(v)

            if hasattr(v, 'register'): # note: convention.
                v.register(self)

    def _register_expressions(self, expressions):
        """ Registers variables in the given expressions."""
        expressions = to_monomials(expressions)

        for expr in expressions:
            for v in expr.variables:
                self._register_variable(v)

    def _register_variables(self):
        for v in self._equations:
            self._register_variable(v)
            self._register_expressions(self._equations[v])

    def _unfold_variables(self):
        for v in self._seq_variables:
            v.unfold(self)

    def add(self, variable, expressions):
        """ Includes the given equation in the system. Note that each equation
        consists of a left-hand side variable and a corresponding right-hand
        side expression list (i.e. polynomial) or a single expression defining
        the right-hand side sum. Each expression should be either an instance of
        'Exp' or be an integer."""

        if not isinstance(expressions, Polynomial):
            expressions = Polynomial(expressions)

        self._equations[variable] = expressions
        variable.type = VariableType.TYPE # make sure its a type variable

    def _power_variable(self, var, d = 1):
        """ Given a variable, say, t = T(Z_1,...,Z_k) outputs a new variable
        representing the dth power of t, i.e. t_d = T(Z_1^d,...,Z_k^d) also
        known as diagonals. The variable t_d is cached within the specification
        and its defining equation saved."""

        assert d > 0, "Invalid degree parameter d."
        assert var._type_variable(), "Non-type variable."

        if var not in self._powers:
            self._powers[var] = {}

        # check the variable cache.
        if d in self._powers[var]:
            return self._powers[var][d]

        if d == 1 and var in self._equations: # special case
            self._powers[var][d] = var
            return var

        var_d = self.type_variable() if d > 1 else var
        self._powers[var][d] = var_d # memorise var[d]

        if var in self._equations:
            # create respective rhs monomials.
            monomials = self._equations[var]
            exprs = [self._power_expr(e,d) for e in monomials]
            self.add(var_d, Polynomial(exprs))
            return var_d

        elif var in self._mset_variables:
            # iterate and create respective rhs monomials.
            exprs = var.definition
            self._msets[var_d] = []
            for k in range(d, self.truncate + 1, d):
                self._msets[var_d].append([self._power_expr(e,k)\
                        for e in exprs]) # increase d

            return var_d

        elif var in self._cyc_variables:
            # iterate and create respective rhs monomials.
            exprs = var.definition
            self._cycs[var_d] = []
            for k in range(d, self.truncate + 1, d):

                # create a sequence version of the expressions
                seq_k = Seq([self._power_expr(e,k) for e in exprs])
                self._register_variable(seq_k)
                seq.unfold(spec)

                self._cycs[var_d].append(seq_k) # increase d

            return var_d

    def _power_expr(self, expr, d = 1):
        """ Extends self._power_variable to expressions."""

        variables = {}
        for v in expr.variables:
            if v._type_variable():
                # substitute the power variable.
                x = self._power_variable(v, d)
                variables[x.idx] = expr.variables[v.idx]
            else:
                # increase the exponent.
                variables[v.idx] = d * expr.variables[v.idx]

        return Exp(expr._mul_coeff, variables)

    def total_variables(self):
        """ Returns the total number of discharged variables."""
        return self._counter

    def _expr_specs(self, expressions):
        """ Given a list (i.e. series) of monomial expressions, creates a
        corresponding sparse matrix thereof."""

        expressions = to_monomials(expressions)

        rows = 0 # row counter
        row, col, data =  [], [], []
        for exp in expressions:
            if isinstance(exp, Exp):
                for (v, e) in exp.spec():
                    row.append(rows)
                    col.append(v.idx)
                    data.append(e)
                rows += 1
            else:
                rows += exp

        # create a sparse representation of the series.
        return sparse.csr_matrix((np.array(data),
            (np.array(row),np.array(col))), shape=(rows,
            self.total_variables()))

    def _specs(self):
        """ Computes sparse matrix specifications corresponding to each of the
        system equation, along with monomial multiplicative coefficient
        logarithms, entering later to the optimisation problem constraints."""

        matrices = []
        coeffs   = []

        for expressions in self._equations.values():
            matrix = self._expr_specs(expressions)
            matrices.append(matrix)

            matrix_coeff = []
            for e in expressions:
                if e._mul_coeff >= 0:
                    matrix_coeff.append(sympy.log(e._mul_coeff))
                else: # hide negative coefficients
                    matrix_coeff.append(0)

            coeffs.append(matrix_coeff)

        return (matrices, np.array(coeffs))

    def check_type(self):
        """ Checks if the system is algebraic or rational."""

        if len(self._mset_variables) > 0 or len(self._cyc_variables) > 0:
            return Type.ALGEBRAIC

        for expressions in self._equations.values():
            for exp in expressions:
                if isinstance(exp, Exp):
                    for v, e in exp.variables.items():
                        if v._type_variable() and e > 1:
                            return Type.ALGEBRAIC

        return Type.RATIONAL

    def _init_params(self, params = None):
        if params is None:
            # some defaults
            sys_type = self.check_type()
            return Params(sys_type)
        else:
            return params

    def _construct_truncated_series(self):
        """ Assuming that the system is already defined, constructs a truncated
        series representation for each of the MSet or Cyc variables in the
        specification."""

        for mset in self._mset_variables:
            self._power_variable(mset,1)

        for cyc in self._cyc_variables:
            self._power_variable(cyc,1)

    def _compose_constraints(self, var):
        assert len(self._equations) > 0, "System without equations."
        matrices, coeffs = self._specs()
        constraints = []

        # compose type variable constraints.
        for idx, eq_variable in enumerate(self._equations):
            log_exp = matrices[idx]
            coeff   = coeffs[idx] # c = e^{log c}
            tidx    = eq_variable.idx

            _const = 0 # allow negative, constant expressions.
            for monomial in self._equations[eq_variable]:
                if monomial._mul_coeff < 0:
                    if monomial.is_constant():
                        _const += monomial._mul_coeff
                    else:
                        raise ValueError('Negative monomial coefficient')

            exponents = log_exp * var + coeff
            constraints.append(var[tidx] >=
                    cvxpy.log_sum_exp(exponents) + _const)

        # compose MSet variable constraints.
        for v in self._msets:
            expressions = self._msets[v]
            xs = [1/(i+1) * cvxpy.exp(cvxpy.sum(self._expr_specs(e) * var))
                    for i, e in enumerate(expressions)]

            constraints.append(var[v.idx] >= cvxpy.sum(xs))

        # compose Cyc variable constraints.
        for v in self._cycs:
            expressions = self._cycs[v]
            xs = [phi(i+1)/(i+1) * self._expr_specs(e) * var
                    for i, e in enumerate(expressions)]

            constraints.append(var[v.idx] >= cvxpy.sum(xs))

        return constraints

    def _run_solver(self, var, problem, params):

        if params.sys_type == Type.RATIONAL:
            solution = problem.solve(solver = params.solver, verbose =
                    params.verbose, eps = params.eps, max_iters =
                    params.max_iters)
        else:
            solution = problem.solve(solver = params.solver, verbose =
                    params.verbose, feastol = params.feastol, max_iters =
                    params.max_iters)

        # decorate system variables
        for idx, expr in enumerate(var.value):
            self._all_variables[idx].value = sympy.exp(expr).evalf()

        return solution

    def run_tuner(self, t, params = None):
        """ Given the type variable and a set of tuning parameters, composes a
        (tuning) optimisation problem corresponding to an approximate sampler
        meant for structures of the given type. Variables are tuned so to
        achieve (in expectation) the marked variable values.  Consider the
        following example:

        sp = Specification()
        z, u, M = sp.variable(1000), sp.variable(200), sp.variable()
        sp.add(M, z + u * z * M + z * M **2)

        params = Params(Type.ALGEBRAIC)
        sp.run_tuner(M, params)

        Here, the variables z and u are marked with *absolute* values 1000 and
        200, respectively. The input type represents the type of Motzkin trees,
        i.e. unary-binary plane trees. Variable z marks their size, whereas u
        marks the occurrences of unary nodes. The tuning goal is to obtain
        specific values of z, u, and M, such that the induced branching
        probabilities lead to a sampler which generates Motzkin trees of size
        1000 with around 200 unary nodes (both in expectation).

        Respective variables (including type variables) are decorated with a
        proper 'value'. The method returns the CVXPY solution (i.e. the optimal
        value for the problem, or a string indicating why the problem could not
        be solved)."""

        params = self._init_params(params)
        self._register_variables()
        self._unfold_variables()

        assert self.total_variables() > 0, "System without variables."
        assert len(self._equations) > 0, "System without equations."
        assert len(self._tuning_variables) > 0,\
            "The given system has no tuned variables."

        self._construct_truncated_series() # note: might generate variables.
        n = self.total_variables()
        var = cvxpy.Variable(n)

        # compose the constraints
        constraints = self._compose_constraints(var)

        # compose the objective
        obj = np.zeros(n)
        obj[t.idx] = 1.0
        for v in self._tuning_variables:
            obj[v.idx] = -v.value

        objective = cvxpy.Minimize(obj * var)
        problem   = cvxpy.Problem(objective, constraints)
        return self._run_solver(var, problem, params)

    def run_singular_tuner(self, z, params = None):
        """ Given a (size) variable and a set of tuning parameters, composes an
        optimisation problem corresponding to an approximate sampler meant for
        structures of the given type. Variables are tuned so to achieve (in
        expectation) the marked variable frequencies.

        Consider the following example:

        sp = Specification()
        z, u, M = sp.variable(), sp.variable(0.4), sp.variable()
        sp.add(M, z + u * z * M + z * M **2)

        params = Params(Type.ALGEBRAIC)
        sp.run_singular_tuner(z, params)

        Here, the variable u is marked with a *frequency* 0.4.  The type M
        represents the type of Motzkin trees, i.e. unary-binary plane trees.
        Variable z marks their size, whereas u marks the occurrences of unary
        nodes. The tuning goal is to obtain specific values of z, u, and M, such
        that the induced branching probabilities lead to a sampler which
        generates, in expectation, Motzkin trees of infinite (i.e. unbounded)
        size and around 40% of unary nodes.

        Respective variables (including type variables) are decorated with a
        proper 'value'. The method returns the CVXPY solution (i.e. the optimal
        value for the problem, or a string indicating why the problem could not
        be solved)."""

        params = self._init_params(params)
        self._register_variables()
        self._unfold_variables()

        assert self.total_variables() > 0, "System without variables."
        assert len(self._equations) > 0, "System without equations."

        self._construct_truncated_series() # note: might generate variables.
        n = self.total_variables()
        var = cvxpy.Variable(n)

        # compose the constraints
        constraints = self._compose_constraints(var)

        if params.sys_type == Type.RATIONAL:
            # for rational systems the optimisation problem becomes unbounded,
            # hence we need to artificially bound the vector norm.
            constraints.append(cvxpy.norm(var,2) <= params.norm)

        # compose the objective
        obj = np.zeros(n)
        obj[z.idx] = 1.0

        for v in self._tuning_variables:
            obj[v.idx] = value

        objective = cvxpy.Maximize(obj * var)
        problem   = cvxpy.Problem(objective, constraints)
        return self._run_solver(var, problem, params)
