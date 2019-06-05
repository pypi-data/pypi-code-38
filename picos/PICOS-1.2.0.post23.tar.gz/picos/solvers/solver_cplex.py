# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2018 Maximilian Stahlberg
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
# This file implements the CPLEX solver through its official Python interface.
#-------------------------------------------------------------------------------

import math
import time
import cvxopt
from collections import namedtuple

from ..expressions import *
from ..constraints import *
from ..tools import NonConvexError

from .solver import *

class CPLEXSolver(Solver):
    """
    Implementation of the CPLEX solver.

    .. note ::
        Names are used instead of indices for identifying both variables and
        constraints since indices can change if the CPLEX instance is modified.
    """
    @classmethod
    def test_availability(cls):
        import cplex

    @classmethod
    def supports_integer(cls):
        return True

    @classmethod
    def supported_objectives(cls):
        yield AffinExp
        yield QuadExp

    @classmethod
    def supported_constraints(cls):
        yield AffineConstraint
        yield SOCConstraint
        yield RSOCConstraint
        yield QuadConstraint

    CplexSOCC = namedtuple("SOCC",
        ("LHSVars", "RHSVar", "LHSCons", "RHSCon", "quadCon"))

    CplexRSOCC = namedtuple("RSOCC",
        ("LHSVars", "RHSVars", "LHSCons", "RHSCons", "quadCon"))

    def __init__(self, problem):
        super(CPLEXSolver, self).__init__(
            problem, "CPLEX", "IBM ILOG CPLEX Optimization Studio")

        self._cplexVarName = dict()
        """Maps PICOS variable indices to CPLEX variable names."""

        self._cplexLinConNames = dict()
        """Maps a PICOS (multidimensional) linear constraint to a collection of
        CPLEX (scalar) linear constraint names."""

        self._cplexQuadConName = dict()
        """Maps a PICOS quadratic or conic quadratic constraint to a CPLEX
        quadratic constraint name."""

        self._cplexSOCC = dict()
        """Maps a PICOS second order cone constraint to its CPLEX representation
        involving auxiliary variables and constraints."""

        self._cplexRSOCC = dict()
        """Maps a PICOS rotated second order cone constraint to its CPLEX
        representation involving auxiliary variables and constraints."""

        self.nextConstraintID = 0
        """Used to create unique names for constraints."""

    def __del__(self):
        if self.int is not None:
            self.int.end()

    def reset_problem(self):
        if self.int is not None:
            self.int.end()
        self.int = None
        self._cplexVarName.clear()
        self._cplexLinConNames.clear()
        self._cplexQuadConName.clear()
        self._cplexSOCC.clear()
        self._cplexRSOCC.clear()

    def _get_unique_constraint_id(self):
        ID = self.nextConstraintID
        self.nextConstraintID += 1
        return ID

    def _make_cplex_var_names(self, picosVar, localIndex = None):
        """
        Converts a PICOS variable to a list of CPLEX variable names, each
        corresponding to one scalar variable contained in the PICOS variable.
        If localIndex is given, then only the name of the CPLEX variable
        representing the scalar variable with that offset is returned.
        The name format is "picosName[localIndex]".
        """
        # TODO: This function appears in multiple solvers, move it to the Solver
        #       base class as "_make_scalar_var_names".
        if localIndex is not None:
            return "{}[{}]".format(picosVar.name, localIndex)
        else:
            return [
                self._make_cplex_var_names(picosVar, localIndex)
                for localIndex in range(picosVar.dim)]

    def _import_variable(self, picosVar):
        import cplex

        varDim  = picosVar.dim
        varType = picosVar.vtype

        # Create names.
        names = self._make_cplex_var_names(picosVar)

        # Retrieve types.
        if varType in ("continuous", "symmetric"):
            types = varDim * self.int.variables.type.continuous
        elif varType == "integer":
            types = varDim * self.int.variables.type.integer
        elif varType == "binary":
            types = varDim * self.int.variables.type.binary
        elif varType == "semiint":
            types = varDim * self.int.variables.type.semi_integer
        elif varType == "semicont":
            types = varDim * self.int.variables.type.semi_continuous
        else:
            raise NotImplementedError(
                "Variables of type '{}' are not supported with CPLEX."
                .format(varType))

        # Retrieve bounds.
        lowerBounds = []
        upperBounds = []
        for localIndex in range(varDim):
            bounds = picosVar.bnd.get(localIndex)
            if bounds:
                lower, upper = bounds
                if lower is None:
                    lowerBounds.append(-cplex.infinity)
                else:
                    lowerBounds.append(lower)
                if upper is None:
                    upperBounds.append(cplex.infinity)
                else:
                    upperBounds.append(upper)
            else:
                lowerBounds.append(-cplex.infinity)
                upperBounds.append(cplex.infinity)

        # Import variable.
        # Note that CPLEX allows importing the objective function coefficients
        # for the new variables here, but that is done later to streamline
        # updates to the objective.
        self.int.variables.add(
            lb=lowerBounds, ub=upperBounds, types=types, names=names)

        # Map PICOS indices to CPLEX names.
        for localIndex in range(varDim):
            picosIndex = picosVar.startIndex + localIndex
            self._cplexVarName[picosIndex] = names[localIndex]

        if self._debug():
            cplexVar = {"names": names, "types": types,
                "lowerBounds": lowerBounds, "upperBounds": upperBounds}
            self._debug(
                "Variable imported: {} → {}".format(picosVar, cplexVar))

    def _remove_variable(self, picosVar):
        cplexVarNames = []
        for localIndex in range(picosVar.dim):
            picosIndex = picosVar.startIndex + localIndex
            cplexVarNames.append(self._cplexVarName.pop(picosIndex))
        self.int.variables.delete(cplexVarNames)

    def _affinexp_pic2cpl(self, picosExpression):
        import cplex
        for names, coefficients, constant in picosExpression.sparse_rows(
                None, indexFunction = self._make_cplex_var_names):
            yield cplex.SparsePair(ind = names, val = coefficients), constant

    def _scalar_affinexp_pic2cpl(self, picosExpression):
        assert len(picosExpression) is 1
        return next(self._affinexp_pic2cpl(picosExpression))

    def _quadexp_pic2cpl(self, picosExpression):
        """
        Tranforms the quadratic part of a PICOS quadratic expression to a CPLEX
        quadratic expression.

        :returns: :class:`SparseTriple <cplex.SparseTriple>` mapping a pair of
            CPLEX variable names to scalar constants.
        """
        import cplex

        if not isinstance(picosExpression, QuadExp):
            raise ValueError("Expression must be a quadratic expression.")

        cplexI, cplexJ, cplexV = [], [], []
        for (picosVar1, picosVar2), picosCoefficients \
            in picosExpression.quad.items():
            for sparseIndex in range(len(picosCoefficients)):
                localVar1Index = picosCoefficients.I[sparseIndex]
                localVar2Index = picosCoefficients.J[sparseIndex]
                localCoefficient = picosCoefficients.V[sparseIndex]
                cplexI.append(self._cplexVarName[
                    picosVar1.startIndex + localVar1Index])
                cplexJ.append(self._cplexVarName[
                    picosVar2.startIndex + localVar2Index])
                cplexV.append(localCoefficient)

        return cplex.SparseTriple(ind1 = cplexI, ind2 = cplexJ, val = cplexV)

    def _import_linear_constraint(self, picosConstraint):
        import cplex
        assert isinstance(picosConstraint, AffineConstraint)

        length = len(picosConstraint)

        # Retrieve left hand side and right hand side expressions.
        cplexLHS, cplexRHS = [], []
        for names, coefficients, constant in picosConstraint.sparse_Ab_rows(
                None, indexFunction = self._make_cplex_var_names):
            cplexLHS.append(cplex.SparsePair(ind = names, val = coefficients))
            cplexRHS.append(constant)

        # Retrieve senses.
        if picosConstraint.is_increasing():
            senses = length * "L"
        elif picosConstraint.is_decreasing():
            senses = length * "G"
        elif picosConstraint.is_equality():
            senses = length * "E"
        else:
            assert False, "Unexpected constraint relation."

        # Give unique names that are used to identify the constraint. This is
        # necessary as constraint indices can change if the problem is modified.
        conID = self._get_unique_constraint_id()
        names = ["{}:{}".format(conID, localConstraintIndex)
            for localConstraintIndex in range(length)]

        if self._debug():
            cplexConstraint = {"lin_expr": cplexLHS, "senses": senses,
                "rhs": cplexRHS, "names": names}
            self._debug(
                "Linear constraint imported: {} → {}".format(
                    picosConstraint, cplexConstraint))

        # Import the constraint.
        self.int.linear_constraints.add(
            lin_expr=cplexLHS, senses=senses, rhs=cplexRHS, names=names)

        return names

    def _import_quad_constraint(self, picosConstraint):
        assert isinstance(picosConstraint, QuadConstraint)

        # Retrieve
        # - CPLEX' linear term, which is the linear term of the affine
        #   expression in the PICOS constraint, and
        # - CPLEX' right hand side, which is the negated constant term of the
        #   affine expression in the PICOS constraint.
        cplexLinear, cplexRHS = \
            self._scalar_affinexp_pic2cpl(picosConstraint.le0.aff)
        cplexRHS = -cplexRHS

        # Retrieve CPLEX' quadratic term.
        cplexQuad = self._quadexp_pic2cpl(picosConstraint.le0)

        # Give a unique name that is used to identify the constraint. This is
        # necessary as constraint indices can change if the problem is modified.
        name = "{}:{}".format(self._get_unique_constraint_id(), 0)

        if self._debug():
            cplexConstraint = {"lin_expr": cplexLinear, "quad_expr": cplexQuad,
                "rhs": cplexRHS, "name": name}
            self._debug(
                "Quadratic constraint imported: {} → {}".format(
                    picosConstraint, cplexConstraint))

        # Import the constraint.
        self.int.quadratic_constraints.add(lin_expr=cplexLinear,
            quad_expr=cplexQuad, sense="L", rhs=cplexRHS, name=name)

        return name

    def _import_socone_constraint(self, picosConstraint):
        import cplex
        assert isinstance(picosConstraint, SOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS = picosConstraint.ub
        picosLHSLen = len(picosLHS)

        # Make identifying names for the auxiliary variables and constraints.
        conID = self._get_unique_constraint_id()
        cplexLHSVars = ["{}:V{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSVar  =  "{}:V{}".format(conID, picosLHSLen)
        cplexLHSCons = ["{}:C{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSCon  =  "{}:C{}".format(conID, picosLHSLen)
        cplexQuadCon =  "{}:C{}".format(conID, picosLHSLen + 1)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and one for its right hand side.
        self.int.variables.add(
            names = cplexLHSVars, lb = [-cplex.infinity] * picosLHSLen,
            ub = [+cplex.infinity] * picosLHSLen,
            types = self.int.variables.type.continuous * picosLHSLen)
        self.int.variables.add(
            names = [cplexRHSVar], lb = [0.0], ub = [+cplex.infinity],
            types = self.int.variables.type.continuous)

        # Add constraints that identify the left hand side CPLEX auxiliary
        # variables with their slice of the PICOS left hand side expression.
        cplexLHSConsLHSs = []
        cplexLHSConsRHSs = []
        for localConIndex, (localLinExp, localConstant) in \
                enumerate(self._affinexp_pic2cpl(picosLHS)):
            localConstant = -localConstant
            localLinExp.ind.append(cplexLHSVars[localConIndex])
            localLinExp.val.append(-1.0)
            cplexLHSConsLHSs.append(localLinExp)
            cplexLHSConsRHSs.append(localConstant)
        self.int.linear_constraints.add(
            names = cplexLHSCons, lin_expr = cplexLHSConsLHSs,
            senses = "E" * picosLHSLen, rhs = cplexLHSConsRHSs)

        # Add a constraint that identifies the right hand side CPLEX auxiliary
        # variable with the PICOS right hand side scalar expression.
        cplexRHSConLHS, cplexRHSConRHS = \
            self._scalar_affinexp_pic2cpl(-picosRHS)
        cplexRHSConRHS = -cplexRHSConRHS
        cplexRHSConLHS.ind.append(cplexRHSVar)
        cplexRHSConLHS.val.append(1.0)
        self.int.linear_constraints.add(
            names = [cplexRHSCon], lin_expr = [cplexRHSConLHS],
            senses = "E", rhs = [cplexRHSConRHS])

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS second order cone constraint itself.
        quadIndices = [cplexRHSVar] + list(cplexLHSVars)
        quadExpr = cplex.SparseTriple(
            ind1 = quadIndices, ind2 = quadIndices,
            val = [-1.0] + [1.0] * picosLHSLen)
        self.int.quadratic_constraints.add(
            name = cplexQuadCon, quad_expr = quadExpr, sense = "L", rhs = 0.0)

        cplexMetaCon = self.CplexSOCC(LHSVars=cplexLHSVars, RHSVar=cplexRHSVar,
            LHSCons=cplexLHSCons, RHSCon=cplexRHSCon, quadCon=cplexQuadCon)

        if self._debug():
            cplexCons = {
                "LHSs of LHS auxiliary equalities": cplexLHSConsLHSs,
                "RHSs of LHS auxiliary equalities": cplexLHSConsRHSs,
                "LHS of RHS auxiliary equality": cplexRHSConLHS,
                "RHS of RHS auxiliary equality": cplexRHSConRHS,
                "Non-positive quadratic term": quadExpr}
            self._debug(
                "SOcone constraint imported: {} → {}, {}".format(
                    picosConstraint, cplexMetaCon, cplexCons))

        return cplexMetaCon

    def _import_rscone_constraint(self, picosConstraint):
        import cplex
        assert isinstance(picosConstraint, RSOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS1 = picosConstraint.ub1
        picosRHS2 = picosConstraint.ub2
        picosLHSLen = len(picosLHS)

        # Make identifying names for the auxiliary variables and constraints.
        conID = self._get_unique_constraint_id()
        cplexLHSVars = ["{}:V{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSVars = ["{}:V{}".format(conID, picosLHSLen + i) for i in (0, 1)]
        cplexLHSCons = ["{}:C{}".format(conID, i) for i in range(picosLHSLen)]
        cplexRHSCons = ["{}:C{}".format(conID, picosLHSLen + i) for i in (0, 1)]
        cplexQuadCon =  "{}:C{}".format(conID, picosLHSLen + 2)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and two for its right hand side.
        self.int.variables.add(
            names = cplexLHSVars, lb = [-cplex.infinity] * picosLHSLen,
            ub = [+cplex.infinity] * picosLHSLen,
            types = self.int.variables.type.continuous * picosLHSLen)
        self.int.variables.add(
            names = cplexRHSVars, lb = [0.0, 0.0], ub = [+cplex.infinity] * 2,
            types = self.int.variables.type.continuous * 2)

        # Add constraints that identify the left hand side CPLEX auxiliary
        # variables with their slice of the PICOS left hand side expression.
        cplexLHSConsLHSs = []
        cplexLHSConsRHSs = []
        for localConIndex, (localLinExp, localConstant) in \
                enumerate(self._affinexp_pic2cpl(picosLHS)):
            localLinExp.ind.append(cplexLHSVars[localConIndex])
            localLinExp.val.append(-1.0)
            localConstant = -localConstant
            cplexLHSConsLHSs.append(localLinExp)
            cplexLHSConsRHSs.append(localConstant)
        self.int.linear_constraints.add(
            names = cplexLHSCons, lin_expr = cplexLHSConsLHSs,
            senses = "E" * picosLHSLen, rhs = cplexLHSConsRHSs)

        # Add two constraints that identify the right hand side CPLEX auxiliary
        # variables with the PICOS right hand side scalar expressions.
        cplexRHSConsLHSs = []
        cplexRHSConsRHSs = []
        for picosRHS, cplexRHSVar in zip((picosRHS1, picosRHS2), cplexRHSVars):
            linExp, constant = self._scalar_affinexp_pic2cpl(-picosRHS)
            linExp.ind.append(cplexRHSVar)
            linExp.val.append(1.0)
            constant = -constant
            cplexRHSConsLHSs.append(linExp)
            cplexRHSConsRHSs.append(constant)
        self.int.linear_constraints.add(
            names = cplexRHSCons, lin_expr = cplexRHSConsLHSs,
            senses = "E" * 2, rhs = cplexRHSConsRHSs)

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS rotated second order cone constraint itself.
        quadExpr = cplex.SparseTriple(
            ind1 = [cplexRHSVars[0]] + list(cplexLHSVars),
            ind2 = [cplexRHSVars[1]] + list(cplexLHSVars),
            val = [-1.0] + [1.0] * picosLHSLen)
        self.int.quadratic_constraints.add(
            name = cplexQuadCon, quad_expr = quadExpr, sense = "L", rhs = 0.0)

        cplexMetaCon = self.CplexRSOCC(
            LHSVars = cplexLHSVars, RHSVars = cplexRHSVars,
            LHSCons = cplexLHSCons, RHSCons = cplexRHSCons,
            quadCon = cplexQuadCon)

        if self._debug():
            cplexCons = {
                "LHSs of LHS auxiliary equalities": cplexLHSConsLHSs,
                "RHSs of LHS auxiliary equalities": cplexLHSConsRHSs,
                "LHSs of RHS auxiliary equalities": cplexRHSConsLHSs,
                "RHSs of RHS auxiliary equalities": cplexRHSConsRHSs,
                "Non-positive quadratic term": quadExpr}
            self._debug(
                "RScone constraint imported: {} → {}, {}".format(
                    picosConstraint, cplexMetaCon, cplexCons))

        return cplexMetaCon

    def _import_constraint(self, picosConstraint):
        # Import constraint based on type and keep track of the corresponding
        # CPLEX constraint and auxiliary variable names.
        if isinstance(picosConstraint, AffineConstraint):
            self._cplexLinConNames[picosConstraint] = \
                self._import_linear_constraint(picosConstraint)
        elif isinstance(picosConstraint, QuadConstraint):
            self._cplexQuadConName[picosConstraint] = \
                self._import_quad_constraint(picosConstraint)
        elif isinstance(picosConstraint, SOCConstraint):
            self._cplexSOCC[picosConstraint] = \
                self._import_socone_constraint(picosConstraint)
        elif isinstance(picosConstraint, RSOCConstraint):
            self._cplexRSOCC[picosConstraint] = \
                self._import_rscone_constraint(picosConstraint)
        else:
            assert False, "Constraint type belongs to unsupported problem type."

    def _remove_constraint(self, picosConstraint):
        if isinstance(picosConstraint, AffineConstraint):
            self.int.linear_constraints.delete(
                self._cplexLinConNames.pop(picosConstraint))
        elif isinstance(picosConstraint, QuadConstraint):
            self.int.quadratic_constraints.delete(
                self._cplexQuadConName.pop(picosConstraint))
        elif isinstance(picosConstraint, SOCConstraint):
            c = self._cplexSOCC.pop(picosConstraint)
            self.int.linear_constraints.delete(c.cplexLHSCons + [c.cplexRHSCon])
            self.int.quadratic_constraints.delete(c.cplexQuadCon)
            self.int.variables.delete(c.cplexLHSVars + [c.cplexRHSVar])
        elif isinstance(picosConstraint, RSOCConstraint):
            c = self._cplexRSOCC.pop(picosConstraint)
            self.int.linear_constraints.delete(c.cplexLHSCons + c.cplexRHSCons)
            self.int.quadratic_constraints.delete(c.cplexQuadCon)
            self.int.variables.delete(c.cplexLHSVars + c.cplexRHSVars)
        else:
            assert False, "Constraint type belongs to unsupported problem type."

    def _import_affine_objective(self, picosExpression):
        assert isinstance(picosExpression, AffinExp)

        cplexExpression = []
        for picosVar, picosCoefficient in picosExpression.factors.items():
            for localIndex in range(picosVar.dim):
                cplexCoefficient = picosCoefficient[localIndex]
                if not cplexCoefficient:
                    continue
                picosIndex = picosVar.startIndex + localIndex
                cplexName = self._cplexVarName[picosIndex]
                cplexExpression.append((cplexName, cplexCoefficient))
        if cplexExpression:
            self.int.objective.set_linear(cplexExpression)

            if self._debug():
                self._debug("Affine (part of) objective imported: {} → {}"
                    .format(picosExpression, cplexExpression))

    def _reset_affine_objective(self):
        linear = self.int.objective.get_linear()
        if any(linear):
            self.int.objective.set_linear(
                [(cplexVarIndex, 0.0) for cplexVarIndex, coefficient \
                in enumerate(linear) if coefficient])

    def _import_quadratic_objective(self, picosExpression):
        assert isinstance(picosExpression, QuadExp)

        # Import affine part of objective function.
        self._import_affine_objective(picosExpression.aff)

        # Import quadratic part of objective function.
        cplexQuadExpression = self._quadexp_pic2cpl(picosExpression)
        cplexQuadCoefficients = zip(
            cplexQuadExpression.ind1, cplexQuadExpression.ind2,
            [2.0 * coefficient for coefficient in cplexQuadExpression.val])
        self.int.objective.set_quadratic_coefficients(cplexQuadCoefficients)

    def _reset_quadratic_objective(self):
        quadratics = self.int.objective.get_quadratic()
        if quadratics:
            self.int.objective.set_quadratic(
                [(sparsePair.ind, [0]*len(sparsePair.ind)) \
                for sparsePair in quadratics])

    def _import_objective(self):
        picosSense, picosObjective = self.ext.objective

        # Import objective sense.
        if picosSense in ("find", "min"):
            cplexSense = self.int.objective.sense.minimize
        elif picosSense == "max":
            cplexSense = self.int.objective.sense.maximize
        else:
            raise NotImplementedError(
                "Objective sense '{0}' not supported by CPLEX."
                .format(picosSense))
        self.int.objective.set_sense(cplexSense)

        # Import objective function.
        if isinstance(picosObjective, AffinExp):
            self._import_affine_objective(picosObjective)
        elif isinstance(picosObjective, QuadExp):
            self._import_quadratic_objective(picosObjective)
        else:
            raise NotImplementedError(
                "Objective of type '{0}' not supported by CPLEX."
                .format(type(picosObjective)))

    def _reset_objective(self):
        self._reset_affine_objective()
        self._reset_quadratic_objective()

    def _import_problem(self):
        import cplex

        # Create a problem instance.
        self.int = cplex.Cplex()

        # Import variables.
        for variable in self.ext.variables.values():
            self._import_variable(variable)

        # Import constraints.
        for constraint in self.ext.constraints:
            self._import_constraint(constraint)

        # Set objective.
        self._import_objective()

    def _update_problem(self):
        for oldConstraint in self._removed_constraints():
            self._remove_constraint(oldConstraint)

        for oldVariable in self._removed_variables():
            self._remove_variable(oldVariable)

        for newVariable in self._new_variables():
            self._import_variable(newVariable)

        for newConstraint in self._new_constraints():
            self._import_constraint(newConstraint)

        if self._objective_has_changed():
            self._reset_objective()
            self._import_objective()

    def _solve(self):
        import cplex

        # Reset options.
        self.int.parameters.reset()

        # Handle "verbose" option.
        verbosity = self.ext.options["verbose"]
        if verbosity <= 0:
            # Note that this behaviour disables warning even with a verbosity of
            # zero but this is still better than having verbose output for every
            # option that is set.
            self.int.set_results_stream(None)
        else:
            self.int.parameters.barrier.display.set(min(2, verbosity))
            self.int.parameters.conflict.display.set(min(2, verbosity))
            self.int.parameters.mip.display.set(min(5, verbosity))
            self.int.parameters.sifting.display.set(min(2, verbosity))
            self.int.parameters.simplex.display.set(min(2, verbosity))
            self.int.parameters.tune.display.set(min(3, verbosity))
        self.int.set_error_stream(None) # Already handled as exceptions.

        # Handle "tol" option.
        if self.ext.options["tol"] is not None:
            tol = self.ext.options["tol"]
            self.int.parameters.barrier.convergetol.set(tol)
            self.int.parameters.barrier.qcpconvergetol.set(tol)

        # Handle "gaplim" option.
        if self.ext.options["gaplim"] is not None:
            self.int.parameters.mip.tolerances.mipgap.set(
                self.ext.options["gaplim"])

        # Handle "maxit" option.
        if self.ext.options["maxit"] is not None:
            maxit = self.ext.options["maxit"]
            self.int.parameters.barrier.limits.iteration.set(maxit)
            self.int.parameters.simplex.limits.iterations.set(maxit)

        # Handle "lp_node_method" option.
        if self.ext.options["lp_node_method"] is not None:
            method = self.ext.options["lp_node_method"]
            if method == "interior":
                self.int.parameters.mip.strategy.subalgorithm.set(4)
            elif method== "psimplex":
                self.int.parameters.mip.strategy.subalgorithm.set(1)
            elif method == "dsimplex":
                self.int.parameters.mip.strategy.subalgorithm.set(2)
            else:
                self._handle_bad_option_value("lp_node_method")

        # Handle "lp_root_method" option.
        if self.ext.options["lp_root_method"] is not None:
            method = self.ext.options["lp_root_method"]
            if method == "interior":
                self.int.parameters.lpmethod.set(4)
            elif method== "psimplex":
                self.int.parameters.lpmethod.set(1)
            elif method == "dsimplex":
                self.int.parameters.lpmethod.set(2)
            else:
                self._handle_bad_option_value("lp_root_method")

        # Handle "timelimit" option.
        if self.ext.options["timelimit"] is not None:
            self.int.parameters.timelimit.set(self.ext.options["timelimit"])

        # Handle "treememory" option.
        if self.ext.options["treememory"] is not None:
            self.int.parameters.mip.limits.treememory.set(
                self.ext.options["treememory"])

        # Handle option conflict between "nbsol" and "pool_size".
        if self.ext.options["nbsol"] is not None \
        and self.ext.options["pool_size"] is not None:
            raise ConflictingOptionsError("The options 'nbsol' and 'pool_size' "
                "cannot be used in conjunction.")

        # Handle "nbsol" option.
        if self.ext.options["nbsol"] is not None:
            self.int.parameters.mip.limits.solutions.set(
                self.ext.options["nbsol"])

        # Handle "pool_size" option.
        if self.ext.options["pool_size"] is not None:
            maxNumSolutions = max(1, int(self.ext.options["pool_size"]))
            self.int.parameters.mip.limits.populate.set(maxNumSolutions)
            self._verbose("")
        else:
            maxNumSolutions = 1

        # Handle "pool_relgap" option.
        if self.ext.options["pool_relgap"] is not None:
            if self.ext.options["pool_size"] is None:
                raise DependentOptionError("The option 'pool_relgap' requires "
                    "the option 'pool_size'.")
            self.int.parameters.mip.pool.relgap.set(
                self.ext.options["pool_relgap"])

        # Handle "pool_absgap" option.
        if self.ext.options["pool_absgap"] is not None:
            if self.ext.options["pool_size"] is None:
                raise DependentOptionError("The option 'pool_absgap' requires "
                    "the option 'pool_size'.")
            self.int.parameters.mip.pool.absgap.set(
                self.ext.options["pool_absgap"])

        # Handle "hotstart" option.
        if self.ext.options["hotstart"]:
            names, values = [], []
            for picosVar in self.ext.variables.values():
                if picosVar.is_valued():
                    for localIndex in range(picosVar.dim):
                        picosIndex = picosVar.startIndex + localIndex
                        cplexName = self._cplexVarName[picosIndex]
                        names.append(cplexName)
                        values.append(picosVar.valueAsMatrix[localIndex])
            if names:
                self.int.MIP_starts.add(
                    cplex.SparsePair(ind=names, val=values),
                    self.int.MIP_starts.effort_level.repair)

        # Handle CPLEX-specific options.
        for option, value in self.ext.options["cplex_params"].items():
            try:
                parameter = eval("self.int.parameters." + option)
                parameter.set(value)
            except AttributeError:
                self._handle_bad_option_value("cplex_params",
                    "CPLEX option '{}' does not exist.".format(option))
            except cplex.exceptions.errors.CplexError:
                self._handle_bad_option_value("cplex_params",
                    "Invalid value '{}' for CPLEX option '{}'."
                    .format(value, option))

        # Handle options "uboundlimit", "lboundlimit" and "boundMonitor" via a
        # CPLEX callback handler.
        callback = None
        if self.ext.options["uboundlimit"] or self.ext.options["lboundlimit"] \
        or self.ext.options["boundMonitor"]:
            from cplex.callbacks import MIPInfoCallback

            class PicosInfoCallback(MIPInfoCallback):
                def __call__(self):
                    v1 = self.get_incumbent_objective_value()
                    v2 = self.get_best_objective_value()
                    ub = max(v1, v2)
                    lb = min(v1, v2)
                    if self.bounds is not None:
                        elapsedTime = time.time() - self.startTime
                        self.bounds.append((elapsedTime, lb, ub))
                    if self.lbound is not None and lb >= self.lbound:
                        self.printer("The specified lower bound was reached, "
                            "so PICOS will ask CPLEX to stop the search.")
                        self.abort()
                    if self.ubound is not None and ub <= self.ubound:
                        self.printer("The specified upper bound was reached, "
                            "so PICOS will ask CPLEX to stop the search.")
                        self.abort()

            # Register the callback handler with CPLEX.
            callback = self.int.register_callback(PicosInfoCallback)

            # Pass parameters to the callback handler. Note that
            # callback.startTime will be set just before optimization begins.
            callback.printer = self._verbose
            callback.ubound = self.ext.options['uboundlimit']
            callback.lbound = self.ext.options['lboundlimit']
            callback.bounds = [] if self.ext.options['boundMonitor'] else None

        # Inform CPLEX about the problem type.
        # This seems necessary, as otherwise LP can get solved as MIP, producing
        # misleading status output (e.g. "not integer feasible").
        picosType = self.ext.type
        if picosType == "LP":
            cplexType = self.int.problem_type.LP
        elif picosType == "QP":
            cplexType = self.int.problem_type.QP
        elif picosType in ("SOCP", "QCQP", "Mixed (SOCP+quad)"):
            cplexType = self.int.problem_type.QCP
        elif picosType == "MIP":
            cplexType = self.int.problem_type.MILP
        elif picosType == "MIQP":
            cplexType = self.int.problem_type.MIQP
        elif picosType in ("MISOCP", "MIQCP", "Mixed (MISOCP+quad)"):
            cplexType = self.int.problem_type.MIQCP
        else:
            cplexType = None
            self._verbose(
                "PICOS is not sure how to inform CPLEX that the problem type is"
                "'{}', and will trust CPLEX to detect this correctly."
                .format(picosType))
        if cplexType is not None:
            self.int.set_problem_type(cplexType)

        # Attempt to solve the problem.
        if callback:
            callback.startTime = time.time()
        with self._header(), self._stopwatch():
            try:
                if maxNumSolutions > 1:
                    self.int.populate_solution_pool()
                    numSolutions = self.int.solution.pool.get_num()
                else:
                    self.int.solve()
                    numSolutions = 1
            except cplex.exceptions.errors.CplexSolverError as error:
                if error.args[2] == 5002:
                    raise NonConvexError(str(error))
                else:
                    raise

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        else:
            primals = {}
            for solution in range(numSolutions):
                for varName, picosVar in self.ext.variables.items():
                    try:
                        cplexNames = []

                        for localIndex in range(picosVar.dim):
                            picosIndex = picosVar.startIndex + localIndex
                            cplexNames.append(self._cplexVarName[picosIndex])
                        if maxNumSolutions > 1:
                            value = self.int.solution.pool.get_values(
                                solution, cplexNames)
                        else:
                            value = self.int.solution.get_values(cplexNames)

                        if maxNumSolutions > 1:
                            varName = (solution, varName)
                        primals[varName] = value
                    except cplex.exceptions.errors.CplexSolverError:
                        primals[varName] = None

        # Retrieve duals.
        # Note that the solution pool only applies to mixed integer programs,
        # which do not come with duals.
        if self.ext.options["noduals"] or not self.ext.is_continuous():
            duals = None
        else:
            duals = []
            for picosConstraint in self.ext.constraints:
                try:
                    if isinstance(picosConstraint, AffineConstraint):
                        cplexConstraints = self._cplexLinConNames[picosConstraint]
                        values = self.int.solution.get_dual_values(cplexConstraints)
                        picosDual = cvxopt.matrix(values, picosConstraint.size)

                        # Flip sign based on constraint relation.
                        if picosConstraint.is_decreasing():
                            picosDual = -picosDual
                    elif isinstance(picosConstraint, SOCConstraint):
                        cplexMetaCon = self._cplexSOCC[picosConstraint]
                        lb = self.int.solution.get_dual_values(cplexMetaCon.RHSCon)
                        z = self.int.solution.get_dual_values(
                            list(cplexMetaCon.LHSCons))
                        picosDual = cvxopt.matrix([lb] + z)
                    elif isinstance(picosConstraint, RSOCConstraint):
                        cplexMetaCon = self._cplexRSOCC[picosConstraint]
                        ab = [x for x in self.int.solution.get_dual_values(
                            list(cplexMetaCon.RHSCons))]
                        z = self.int.solution.get_dual_values(
                            list(cplexMetaCon.LHSCons))
                        picosDual = cvxopt.matrix(ab + z)
                    elif isinstance(picosConstraint, QuadConstraint):
                        picosDual = None
                    else:
                        assert False, \
                            "Constraint type belongs to unsupported problem type."

                    # Flip sign based on objective sense.
                    if picosDual and self.ext.objective[0] == "min":
                        picosDual = -picosDual
                except cplex.exceptions.errors.CplexSolverError:
                    duals.append(None)
                else:
                    duals.append(picosDual)

        # Retrieve objective value.
        try:
            if maxNumSolutions > 1:
                objectiveValue = []
                for solution in range(numSolutions):
                    objectiveValue.append(
                        self.int.solution.pool.get_objective_value(solution))
            else:
                objectiveValue = self.int.solution.get_objective_value()
        except cplex.exceptions.errors.CplexSolverError:
            objectiveValue = None

        # Retrieve solution metadata.
        meta = {}

        # Set common entry "status".
        meta["status"] = self.int.solution.get_status_string()

        # Set CPLEX-specific entry "boundMonitor".
        if self.ext.options["boundMonitor"]:
            meta["bounds_monitor"] = callback.bounds

        return (primals, duals, objectiveValue, meta)
