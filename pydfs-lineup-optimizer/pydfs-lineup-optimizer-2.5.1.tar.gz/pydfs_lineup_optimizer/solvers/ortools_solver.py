from ortools.linear_solver import pywraplp
from ortools.linear_solver.pywraplp import _pywraplp
from .base import Solver
from .constants import SolverSign
from .exceptions import SolverException

from copy import deepcopy


class ORToolsSolver(Solver):
    LP_SOLVER = None

    def __init__(self):
        self.prob = None
        self.variables = []
        self.constraints = []
        self.objective = None

    def setup_solver(self):
        self.prob = pywraplp.Solver(
            'FD',
            pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
        )

    def add_variable(self, name):
        variable = self.prob.IntVar(0, 1, name)
        self.variables.append(variable)
        return variable

    def set_objective(self, variables, coefficients):
        self.objective = self.prob.Sum(
            [variable * coefficient for variable, coefficient in zip(variables, coefficients)])
        self.prob.Maximize(self.objective)

    def add_constraint(self, variables, coefficients, sign, rhs):
        if coefficients:
            lhs = [variable * coefficient for variable, coefficient in zip(variables, coefficients)]
        else:
            lhs = variables
        lhs = self.prob.Sum(lhs)
        if sign == SolverSign.EQ:
            constraint = lhs == rhs
        elif sign == SolverSign.NOT_EQ:
            constraint = lhs != rhs
        elif sign == SolverSign.GTE:
            constraint = lhs >= rhs
        elif sign == SolverSign.LTE:
            constraint = lhs <= rhs
        else:
            raise SolverException('Incorrect constraint sign')
        self.constraints.append(constraint)
        self.prob.Add(constraint, name='constraint_%d' % len(self.constraints))

    def copy(self):
        return self
        new_solver = type(self)()
        self.prob.Clear()
        new_solver.setup_solver()
        new_solver.variables = self.variables
        new_solver.objective = self.objective
        new_solver.constraints = self.constraints
        new_solver.prob.Maximize(new_solver.objective)
        for constraint in self.constraints:
            new_solver.prob.Add(constraint)
        return new_solver

    def solve(self):
        status = self.prob.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            result = []
            for variable in self.variables:
                if variable.solution_value() == 1.0:
                    result.append(variable)
            return result
        else:
            raise SolverException('Unable to solve')
