#-------------------------------------------------------------------------------
# Copyright (C) 2017-2018 Maximilian Stahlberg
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
# This file implements the GLPK solver through the swiglpk interface.
#-------------------------------------------------------------------------------

import cvxopt

from ..expressions import *
from ..constraints import *

from .solver import *

class GLPKSolver(Solver):
    @staticmethod
    def _picos2glpk_variable_index(globalVarIndex):
        return globalVarIndex + 1

    @staticmethod
    def _glpk2picos_variable_index(globalVarIndex):
        return globalVarIndex - 1

    @classmethod
    def test_availability(cls):
        import swiglpk

    @classmethod
    def supports_integer(cls):
        return True

    @classmethod
    def supported_objectives(cls):
        yield AffinExp

    @classmethod
    def supported_constraints(cls):
        yield AffineConstraint

    def __init__(self, problem):
        super(GLPKSolver, self).__init__(
            problem, "GLPK", "GNU Linear Programming Kit")

    def __del__(self):
        try:
            import swiglpk as glpk
        except ImportError:
            # Happens when python is shutting down. In this case, no garbage
            # collection is necessary, anyway.
            return

        if self.int is not None:
            glpk.glp_delete_prob(self.int)

    def reset_problem(self):
        import swiglpk as glpk

        if self.int is not None:
            glpk.glp_delete_prob(self.int)
            self.int = None

    def _import_problem(self):
        import swiglpk as glpk

        if self.verbosity() >= 1:
            glpk.glp_term_out(glpk.GLP_ON)
        else:
            glpk.glp_term_out(glpk.GLP_OFF)

        # Create a problem instance.
        p = self.int = glpk.glp_create_prob();

        # Set the objective.
        if self.ext.objective[0] in ("find", "min"):
            glpk.glp_set_obj_dir(p, glpk.GLP_MIN)
        elif self.ext.objective[0] is "max":
            glpk.glp_set_obj_dir(p, glpk.GLP_MAX)
        else:
            raise NotImplementedError("Objective '{0}' not supported by GLPK."
                .format(self.ext.objective[0]))

        # Set objective function shift
        if self.ext.objective[1] is not None \
        and self.ext.objective[1].constant is not None:
            if not isinstance(self.ext.objective[1], AffinExp):
                raise NotImplementedError("Non-linear objective function not "
                    "supported by GLPK.")

            if self.ext.objective[1].constant.size != (1,1):
                raise NotImplementedError("Non-scalar objective function not "
                    "supported by GLPK.")

            glpk.glp_set_obj_coef(p, 0, self.ext.objective[1].constant[0])

        # Add variables.
        # Multideminsional variables are split into multiple scalar variables
        # represented as matrix columns within GLPK.
        for varName in self.ext.varNames:
            var = self.ext.variables[varName]

            # Add a column for every scalar variable.
            numCols = var.size[0] * var.size[1]
            glpk.glp_add_cols(p, numCols)

            for localIndex, picosIndex \
            in enumerate(range(var.startIndex, var.endIndex)):
                glpkIndex = self._picos2glpk_variable_index(picosIndex)

                # Assign a name to the scalar variable.
                scalarName = varName
                if numCols > 1:
                    x = localIndex // var.size[0]
                    y = localIndex % var.size[0]
                    scalarName += "_{:d}_{:d}".format(x + 1, y + 1)
                glpk.glp_set_col_name(p, glpkIndex, scalarName)

                # Assign bounds to the scalar variable.
                lower, upper = var.bnd.get(localIndex, (None, None))
                if lower is not None and upper is not None:
                    if lower == upper:
                        glpk.glp_set_col_bnds(
                            p, glpkIndex, glpk.GLP_FX, lower, upper)
                    else:
                        glpk.glp_set_col_bnds(
                            p, glpkIndex, glpk.GLP_DB, lower, upper)
                elif lower is not None and upper is None:
                    glpk.glp_set_col_bnds(p, glpkIndex, glpk.GLP_LO, lower, 0)
                elif lower is None and upper is not None:
                    glpk.glp_set_col_bnds(p, glpkIndex, glpk.GLP_UP, 0, upper)
                else:
                    glpk.glp_set_col_bnds(p, glpkIndex, glpk.GLP_FR, 0, 0)

                # Assign a type to the scalar variable.
                if var.vtype in ("continuous", "symmetric"):
                    glpk.glp_set_col_kind(p, glpkIndex, glpk.GLP_CV)
                elif var.vtype == "integer":
                    glpk.glp_set_col_kind(p, glpkIndex, glpk.GLP_IV)
                elif var.vtype == "binary":
                    glpk.glp_set_col_kind(p, glpkIndex, glpk.GLP_BV)
                else:
                    raise NotImplementedError("Variable type '{0}' not "
                        "supported by GLPK.".format(var.vtype()))

                # Set objective function coefficient of the scalar variable.
                if self.ext.objective[1] is not None \
                and var in self.ext.objective[1].factors:
                    glpk.glp_set_obj_coef(p, glpkIndex,
                        self.ext.objective[1].factors[var][localIndex])

        # Add constraints.
        # Multideminsional constraints are split into multiple scalar
        # constraints represented as matrix rows within GLPK.
        rowOffset = 1
        for constraintNum, constraint in enumerate(self.ext.constraints):
            if not isinstance(constraint, AffineConstraint):
                raise NotImplementedError(
                    "Non-linear constraints not supported by GLPK.")

            # Add a row for every scalar constraint.
            # Internally, GLPK uses an auxiliary variable for every such row,
            # bounded by the right hand side of the scalar constraint in a
            # canonical form.
            numRows = len(constraint)
            glpk.glp_add_rows(p, numRows)

            self._debug("Handling PICOS Constraint: " + str(constraint))

            # Split multidimensional constraints into multiple scalar ones.
            for localConIndex, (glpkVarIndices, coefficients, rhs) in \
                    enumerate(constraint.sparse_Ab_rows(
                    None, indexFunction = lambda picosVar, i:
                    self._picos2glpk_variable_index(picosVar.startIndex + i))):
                # Determine GLPK's row index of the scalar constraint.
                glpkConIndex = rowOffset + localConIndex
                numColumns   = len(glpkVarIndices)

                # Name the auxiliary variable associated with the current row.
                if constraint.name:
                    name = constraint.name
                else:
                    name = "rhs_{:d}".format(constraintNum)
                if numRows > 1:
                    x = localConIndex // constraint.size[0]
                    y = localConIndex % constraint.size[0]
                    name += "_{:d}_{:d}".format(x + 1, y + 1)
                glpk.glp_set_row_name(p, glpkConIndex, name)

                # Assign bounds to the auxiliary variable.
                if constraint.is_equality():
                    glpk.glp_set_row_bnds(p, glpkConIndex, glpk.GLP_FX, rhs,rhs)
                elif constraint.is_increasing():
                    glpk.glp_set_row_bnds(p, glpkConIndex, glpk.GLP_UP, 0, rhs)
                elif constraint.is_decreasing():
                    glpk.glp_set_row_bnds(p, glpkConIndex, glpk.GLP_LO, rhs, 0)
                else:
                    assert False, "Unexpected constraint relation."

                # Set coefficients for current row.
                # Note that GLPK requires a glpk.intArray containing column
                # indices and a glpk.doubleArray of same size containing the
                # coefficients for the listed column index. The first element
                # of both arrays (with index 0) is skipped by GLPK.
                glpkVarIndicesArray = glpk.intArray(numColumns + 1)
                for i in range(numColumns):
                    glpkVarIndicesArray[i + 1] = glpkVarIndices[i]

                coefficientsArray = glpk.doubleArray(numColumns + 1)
                for i in range(numColumns):
                    coefficientsArray[i + 1] = coefficients[i]

                glpk.glp_set_mat_row(p, glpkConIndex, numColumns,
                    glpkVarIndicesArray, coefficientsArray)

            rowOffset += numRows

    def _update_problem(self):
        import swiglpk as glpk

        # TODO: Check to which extend GLPK supports updates to a problem.
        raise NotImplementedError()

    def _solve(self):
        import swiglpk as glpk

        # An alias to the internal problem instance.
        p = self.int

        continuous = self.ext.is_continuous()

        # Select LP solver (Simplex or Interior Point Method).
        if continuous:
            if self.ext.options["lp_root_method"] == "interior":
                interior = True
            else:
                # Default to Simplex.
                interior = False
            simplex = not interior
        else:
            simplex = interior = False

        # Select appropriate options container.
        if simplex:
            options = glpk.glp_smcp()
            glpk.glp_init_smcp(options)
        elif interior:
            options = glpk.glp_iptcp()
            glpk.glp_init_iptcp(options)
        else:
            options = glpk.glp_iocp()
            glpk.glp_init_iocp(options)

        # Handle "verbose" option.
        verbosity = self.verbosity()
        if verbosity < 0:
            options.msg_lev = glpk.GLP_MSG_OFF
        elif verbosity == 0:
            options.msg_lev = glpk.GLP_MSG_ERR
        elif verbosity == 1:
            options.msg_lev = glpk.GLP_MSG_ON
        elif verbosity >= 2:
            options.msg_lev = glpk.GLP_MSG_ALL

        # Handle "tol" option.
        # Note that GLPK knows three different tolerances for Simplex but none
        # for the Interior Point Method, while PICOS states that "tol" is meant
        # only for the IPM.
        # XXX: The option is unsupported but does not default to None, so we
        #      cannot warn the user.
        pass

        # Handle "maxit" option.
        if not simplex:
            self._handle_unsupported_option("maxit",
                "GLPK supports the 'maxit' option only with Simplex.")
        elif self.ext.options["maxit"] is not None:
                options.it_lim = int(self.ext.options["maxit"])

        # Handle "lp_root_method" option.
        # Note that the PICOS option is explicitly also meant for the MIP
        # preprocessing step but GLPK does not support it in that scenario.
        if not continuous:
            self._handle_unsupported_option("lp_root_method",
                "GLPK supports the 'lp_root_method' option only for LPs.")
        elif self.ext.options["lp_root_method"] is not None:
            if self.ext.options["lp_root_method"] == "interior":
                # Handled above.
                pass
            elif self.ext.options["lp_root_method"] == "psimplex":
                assert simplex
                options.meth = glpk.GLP_PRIMAL
            elif self.ext.options["lp_root_method"] == "dsimplex":
                assert simplex
                options.meth = glpk.GLP_DUAL
            else:
                self._handle_bad_option_value("lp_root_method")

        # Handle "timelimit" option.
        if interior:
            self._handle_unsupported_option("timelimit",
                "GLPK does not support the 'timelimit' option with the "
                "Interior Point Method.")
        elif self.ext.options["timelimit"] is not None:
            options.tm_lim = 1000 * int(self.ext.options["timelimit"])

        # Handle "gaplim" option.
        # Note that the option is silently ignored if passed alongside an LP;
        # while the solver does not allow us to pass the option in that case, it
        # is still technically a valid option as every LP is also a MIP.
        # TODO: Find out if "mip_gap" is really equivalent to "gaplim".
        if self.ext.options["gaplim"] is not None:
            if not continuous:
                options.mip_gap = float(self.ext.options["gaplim"])

        # Handle unsupported options.
        self._handle_unsupported_options(
            "lp_node_method", "treememory", "nbsol", "hotstart")

        # TODO: Add GLPK-sepcific options. Candidates are:
        #       For both Simplex and MIPs:
        #           tol_*, out_*
        #       For Simplex:
        #           pricing, r_test, obj_*
        #       For the Interior Point Method:
        #           ord_alg
        #       For MIPs:
        #           *_tech, *_heur, ps_tm_lim, *_cuts, cb_size, binarize

        # Attempt to solve the problem.
        with self._header():
            with self._stopwatch():
                if simplex:
                    # TODO: Support glp_exact.
                    error = glpk.glp_simplex(p, options)
                elif interior:
                    error = glpk.glp_interior(p, options)
                else:
                    options.presolve = glpk.GLP_ON
                    error = glpk.glp_intopt(p, options)

            # Conert error codes to text output.
            # Note that by printing it above the footer, this output is made to
            # look like it's coming from GLPK, which is technically wrong but
            # semantically correct.
            if error == glpk.GLP_EBADB:
                self._warn("Unable to start the search, because the initial "
                    "basis specified in the problem object is invalid.")
            elif error == glpk.GLP_ESING:
                self._warn("Unable to start the search, because the basis "
                    "matrix corresponding to the initial basis is singular "
                    "within the working precision.")
            elif error == glpk.GLP_ECOND:
                self._warn("Unable to start the search, because the basis "
                    "matrix corresponding to the initial basis is "
                    "ill-conditioned.")
            elif error == glpk.GLP_EBOUND:
                self._warn("Unable to start the search, because some double-"
                    "bounded variables have incorrect bounds.")
            elif error == glpk.GLP_EFAIL:
                self._warn("The search was prematurely terminated due to a "
                    "solver failure.")
            elif error == glpk.GLP_EOBJLL:
                self._warn("The search was prematurely terminated, because the "
                    "objective function being maximized has reached its lower "
                    "limit and continues decreasing.")
            elif error == glpk.GLP_EOBJUL:
                self._warn("The search was prematurely terminated, because the "
                    "objective function being minimized has reached its upper "
                    "limit and continues increasing.")
            elif error == glpk.GLP_EITLIM:
                self._warn("The search was prematurely terminated, because the "
                    "simplex iteration limit has been exceeded.")
            elif error == glpk.GLP_ETMLIM:
                self._warn("The search was prematurely terminated, because the "
                    "time limit has been exceeded.")
            elif error == glpk.GLP_ENOPFS:
                self._verbose("The LP has no primal feasible solution.")
            elif error == glpk.GLP_ENODFS:
                self._verbose("The LP has no dual feasible solution.")
            elif error != 0:
                self._warn("GLPK error {:d}.".format(error))

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        else:
            primals = {}

            for variable in self.ext.variables.values():
                value = []

                for localIndex, picosIndex \
                in enumerate(range(variable.startIndex, variable.endIndex)):
                    glpkIndex = self._picos2glpk_variable_index(picosIndex)

                    if simplex:
                        localValue = glpk.glp_get_col_prim(p, glpkIndex);
                    elif interior:
                        localValue = glpk.glp_ipt_col_prim(p, glpkIndex);
                    else:
                        localValue = glpk.glp_mip_col_val(p, glpkIndex);

                    value.append(localValue)

                primals[variable.name] = value

        # Retrieve duals.
        # XXX: Returns the duals as a flat cvx.matrix to be consistent with
        #      other solvers. This feels incorrect when the constraint was given
        #      as a proper two dimensional matrix.
        if self.ext.options["noduals"] or not continuous:
            duals = None
        else:
            duals = []
            rowOffset = 1
            for constraintNum, constraint in enumerate(self.ext.constraints):
                assert isinstance(constraint, AffineConstraint)
                numRows = len(constraint)
                values = []
                for localConIndex in range(numRows):
                    glpkConIndex = rowOffset + localConIndex
                    if simplex:
                        localValue = glpk.glp_get_row_dual(p, glpkConIndex);
                    elif interior:
                        localValue = glpk.glp_ipt_row_dual(p, glpkConIndex);
                    else:
                        assert False
                    values.append(localValue)
                if constraint.is_decreasing():
                    duals.append(-cvxopt.matrix(values))
                else:
                    duals.append(cvxopt.matrix(values))
                rowOffset += numRows
            if glpk.glp_get_obj_dir(p) == glpk.GLP_MIN:
                duals = [-d for d in duals]

        # Retrieve objective value.
        if simplex:
            objectiveValue = glpk.glp_get_obj_val(p)
        elif interior:
            objectiveValue = glpk.glp_ipt_obj_val(p)
        else:
            objectiveValue = glpk.glp_mip_obj_val(p)

        # Retrieve solution metadata.
        meta = {}

        if simplex:
            # Set common entry "status".
            status = glpk.glp_get_status(p)
            if status is glpk.GLP_OPT:
                meta["status"] = "optimal"
            elif status is glpk.GLP_FEAS:
                meta["status"] = "feasible"
            elif status in (glpk.GLP_INFEAS, glpk.GLP_NOFEAS):
                meta["status"] = "infeasible"
            elif status is glpk.GLP_UNBND:
                meta["status"] = "unbounded"
            elif status is glpk.GLP_UNDEF:
                meta["status"] = "undefined"
            else:
                meta["status"] = "unknown"

            # Set GLPK-specific entry "primal_status".
            primalStatus = glpk.glp_get_prim_stat(p)
            if primalStatus is glpk.GLP_FEAS:
                meta["primal_status"] = "feasible"
            elif primalStatus in (glpk.GLP_INFEAS, glpk.GLP_NOFEAS):
                meta["primal_status"] = "infeasible"
            elif primalStatus is glpk.GLP_UNDEF:
                meta["primal_status"] = "undefined"
            else:
                meta["primal_status"] = "unknown"

            # Set GLPK-specific entry "dual_status".
            dualStatus = glpk.glp_get_dual_stat(p)
            if dualStatus is glpk.GLP_FEAS:
                meta["dual_status"] = "feasible"
            elif dualStatus in (glpk.GLP_INFEAS, glpk.GLP_NOFEAS):
                meta["dual_status"] = "infeasible"
            elif dualStatus is glpk.GLP_UNDEF:
                meta["dual_status"] = "undefined"
            else:
                meta["dual_status"] = "unknown"
        elif interior:
            # Set common entry "status".
            status = glpk.glp_ipt_status(p)
            if status is glpk.GLP_OPT:
                meta["status"] = "optimal"
            elif status in (glpk.GLP_INFEAS, glpk.GLP_NOFEAS):
                meta["status"] = "infeasible"
            elif status is glpk.GLP_UNDEF:
                meta["status"] = "undefined"
            else:
                meta["status"] = "unknown"
        else:
            # Set common entry "status".
            status = glpk.glp_mip_status(p)
            if status is glpk.GLP_OPT:
                meta["status"] = "optimal"
            elif status is glpk.GLP_FEAS:
                meta["status"] = "feasible"
            elif status is glpk.GLP_NOFEAS:
                meta["status"] = "infeasible"
            elif status is glpk.GLP_UNDEF:
                meta["status"] = "undefined"
            else:
                meta["status"] = "unknown"

        return (primals, duals, objectiveValue, meta)
