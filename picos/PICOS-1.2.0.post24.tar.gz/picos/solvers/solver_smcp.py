#-------------------------------------------------------------------------------
# Copyright (C) 2017 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file is a skeleton implementation for the SMCP solver.
# Currently, the funcional implementation is found in CVXOPTSolver.
#-------------------------------------------------------------------------------

from ..expressions import *
from ..constraints import *

from .solver_cvxopt import CVXOPTSolver
from .solver import *

class SMCPSolver(CVXOPTSolver):
    @classmethod
    def test_availability(cls):
        import smcp

    @classmethod
    def supports_integer(cls):
        return False

    @classmethod
    def supported_objectives(cls):
        yield AffinExp

    @classmethod
    def supported_constraints(cls):
        yield AffineConstraint
        yield SOCConstraint
        yield RSOCConstraint
        yield LMIConstraint

    @classmethod
    def support_level(cls, problem):
        level = super(SMCPSolver, cls).support_level(problem)

        hasLMI = False
        hasNonAffineNonLMI = False
        for constraint in problem.constraints:
            if isinstance(constraint, LMIConstraint):
                hasLMI = True
            elif not isinstance(constraint, AffineConstraint):
                hasNonAffineNonLMI = True

        # SMCP is made to solve sparse SDPs.
        if not hasLMI or hasNonAffineNonLMI:
            level = min(level, SUPPORT_LEVEL_EXPERIMENTAL)

        return level

    def __init__(self, problem):
        super(SMCPSolver, self).__init__(problem)

        self.name = "SMCP"
        self.longname = "Sparse Matrix Cone Program Solver"
