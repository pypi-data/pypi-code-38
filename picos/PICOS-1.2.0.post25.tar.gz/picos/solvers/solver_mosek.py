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
# This file implements the MOSEK 8/9 solver through its low level Optimizer API.
# The low level API is tedious to interface, but is currently much faster than
# the high level Fusion API, which would be the prefered interface otherwise.
#-------------------------------------------------------------------------------

import sys
import math
import cvxopt

from ..expressions import *
from ..constraints import *

from .solver import *

class MOSEKSolver(Solver):
    @classmethod
    def test_availability(cls):
        import mosek

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
        yield QuadConstraint
        yield SOCConstraint
        yield RSOCConstraint
        yield LMIConstraint

    @classmethod
    def supports_quad_socp_mix(cls):
        return False

    @classmethod
    def support_level(cls, problem):
        # MOSEK does not support mixed integer SDPs.
        if not problem.is_continuous() \
            and any([True for constraint in problem.constraints
                if constraint.__class__ is LMIConstraint]):
            return SUPPORT_LEVEL_NONE

        return super(MOSEKSolver, cls).support_level(problem)

    def __init__(self, problem):
        super(MOSEKSolver, self).__init__(
            problem, "MOSEK (Optimizer)", "MOSEK via Optimizer API")

        self._mosekVarOffset = dict()
        """Maps a PICOS (multidimensional) variable to a MOSEK scalar variable
        (start) index."""

        self._mosekLinConOffset = dict()
        """Maps a PICOS (multidimensional) linear constraint to a MOSEK scalar
        constraint (start) index."""

        self._mosekQuadConIndex = dict()
        """Maps a PICOS quadratic constraint to a MOSEK constraint index."""

        self._mosekCone = dict()
        """
        Maps a PICOS SOCC or RSOCC to a triple:

        - The first entry is the index of a MOSEK conic constraint.
        - The second entry is a list of MOSEK scalar (auxiliary) variable
          indices that appear in the MOSEK conic constraint.
        - The third entry is another list of same size containing auxiliary
          constraints (or None). If an entry in the second list is None, then
          the corresponding index in the first list is of a proper MOSEK scalar
          variable instead of an auxiliary one, which can happen at most once
          per variable and only if the structure of the PICOS constraint allows
          it (that is, if the repspective entry of the cone member happens to be
          a PICOS scalar variable as opposed to a composed affine expression).
        """

        self._mosekLMI = dict()
        """Maps a PICOS LMI to a pair representing its MOSEK representation. The
        first entry is the index of a MOSEK symmetric PSD "bar variable", the
        second entry is the offset for a number of scalar linear equalities."""

        self._mosekBarUnitCoefs = dict()
        """Maps the row (column) count of a symmetric matrix to a list of MOSEK
        symmetric coefficient matrices. More precisely, if X is a n×n symmetric
        matrix, 0 ≤ k ≤ n*(n+1)/2, then <_mosekBarUnitCoefs[n][k], X> = h(X)[k]
        where h refers to the lower-triangular, column-major half-vectorization
        of X. These matrices are used to represent LMIs. Unlike values of
        _mosekLMI, they are shared between LMIs of same size."""

    def reset_problem(self):
        self.int = None

        self._mosekVarOffset.clear()
        self._mosekLinConOffset.clear()
        self._mosekQuadConIndex.clear()
        self._mosekCone.clear()
        self._mosekLMI.clear()
        self._mosekBarUnitCoefs.clear()

    @classmethod
    def _get_environment(cls):
        if not hasattr(cls, "mosekEnvironment"):
            import mosek
            cls.mosekEnvironment = mosek.Env()

        return cls.mosekEnvironment

    env = property(lambda self: self.__class__._get_environment())
    """This references a MOSEK environment, which is shared among all
    MOSEKSolver instances. (The MOSEK documentation states that "[a]ll tasks in
    the program should share the same environment.")"""

    @classmethod
    def _get_major_version(cls):
        if not hasattr(cls, "mosekVersion"):
            import mosek
            cls.mosekVersion = mosek.Env.getversion()

        return cls.mosekVersion[0]

    ver = property(lambda self: self.__class__._get_major_version())
    """The major version of the available MOSEK library."""

    @classmethod
    def _get_solution_status_map(cls):
        if not hasattr(cls, "solstaMap"):
            from mosek import solsta

            cls.solstaMap = {
                    solsta.unknown:                 "unknown",
                    solsta.optimal:                 "optimal",
                    solsta.prim_feas:               "primal feasible",
                    solsta.dual_feas:               "dual feasible",
                    solsta.prim_and_dual_feas:      "feasible",
                    solsta.prim_infeas_cer:         "primal infeasible",
                    solsta.dual_infeas_cer:         "dual infeasible",
                    solsta.prim_illposed_cer:       "primal illposed",
                    solsta.dual_illposed_cer:       "dual illposed",
                    solsta.integer_optimal:         "integer optimal"
            }

            if cls._get_major_version() < 9:
                cls.solstaMap.update({
                    solsta.near_optimal:            "near optimal",
                    solsta.near_prim_feas:          "near primal feasible",
                    solsta.near_dual_feas:          "near dual feasible",
                    solsta.near_prim_and_dual_feas: "near feasible",
                    solsta.near_prim_infeas_cer:    "near primal infeasible",
                    solsta.near_dual_infeas_cer:    "near dual infeasible",
                    solsta.near_integer_optimal:    "near integer optimal"
                })

        return cls.solstaMap

    @classmethod
    def _status_string(cls, statusCode):
        try:
            return cls._get_solution_status_map()[statusCode]
        except KeyError:
            return "unknown"

    @staticmethod
    def _streamprinter(text):
        sys.stdout.write(text)
        sys.stdout.flush()

    @staticmethod
    def _low_tri_indices(rowCount):
        """
        Yields lower triangular (row, col) indices in column-major order.
        """
        for col in range(rowCount):
            for row in range(col, rowCount):
                yield (row, col)

    def _scalar_affinexp_pic2msk(self, picosExpression):
        assert len(picosExpression) is 1
        return picosExpression.sparse_rows(self._mosekVarOffset)[0]

    def _affinexp_pic2msk(self, picosExpression):
        return picosExpression.sparse_rows(self._mosekVarOffset)

    def _quadexp_pic2msk(self, picosExpression):
        """
        Tranforms the quadratic part of a PICOS quadratic expression to a
        symmetric, sparse biliniar form of which only the lower triangular
        entries are given, and that can be used with MOSEK's variable vector.
        Note that MOSEK applies a built-in factor of 0.5 to all biliniar forms
        while PICOS doesn't, so a factor of 2 is applied here to cancel it out.
        """
        assert isinstance(picosExpression, QuadExp)
        numVars = self.int.getnumvar()

        # Make a sparse representation of the strict lower, diagonal and strict
        # upper parts of the matrix.
        IL, JL, VL = [], [], []
        ID, JD, VD = [], [], []
        IU, JU, VU = [], [], []
        for (picosVar1, picosVar2), picosCoefs in picosExpression.quad.items():
            for sparseIndex in range(len(picosCoefs)):
                localVar1Index   = picosCoefs.I[sparseIndex]
                localVar2Index   = picosCoefs.J[sparseIndex]
                localCoefficient = picosCoefs.V[sparseIndex]
                mskVar1Index = self._mosekVarOffset[picosVar1] + localVar1Index
                mskVar2Index = self._mosekVarOffset[picosVar2] + localVar2Index

                if   mskVar2Index < mskVar1Index:
                    I, J, V = IL, JL, VL
                elif mskVar1Index < mskVar2Index:
                    I, J, V = IU, JU, VU
                else:
                    I, J, V = ID, JD, VD

                I.append(mskVar1Index)
                J.append(mskVar2Index)
                V.append(localCoefficient)

        # Compute the lower triangular part of the biliniar form.
        L = cvxopt.spmatrix(VL, IL, JL, (numVars, numVars))
        D = cvxopt.spmatrix(VD, ID, JD, (numVars, numVars))
        U = cvxopt.spmatrix(VU, IU, JU, (numVars, numVars))
        Q = 2*D + L + U.T

        # Return it as a sparse triple for MOSEK to consume.
        return list(Q.I), list(Q.J), list(Q.V)

    def _import_variable(self, picosVar):
        import mosek

        numVars = self._mosekVarOffset[picosVar] = self.int.getnumvar()
        varDim  = picosVar.dim
        indices = range(numVars, numVars + varDim)
        self.int.appendvars(varDim)

        # Set the variable type.
        if picosVar.vtype in ("binary", "integer"):
            self.int.putvartypelist(
                indices, [mosek.variabletype.type_int]*varDim)

        # Import bounds.
        # NOTE: The MOSEK documentation claims that "[a]ppended variables will
        #       be fixed at zero." Therefor, we make a dense import of bounds.
        if picosVar.vtype is "binary":
            self.int.putvarboundlist(
                indices, [mosek.boundkey.ra]*varDim, [0]*varDim, [1]*varDim)
        elif picosVar.vtype in ("continuous", "integer", "symmetric"):
            boundKeys   = [mosek.boundkey.fr]*varDim
            lowerBounds = [0.0]*varDim
            upperBounds = [0.0]*varDim

            for localIndex in range(varDim):
                lower, upper = picosVar.bnd.get(localIndex, (None, None))

                if lower is None and upper is None:
                    pass
                elif lower is not None and upper is not None:
                    if lower == upper:
                        boundKeys[localIndex] = mosek.boundkey.fx
                    else:
                        boundKeys[localIndex] = mosek.boundkey.ra
                    lowerBounds[localIndex] = lower
                    upperBounds[localIndex] = upper
                elif lower is not None:
                    boundKeys[localIndex]   = mosek.boundkey.lo
                    lowerBounds[localIndex] = lower
                else:
                    boundKeys[localIndex]   = mosek.boundkey.up
                    upperBounds[localIndex] = upper

            self.int.putvarboundlist(
                indices, boundKeys, lowerBounds, upperBounds)
        else:
            raise NotImplementedError("Variable type '{}' not supported by "
                "MOSEK.".format(picosVar.vtype))

    def _import_linear_constraint(self, picosConstraint):
        import mosek

        numCons = self.int.getnumcon()
        conLen  = len(picosConstraint)
        self.int.appendcons(conLen)

        rows = picosConstraint.sparse_Ab_rows(self._mosekVarOffset)

        if picosConstraint.is_equality():
            boundKey = mosek.boundkey.fx
        elif picosConstraint.is_increasing():
            boundKey = mosek.boundkey.up
        else:
            boundKey = mosek.boundkey.lo

        for localConIndex, (mosekVarIndices, coefs, offset) in enumerate(rows):
            mosekConIndex = numCons + localConIndex

            self.int.putarow(mosekConIndex, mosekVarIndices, coefs)
            self.int.putconbound(mosekConIndex, boundKey, offset, offset)

        self._mosekLinConOffset[picosConstraint] = numCons

    def _import_quad_constraint(self, picosConstraint):
        # Import the linear part first.
        picosLinConPart = picosConstraint.le0.aff < 0
        self._import_linear_constraint(picosLinConPart)
        mosekConIndex = self._mosekLinConOffset.pop(picosLinConPart)

        # Add the quadratic part.
        self.int.putqconk(
            mosekConIndex, *self._quadexp_pic2msk(picosConstraint.le0))

        self._mosekQuadConIndex[picosConstraint] = mosekConIndex

    def _var_was_used_in_cone(self, mosekVariableIndex, usedJustNow = []):
        if mosekVariableIndex in usedJustNow:
            return True
        for _, mosekVarIndices, _ in self._mosekCone.values():
            if mosekVariableIndex in mosekVarIndices:
                return True
        return False

    def _import_quad_conic_constraint(self, picosConstraint):
        import mosek

        isRotated = isinstance(picosConstraint, RSOCConstraint)
        mosekVars, mosekCons = [], [None]*len(picosConstraint)

        # Get an initial MOSEK representation of the cone member.
        entries = []
        if isRotated:
            # MOSEK internally adds a factor of 2 to the upper bound while PICOS
            # doesn't, so cancel it out by adding a factor of 1/sqrt(2) to both
            # factors of the upper bound.
            f = 1.0 / math.sqrt(2.0)
            entries.append(self._scalar_affinexp_pic2msk(f*picosConstraint.ub1))
            entries.append(self._scalar_affinexp_pic2msk(f*picosConstraint.ub2))
        else:
            entries.append(self._scalar_affinexp_pic2msk(picosConstraint.ub))
        entries += self._affinexp_pic2msk(picosConstraint.ne)

        # Map cone member entries to existing MOSEK variables, if possible.
        mosekVarsMissing = []
        for scalarVarNum, (indices, values, offset) in enumerate(entries):
            if len(values) == 1 and values[0] == 1.0 and offset == 0.0 \
            and not self._var_was_used_in_cone(indices[0], mosekVars):
                mosekVars.append(indices[0])
            else:
                mosekVars.append(None)
                mosekVarsMissing.append(scalarVarNum)

        # Create auxiliary variables and constraints.
        numAux = len(mosekVarsMissing)
        auxVarOffset = self.int.getnumvar()
        auxConOffset = self.int.getnumcon()
        self.int.appendvars(numAux)
        self.int.appendcons(numAux)

        # Mosek fixes (!) new variables at zero, so set them free.
        self.int.putvarboundlist(range(auxVarOffset, auxVarOffset + numAux),
            [mosek.boundkey.fr]*numAux, [0.0]*numAux, [0.0]*numAux)

        # Constrain the auxiliary variables to be equal to the cone member
        # entries for which no existing MOSEK variable could be used.
        for auxNum, missingVarIndex in enumerate(mosekVarsMissing):
            auxVarIndex = auxVarOffset + auxNum
            auxConIndex = auxConOffset + auxNum

            # Prepare the auxiliary constraint.
            indices, values, offset = entries[missingVarIndex]

            # TODO: Instead of always creating a constraint, fix variables via
            #       their bound whenever possible.
            # if len(indices) is 0:
            #     if self._debug():
            #         self._debug("  Fixing MOSEK auxiliary variable: "
            #                 "x[{}] = {}".format(auxVarIndex, offset))
            #
            #     self.int.putvarbound(
            #         auxVarIndex, mosek.boundkey.fx, offset, offset)
            # else:
            indices.append(auxVarIndex)
            values.append(-1.0)

            if self._debug():
                self._debug("  Adding MOSEK auxiliary constraint: "
                    "{}.T * x{} = {}".format(values, indices, -offset))

            # Add the auxiliary constraint.
            self.int.putarow(auxConIndex, indices, values)
            self.int.putconbound(
                auxConIndex, mosek.boundkey.fx, -offset, -offset)

            # Complete the mapping of cone member entries to MOSEK (auxiliary)
            # variables (and auxiliary constraints).
            mosekVars[missingVarIndex] = auxVarIndex
            mosekCons[missingVarIndex] = auxConIndex

        if self._debug():
            self._debug("  Adding MOSEK conic constraint: {} in {}".format(
                mosekVars, "Qr" if isRotated else "Q"))

        # Add the conic constraint.
        coneIndex = self.int.getnumcone()
        mosekCone = mosek.conetype.rquad if isRotated else mosek.conetype.quad
        self.int.appendcone(mosekCone, 0.0, mosekVars)

        self._mosekCone[picosConstraint] = (coneIndex, mosekVars, mosekCons)

    def _import_sdp_constraint(self, picosConstraint):
        import mosek

        rowCount  = picosConstraint.size[0]
        dimension = (rowCount*(rowCount + 1)) // 2

        # MOSEK does not support general LMIs but so called "bar vars" which
        # are variables in the symmetric positive semidefinite cone. We use them
        # in combination with linear equalities to represent the LMI.
        barVar         = self.int.getnumbarvar()
        mosekConOffset = self.int.getnumcon()
        self.int.appendbarvars([rowCount])
        self.int.appendcons(dimension)

        # MOSEK uses a storage of symmetric coefficient matrices that are used
        # as dot product coefficients to build scalar constraints involving both
        # "bar vars" and normal scalar variables. We build a couple of these
        # matrices to be able to select individual entries of our "bar vars".
        # More precisely, if X is a n×n symmetric matrix and 0 ≤ k ≤ n*(n+1)/2,
        # then <Units[n][k],X> = h(X)[k] where h refers to the lower-triangular,
        # column-major half-vectorization of X.
        if rowCount in self._mosekBarUnitCoefs:
            Units = self._mosekBarUnitCoefs[rowCount]
        else:
            Units = self._mosekBarUnitCoefs[rowCount] = [
                self.int.appendsparsesymmat(
                    rowCount, [row], [col], [1.0 if row == col else 0.5])
                for row, col in self._low_tri_indices(rowCount)]

        # We iterate over the lower triangular scalar sub-expressions of the
        # expression that the PICOS constraint states to be PSD, and constrain
        # them to be eqal to the MOSEK "bar var" at the same index.
        psd = picosConstraint.psd
        psdRows = psd.sparse_rows(self._mosekVarOffset, lowerTriangle = True)
        for svecIndex, (row, col) in enumerate(self._low_tri_indices(rowCount)):
            localIndex    = row * psd.size[0] + col
            mosekConIndex = mosekConOffset + svecIndex
            indices, coefficients, offset = psdRows[localIndex]

            # The lower-triangular entries in the PSD-constrained matrix …
            self.int.putarow(mosekConIndex, indices, coefficients)

            # … minus the corresponding bar var entries …
            self.int.putbaraij(
                mosekConIndex, barVar, [Units[svecIndex]], [-1.0])

            # … should equal zero.
            self.int.putconbound(
                mosekConIndex, mosek.boundkey.fx, -offset, -offset)

            if self._debug():
                self._debug("  Index {} ({}, {}): indices = {}, coefs = {}"
                    .format(svecIndex, row, col, indices, coefficients))

        self._mosekLMI[picosConstraint] = (barVar, mosekConOffset)

    def _import_constraint(self, picosConstraint):
        if self._debug():
            self._debug("Importing Constraint: {}".format(picosConstraint))

        if   isinstance(picosConstraint, AffineConstraint):
            self._import_linear_constraint(picosConstraint)
        elif isinstance(picosConstraint, QuadConstraint):
            self._import_quad_constraint(picosConstraint)
        elif isinstance(picosConstraint, SOCConstraint) \
        or   isinstance(picosConstraint, RSOCConstraint):
            self._import_quad_conic_constraint(picosConstraint)
        elif isinstance(picosConstraint, LMIConstraint):
            self._import_sdp_constraint(picosConstraint)
        else:
            assert False, "Constraint type not supported."

    def _reset_objective(self):
        # Reset affine part.
        numVars = self.int.getnumvar()
        self.int.putclist(range(numVars), [0.0]*numVars)
        self.int.putcfix(0.0)

        # Reset quadratic part.
        self.int.putqobj([], [], [])

    def _import_affine_objective(self, picosObjective):
        mosekIndices      = []
        mosekCoefficients = []

        for picosVar, picosCoef in picosObjective.factors.items():
            for localIndex in range(picosVar.dim):
                if picosCoef[localIndex]:
                    mosekIndex = self._mosekVarOffset[picosVar] + localIndex
                    mosekIndices.append(mosekIndex)
                    mosekCoefficients.append(picosCoef[localIndex])

        self.int.putclist(mosekIndices, mosekCoefficients)

        if picosObjective.constant is not None:
            self.int.putcfix(picosObjective.constant[0])

    def _import_quadratic_objective(self, picosObjective):
        # Import the quadratic part.
        self.int.putqobj(*self._quadexp_pic2msk(picosObjective))

        # Import the affine part.
        self._import_affine_objective(picosObjective.aff)

    def _import_objective(self):
        import mosek

        picosSense, picosObjective = self.ext.objective

        # Import objective sense.
        if picosSense in ("find", "min"):
            self.int.putobjsense(mosek.objsense.minimize)
        elif picosSense == "max":
            self.int.putobjsense(mosek.objsense.maximize)
        else:
            raise NotImplementedError("Objective sense '{}' not supported by "
                "MOSEK.".format(picosSense))

        # Import objective function.
        if isinstance(picosObjective, AffinExp):
            self._import_affine_objective(picosObjective)
        elif isinstance(picosObjective, QuadExp):
            self._import_quadratic_objective(picosObjective)
        else:
            raise NotImplementedError(
                "Objective of type '{}' not supported by MOSEK."
                .format(type(picosObjective)))

    def _import_problem(self):
        # Create a problem instance.
        self.int = self.env.Task()

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
            raise ProblemUpdateError("PICOS does not support removing "
                "constraints from a MOSEK instance.")

        for oldVariable in self._removed_variables():
            raise ProblemUpdateError("PICOS does not support removing variables"
                " from a MOSEK instance.")

        for newVariable in self._new_variables():
            self._import_variable(newVariable)

        for newConstraint in self._new_constraints():
            self._import_constraint(newConstraint)

        if self._objective_has_changed():
            self._reset_objective()
            self._import_objective()

    def _solve(self):
        import mosek

        # Reset all solver options to default.
        self.int.setdefaults()

        # Handle "verbose" option.
        if self.ext._verbose():
            self.int.set_Stream(mosek.streamtype.log, self._streamprinter)
            self.int.putintparam(mosek.iparam.log, self.ext.verbosity())

        # Handle "tol" option.
        if self.ext.options["tol"] is not None:
            # Domains:
            # - "": linear,
            # - "co": conic,
            # - "nl": nonlinear (MOSEK < 9)
            # - "qo": quadratic
            # Tolerances:
            # - "pfeas": primal feasibility,
            # - "dfeas": dual feasibility,
            # - "mu_red": relative complementary gap,
            # - "rel_gap": relative gap termination tolerance
            # Omitted tolerances:
            # - "infeas": infeasibility,
            # - "near_rel": (not actually a tolerance)
            for domain in ("", "co", "qo") + (("nl",) if self.ver < 9 else ()):
                for tolerance in ("pfeas", "dfeas", "mu_red", "rel_gap"):
                    parameter = "msk_dpar_intpnt_{}{}tol_{}".format(
                        domain, "_" if domain else "", tolerance).upper()
                    self.int.putnadouparam(parameter, self.ext.options["tol"])

        # Handle "gaplim" option.
        if self.ext.options["gaplim"] is not None:
            self.int.putdouparam(
                mosek.dparam.mio_tol_rel_gap, self.ext.options["gaplim"])

        # Handle "maxit" option.
        if self.ext.options["maxit"] is not None:
            for subsolver in ("bi", "intpnt", "sim"):
                option = "msk_ipar_{}_max_iterations".format(subsolver).upper()
                self.int.putnaintparam(option, self.ext.options["maxit"])

        # Handle "lp_node_method" option.
        if self.ext.options["lp_node_method"] is not None:
            method = self.ext.options["lp_node_method"]
            if   method == "interior":
                self.int.putstrparam(
                    mosek.sparam.mio_node_optimizer, "intpnt")
            elif method == "psimplex":
                self.int.putstrparam(
                    mosek.sparam.mio_node_optimizer, "primal_simplex")
            elif method == "dsimplex":
                self.int.putstrparam(
                    mosek.sparam.mio_node_optimizer, "dual_simplex")
            else:
                self._handle_bad_option_value("lp_node_method")

        # Handle "lp_root_method" option.
        if self.ext.options["lp_root_method"] is not None:
            method = self.ext.options["lp_root_method"]
            if   method == "interior":
                self.int.putstrparam(
                    mosek.sparam.mio_root_optimizer, "intpnt")
            elif method == "psimplex":
                self.int.putstrparam(
                    mosek.sparam.mio_root_optimizer, "primal_simplex")
            elif method == "dsimplex":
                self.int.putstrparam(
                    mosek.sparam.mio_root_optimizer, "dual_simplex")
            else:
                self._handle_bad_option_value("lp_node_method")

        # Handle "timelimit" option.
        if self.ext.options["timelimit"] is not None:
            value = float(self.ext.options["timelimit"])
            for subsolver in ("optimizer", "mio"):
                option = "msk_dpar_{}_max_time".format(subsolver).upper()
                self.int.putnadouparam(option, value)

        # Handle "nbsol" option.
        if self.ext.options["nbsol"] is not None:
            self.int.putintparam(
                mosek.iparam.mio_max_num_solutions, self.ext.options["nbsol"])

        # Handle MOSEK-specific options.
        for option, value in self.ext.options["mosek_params"].items():
            try:
                self.int.putparam(option.upper(), str(value))
            except mosek.Error as error:
                self._handle_bad_option_value("mosek_params", str(error))

        # Handle unsupported options.
        # TODO: Handle "hotstart" option (via mio_construct_sol).
        self._handle_unsupported_option("hotstart", "treememory")

        # Determine whether a basic solution will be available.
        isLP = isinstance(self.ext.objective[1], AffinExp) and all(
            [isinstance(c, AffineConstraint) for c in self.ext.constraints])

        # Attempt to solve the problem.
        try:
            with self._header(), self._stopwatch():
                self.int.optimize()
        except mosek.Error as error:
            if error.errno in (
                    mosek.rescode.err_con_q_not_psd,
                    mosek.rescode.err_con_q_not_nsd,
                    mosek.rescode.err_obj_q_not_psd,
                    mosek.rescode.err_obj_q_not_nsd,
                    mosek.rescode.err_toconic_constr_q_not_psd,
                    mosek.rescode.err_toconic_objective_not_psd):
                raise NonConvexError(error.msg)
            else:
                raise

        # Set the solution to be retrieved.
        if self.ext.is_continuous():
            if isLP:
                solType = mosek.soltype.bas
            else:
                solType = mosek.soltype.itr
        else:
            solType = mosek.soltype.itg

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        else:
            primals = {}

            values = [float("nan")]*self.int.getnumvar()
            self.int.getxx(solType, values)

            for picosVar in self.ext.variables.values():
                varName = picosVar.name
                varSize = picosVar.size

                mosekOffset = self._mosekVarOffset[picosVar]
                primal = values[mosekOffset:mosekOffset + picosVar.dim]

                if float("nan") in primal:
                    primals[varName] = None
                else:
                    primals[varName] = primal

        # Retrieve duals.
        if self.ext.options["noduals"] or not self.ext.is_continuous():
            duals = None
        else:
            duals = []

            for constraint in self.ext.constraints:
                length = len(constraint)
                dual   = [float("nan")]*length

                if isinstance(constraint, AffineConstraint):
                    offset = self._mosekLinConOffset[constraint]
                    self.int.getyslice(solType, offset, offset + length, dual)
                elif isinstance(constraint, QuadConstraint):
                    # TODO: Implement consistent QCQP dual retrieval for all
                    #       solvers that return such duals.
                    dual = None
                elif isinstance(constraint, SOCConstraint) \
                or isinstance(constraint, RSOCConstraint):
                    mosekVars = self._mosekCone[constraint][1]
                    for localConeIndex in range(length):
                        x = [float("nan")]
                        offset = mosekVars[localConeIndex]
                        self.int.getsnxslice(solType, offset, offset + 1, x)
                        dual[localConeIndex] = x[0]

                    if isinstance(constraint, SOCConstraint):
                        dual[0] = -dual[0]
                    elif isinstance(constraint, RSOCConstraint):
                        dual[0] = -dual[0] / math.sqrt(2.0)
                        dual[1] = -dual[1] / math.sqrt(2.0)
                elif isinstance(constraint, LMIConstraint):
                    n = constraint.size[0]
                    barVar, _ = self._mosekLMI[constraint]
                    lowerTriangularDual = [float("nan")]*(n*(n + 1) // 2)
                    self.int.getbarsj(solType, barVar, lowerTriangularDual)
                    for lti, (row, col) in enumerate(self._low_tri_indices(n)):
                        value = lowerTriangularDual[lti]
                        dual[n*row + col] = value
                        if row != col:
                            dual[n*col + row] = value
                else:
                    assert False, "Constraint type not supported."

                if dual is None:
                    pass
                elif float("nan") in dual:
                    dual = None
                else:
                    dual = cvxopt.matrix(dual, constraint.size)

                    if isinstance(constraint, AffineConstraint) \
                    or isinstance(constraint, LMIConstraint):
                        if constraint.is_decreasing():
                            dual = -dual

                duals.append(dual)

            if self.int.getobjsense() is mosek.objsense.minimize:
                duals = [-dual if dual is not None else None for dual in duals]

        # Retrieve objective value.
        objectiveValue = self.int.getprimalobj(solType)

        # Retrieve solution metadata.
        meta = {}
        meta["status"] = self._status_string(self.int.getsolsta(solType))

        return (primals, duals, objectiveValue, meta)
