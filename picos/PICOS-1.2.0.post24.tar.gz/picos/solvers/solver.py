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
# This file contains the abstract base class for all solvers.
# It is imported exactly by the solver implementations.
#-------------------------------------------------------------------------------

from __future__ import print_function
from contextlib import contextmanager
import os
import sys
import time

# Import abstract base class support for both Pythons.
from abc import ABCMeta, abstractmethod
ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

# Enable solvers that support only conic constraints to solve QCQPs.
from ..expressions import QuadExp
from ..constraints import QuadConstraint, SOCConstraint, RSOCConstraint

SUPPORT_LEVEL_NATIVE       = 4
"""The problem and options are supported fully and without transformation."""

SUPPORT_LEVEL_SECONDARY    = 3
"""The problem and options are supported fully after a necessary transformation
of the problem."""

SUPPORT_LEVEL_EXPERIMENTAL = 2
"""The solver will accept the problem and options but is not designed with this
kind of task in mind, and may handle it poorly as a result."""

SUPPORT_LEVEL_LIMITED      = 1
"""The solver does not fully support the problem with the given set of options,
for instance it might not return a dual value where one is expected."""

SUPPORT_LEVEL_NONE         = 0
"""The problem is not supported, regardless of options provided."""

def supportLevelString(level):
    return ["no", "limited", "experimental", "secondary", "native"][level]

class SolverError(Exception):
    """
    Base class for solver-specific exceptions.
    """
    pass

class ProblemUpdateError(SolverError):
    """
    An exception raised by implementations of `_update_problem` to signal to
    the method `_load_problem` that the problem needs to be re-imported.
    """
    pass

class InappropriateSolverError(SolverError):
    """
    An exception raised by implementations of `_solve` to signal to the user
    that the solver (or its requested sub-solver) does not support the given
    problem type.
    """
    pass

class OptionError(SolverError):
    """
    Base class for solver option related errors.
    """
    pass

class UnsupportedOptionError(OptionError):
    """
    An exception raised by implementations of `_solve` to signal to the user
    that an option they specified is not supported by the solver or the
    requested sub-solver, or in conjunction with the given problem type or
    with another option. If the option is valid but not supported by PICOS,
    then NotImplementedError should be raised instead. The exception is only
    raised if the `strictOptions` option is set, otherwise a warning is printed.
    """
    pass

class ConflictingOptionsError(OptionError):
    """
    An exception raised by implementations of `_solve` to signal to the user
    that two options they specified cannot be used in conjunction.
    """
    # TODO: Handle conflicting options globally, instead of within solver
    #       implementations. (Should not inherit from SolverError then.)
    pass

class DependentOptionError(OptionError):
    """
    An exception raised by implementations of `_solve` to signal to the user
    that an option they specified needs another option to also be set.
    """
    # TODO: Handle dependent options globally, instead of within solver
    #       implementations. (Should not inherit from SolverError then.)
    pass

class OptionValueError(OptionError, ValueError):
    """
    An exception raised by implementations of `_solve` to signal to the user
    that they have set an option to an invalid value.
    """
    # TODO: Handle option value errors globally, instead of within solver
    #       implementations. (Should not inherit from SolverError then.)
    pass

# TODO: Add a write function that interfaces the solver's export to file.
class Solver(ABC):
    """
    Abstract base class for a wrapper around the internal problem representation
    of solvers.
    """

    #---------------------------------------------------------------------------
    # The following section contains the abstract methods, and __init__.
    # They need to be overridden by any solver implementation and, most of the
    # time, overwriting these methods is sufficient to implement a solver.
    #---------------------------------------------------------------------------

    @classmethod
    @abstractmethod
    def test_availability(cls):
        """
        Checks whether the solver is properly installed on the system, and
        raises an appropriate exception (usually `ModuleNotFoundError` or
        `ImportError`) if not. Does not return anything.
        """
        pass

    @classmethod
    @abstractmethod
    def supports_integer(cls):
        """
        :returns: Whether (mixed) integer problems are supported.
        """
        pass

    @classmethod
    @abstractmethod
    def supported_objectives(cls):
        """
        :returns: All objective function types that the solver can import.
        """
        pass

    @classmethod
    @abstractmethod
    def supported_constraints(cls):
        """
        :returns: All constraint classes that the solver can import.
        """
        pass

    def __init__(self, problem, displayName, longDisplayName):
        """
        Creates an instance of a wrapper around a solver's internal problem
        representation of the given PICOS problem formulation.

        An exception is raised when the solver is not available on the user's
        platform. No exception is raised when the problem type is not supported
        as the problem is first imported when the user calls `solve`.

        Solver implementations are supposed to also implement `__init__`, but
        with `problem` as its only positional argument, and using `super` to
        provide fixed values for this method's additional parameters.

        :param problem: A PICOS optimization problem.
        :type problem: :class:`Problem <picos.Problem>`
        :param displayName: The short display name of the solver.
        :type displayName: str
        :param longDisplayName: The long display name of the solver.
        :type longDisplayName: str
        """
        # Make sure the solver is available.
        self.test_availability()

        # The external (PICOS) problem represenation.
        self.ext = problem

        # Names for console output, given by solver implementation.
        self.name = displayName
        self.longname = longDisplayName

        # The solver's internal problem representation, which the advanced user
        # may access at their own risk.
        self.int = None

        # The last optimization objective that was imported.
        self._knownObjective = None

        # The PICOS variables that are currently imported.
        self._knownVariables = set()

        # The PICOS constraints that are currently imported.
        self._knownConstraints = set()

    @abstractmethod
    def reset_problem(self):
        """
        Resets the solver's internal problem representation and related data.

        Method implementations are supposed to

        - set `int` to None (after performing any garbage collection), and
        - reset all additional problem metadata to the state it had after
          `__init__`, in particular the data stored for `_update_problem`.

        Solver implementations should not call `reset_problem` directly, except
        from within `__init__` if this is convenient.

        The user may call this method at any time if they wish to solve the
        problem from scratch.
        """
        pass

    @abstractmethod
    def _import_problem(self):
        """
        Converts PICOS' problem formulation to the solver's internal problem
        representation.

        Method implementations can assume to be run directly after either
        `__init__` or `reset_problem`, and before `solve`. The method is
        supposed to transform only the problem formulation itself; solver
        configuration options are passed inside `solve` instead.

        Solver implementations should not call `_import_problem` directly, but
        instead call `_load_problem` (from within `solve`).
        """
        pass

    @abstractmethod
    def _update_problem(self):
        """
        Updates the solver's internal problem representation, if possible.

        Method implementations should make use of `_objective_has_changed`,
        `_new_variables`, `_removed_variables`, `_new_constraints` and
        `_removed_constraints`. Note that you can use each of the latter four
        generators only once each update as they will update the sets of known
        variables and constraints, respectively.

        Method implementations may raise
        - `NotImplementedError`, if updates to the internal problem instance of
          the solver are not supported (not at all or just not by PICOS), or
        - `ProblemUpdateError`, if an update to the solver's internal problem
           instance is not possible for the particular set of changes in the
           problem formulation.
        In both cases, the user will receive a warning and the problem will be
        re-imported instead of updated. In the case of `ProblemUpdateError`, a
        reason should be given and will be included in the warning.

        Solver implementations should not call `_update_problem` directly, but
        instead call `_load_problem` (from within `solve`).
        """
        pass

    @abstractmethod
    def _solve(self):
        """
        Solves the problem and returns the solution.

        Method implementations can assume to be run after `_load_problem`, which
        attempts to run `_update_problem` and falls back to `_import_problem`.
        The method is supposed to pass options to the solver, run it within the
        `_stopwatch` context, and retrieve the results. See below for the format
        that results need to be returned in.

        An InappropriateSolverError should be raised if the solver (or its
        requested sub-solver) does not support the given problem type.

        :returns: A quadruple `(primals, duals, objectiveValue, meta)`.
            - `primals` is a :class:`dict` mapping variable names to their value
              in the primal solution, with a type matching that of the variable.
              If no primal solution was produced, may be None or a dictionary
              where all values are None.
            - `duals` is a :class:`list` whose members are the dual solution
              values of the dual variables corresponding to the constraints that
              are stored at the same index in :attr:`Problem.constraints`. If no
              dual solution was produced, may be None or a list full of None.
            - `objectiveValue` is the optimal objective function value, or the
              string "toEval", or None.
            - `meta` is a :class:`dict` containing solution metadata, which may
              be specific to the solver. Solver implementations are required to:
              - Map "status" to a lowercase string.
              - Not map "time", as it is set by the solver base class based upon
                the time spent in the `_stopwatch` context.
        """
        pass

    #---------------------------------------------------------------------------
    # The following section contains default methods that most solvers will want
    # to inherit, while sometimes it becomes necessary to make modifications.
    #---------------------------------------------------------------------------

    @classmethod
    def support_level(cls, problem):
        """
        Solver implementations may overwrite this method if necessary, for
        instance to indicate experimental or limited support, or to disallow
        certain combinations of constraints that are supported individually,
        or to allow constraints that are otherwise not supported if they
        originate from a metaconstraint that is supported directly.

        Support levels are used for determining a solver's priority when PICOS
        selects a solver, and for skipping tests that are known/likely to fail.

        :returns: A number indicating how well the problem is supported, which
            must be one of the `SUPPORT_LEVEL_*` constants.
        """
        if not problem.is_continuous() and not cls.supports_integer():
            return SUPPORT_LEVEL_NONE

        quadsAsSOCP = cls.needs_quad_to_socp_cast()
        needsCast   = False

        # Check if objective type is supported.
        objectiveFunction = problem.objective[1]
        objectiveSupported = objectiveFunction is None or any(
            [True for supported in cls.supported_objectives()
            if isinstance(objectiveFunction, supported)])

        if not objectiveSupported:
            if isinstance(objectiveFunction, QuadExp) and quadsAsSOCP:
                needsCast = True
            else:
                return SUPPORT_LEVEL_NONE

        # Check if all constraints are supported.
        for constraint in problem.constraints:
            if constraint.__class__ in cls.supported_constraints():
                pass
            elif constraint.__class__ is QuadConstraint and quadsAsSOCP:
                needsCast = True
            else:
                return SUPPORT_LEVEL_NONE

        if needsCast:
            return SUPPORT_LEVEL_SECONDARY
        else:
            return SUPPORT_LEVEL_NATIVE

    @classmethod
    def supports_quad_socp_mix(cls):
        """
        :returns: Whether quadratic constraints and (rotated) second order cone
            constraints may appear in the same problem.
        """
        quad = QuadConstraint in cls.supported_constraints()
        soc  = SOCConstraint  in cls.supported_constraints()
        rsoc = RSOCConstraint in cls.supported_constraints()

        return quad and (soc or rsoc)

    #---------------------------------------------------------------------------
    # The following section contains methods that should not be overriden by
    # solver implementations, so that their behaviour is consistent.
    #---------------------------------------------------------------------------

    @classmethod
    def available(cls, verbose = False):
        """
        :returns: Whether the solver is properly installed on the system.
        """
        try:
            cls.test_availability()
            return True
        except Exception as e:
            if verbose:
                print(e)
            return False

    @classmethod
    def needs_quad_to_socp_cast(cls):
        """
        :returns: Whether second order cone constraints are supported but
            quadratic problems are not.
        """
        supportsQuadObj = QuadExp in cls.supported_objectives()
        supportsQuadCon = QuadConstraint in cls.supported_constraints()
        supportsSOCC    = SOCConstraint in cls.supported_constraints()

        return (not supportsQuadObj or not supportsQuadCon) and supportsSOCC

    def __str__(self):
        return "# wrapper around a " + self.name + " problem instance #"

    def external_problem(self):
        """
        :returns: The external (PICOS) problem represenation.
        """
        return self.ext

    def internal_problem(self):
        """
        :returns: The solver's internal problem represenation.
        """
        return self.int

    def problem_support_level(self):
        """
        :returns: How well the problem in its current state is supperted by the
                  solver, as a nonnegative integer.
        """
        return self.support_level(self.ext)

    def verbosity(self):
        """
        :returns: The problem's current verbosity level.
        """
        return self.ext.verbosity()

    def _warn(self, message = None):
        """
        Prints a warning message, if the verbosity level allows for it.

        :returns: Whether warning messages are printed.
        """
        return self.ext._warn(message)

    def _verbose(self, message = None):
        """
        Prints an informative message, if the verbosity level allows for it.

        :returns: Whether informative messages are printed.
        """
        return self.ext._verbose(message)

    def _debug(self, message = None):
        """
        Prints a debug message, if the verbosity level allows for it.

        :returns: Whether debug messages are printed.
        """
        return self.ext._debug(message)

    def _handle_unsupported_option(self, option, customMessage = None):
        """
        Informs the user about an unsupported option, in a manner depending on
        the `strict_options` option.
        """
        assert option in self.ext.options, \
            "The option '{}' does not exist.".format(option)

        if self.ext.options[option] in (None, False):
            return

        if customMessage:
            message = customMessage
        else:
            message = "{} does not support the '{}' option." \
                .format(self.name, option)

        if self.ext.options["strict_options"]:
            raise UnsupportedOptionError(message)
        else:
            self._warn(message)

    def _handle_unsupported_options(self, *options):
        """
        A helper to handle a number of unsupported options at once.
        """
        for option in options:
            self._handle_unsupported_option(option)

    def _handle_bad_option_value(self, option, reason = None):
        """
        Informs the user that they set an option to an invalid value.
        """
        assert option in self.ext.options, \
            "The option '{}' does not exist.".format(option)
        raise OptionValueError("Invalid value '{}' for option '{}'{}"
            .format(self.ext.options[option], option,
            ": {}".format(reason) if reason else "."))

    def _load_problem(self):
        """
        (Re-)imports or updates the internal problem representation for solving.
        """
        # Make sure the problem type is supported.
        supportLevel = self.problem_support_level()

        assert supportLevel is not SUPPORT_LEVEL_SECONDARY, \
            "The problem should have been converted, but it was not."

        if supportLevel is SUPPORT_LEVEL_NONE:
            raise InappropriateSolverError(
                "Solver {} does not support problem of type {}."
                .format(self.name, self.ext.type))
        elif supportLevel in (SUPPORT_LEVEL_LIMITED,SUPPORT_LEVEL_EXPERIMENTAL):
            self._warn("Solver {} has only {} support for the given problem "
                "and options!".format(self.name,
                supportLevelString(supportLevel).upper(), self.ext.type))

        # Import or update the problem.
        if self.int is None:
            self._verbose("Building a {} problem instance.".format(self.name))
            self._import_problem()
        else:
            try:
                self._verbose("Updating the {} problem instance."
                    .format(self.name))
                self._update_problem()
            except (NotImplementedError, ProblemUpdateError) as error:
                if type(error) is NotImplementedError:
                    reason = "Not supported with {}.".format(self.name)
                else:
                    reason = str(error)
                    if reason == "":
                        reason = "Unknown reason."
                self._verbose("Update failed: {}".format(reason))
                self._verbose("Rebuilding the {} problem instance."
                    .format(self.name))
                self.reset_problem()
                self._import_problem()

        # Remember which objective and what constraints were imported.
        self._knownObjective = self.ext.objective
        self._knownVariables = set(self.ext.variables.values())
        self._knownConstraints = set(self.ext.constraints)

    def _objective_has_changed(self):
        """
        :returns: Whether the optimization objective has changed since the last
        import or update.
        """
        assert self._knownObjective is not None, \
            "_objective_has_changed may only be used inside _update_problem."

        directionChanged = self._knownObjective[0] != self.ext.objective[0]
        functionChanged = self._knownObjective[1] is not self.ext.objective[1]
        objectiveChanged = directionChanged or functionChanged

        if objectiveChanged:
            self._knownObjective = self.ext.objective

        return objectiveChanged

    def _new_variables(self):
        """
        Yields PICOS variables that were added to the external problem
        representation since the last import or update.

        Note that variables received from this method will also be added to the
        set of known variables, so you can only iterate once within each update.
        """
        for variable in self.ext.variables.values():
            if variable not in self._knownVariables:
                self._knownVariables.add(variable)
                yield variable

    def _removed_variables(self):
        """
        Yields PICOS variables that were removed from the external problem
        representation since the last import or update.

        Note that variables received from this method will also be removed from
        the set of known variables, so you can only iterate once within each
        update.
        """
        newVariables = set(self.ext.variables.values())
        for variable in self._knownVariables:
            if variable not in newVariables:
                yield variable
        self._knownVariables.intersection_update(newVariables)

    def _new_constraints(self):
        """
        Yields PICOS constraints that were added to the external problem
        representation since the last import or update.

        Note that constraints received from this method will also be added to
        the set of known constraints, so you can only iterate once within each
        update.
        """
        for constraint in self.ext.constraints:
            if constraint not in self._knownConstraints:
                self._knownConstraints.add(constraint)
                yield constraint

    def _removed_constraints(self):
        """
        Yields PICOS constraints that were removed from the external problem
        representation since the last import or update.

        Note that constraints received from this method will also be removed
        from the set of known constraints, so you can only iterate once within
        each update.
        """
        newConstraints = set(self.ext.constraints)
        for constraint in self._knownConstraints:
            if constraint not in newConstraints:
                yield constraint
        self._knownConstraints.intersection_update(newConstraints)

    @contextmanager
    def _stopwatch(self):
        """
        A contextmanager that times the time spent within the context and stores
        it in the `timer` member for later use.

        Solver implementations should use this context around the call to the
        solution routine to measure its search time.
        """
        startTime = time.time()
        yield
        endTime = time.time()
        self.timer = endTime - startTime

    def _reset_stopwatch(self):
        """
        Resets the `timer` used by the `_stopwatch` context manager.
        """
        self.timer = None

    def solve(self):
        """
        Solves the problem and returns the solution.

        :returns: A quadruple (primals, duals, objectiveValue, meta).
        """
        self._print_header(forPICOS = True)

        self._load_problem()
        self._reset_stopwatch()

        self._verbose("Solving the problem via {}.".format(self.name))
        primals, duals, objectiveValue, meta = self._solve()

        # Enforce proper format of the returned solution.
        assert primals is None or type(primals) is dict
        assert duals is None or type(duals) is list
        assert type(objectiveValue) in (int, float, list) \
            or objectiveValue is None \
            or objectiveValue == "toEval"
        assert type(meta) is dict
        assert "status" in meta and type(meta["status"]) is str
        assert "time" not in meta, \
            "Field 'time' of solution metadata is set in Solver base class."
        assert self.timer is not None, \
            "Solvers must measure search time via _stopwatch."

        meta["time"] = self.timer

        # Output solution status.
        self._verbose("Solution is {} after {:.1e}s."
            .format(meta["status"], meta["time"]))

        # Warn about incomplete primals.
        if primals is not None and None in primals.values():
            if any([True for primal in primals.values() if primal is not None]):
                self._warn("The primal solution is incomplete.")
            else:
                primals = None

        if primals is None:
            self._verbose("No primal solution obtained.")

        # Warn about incomplete duals.
        if duals is not None and None in duals:
            if any([True for dual in duals if dual is not None]):
                self._warn("The dual solution is incomplete.")
            else:
                duals = None

        if duals is None:
            self._verbose("No dual solution obtained.")

        self._print_footer(forPICOS = True)

        return primals, duals, objectiveValue, meta

    DEFAULT_HEADER_WIDTH = 35

    def _print_header(
        self, subsolver=None, width=DEFAULT_HEADER_WIDTH, forPICOS=False):
        """
        Prints a text header with the long display name of the solver, if the
        verbosity level permits it.

        Solver implementations should call this from within `solve` before
        starting the search if the solver does not print a header of its own.

        :param bool forPICOS: Whether to print the PICOS super header instead.
        """
        if self._verbose():
            from ..__init__ import __version__ as picosVer

            l = "=" * width if forPICOS else "-" * width
            w = "{:d}".format(width)

            if subsolver:
                s = ("{:^"+w+"}\n").format("via {}".format(subsolver))
            else:
                s = ""

            print(("{0}\n{2:^"+w+"}\n{1}{0}").format(l, s,
                "PICOS {}".format(picosVer) if forPICOS else self.longname))
            sys.stdout.flush()

    def _print_footer(self, width=DEFAULT_HEADER_WIDTH, forPICOS=False):
        """
        Prints a text footer matching the header printed by `_print_header`, if
        the verbosity level permits it.

        Solver implementations should call this from within `solve` after the
        the search if the solver does not print a footer of its own.

        :param bool forPICOS: Whether to print the PICOS super footer instead.
        """
        if self._verbose():
            from math import floor, ceil

            lineChar = "=" if forPICOS else "-"
            middle   = "[ {} ]".format("PICOS" if forPICOS else self.name)

            if width < len(middle) + 2:
                footer = lineChar * width
            else:
                s = (width - len(middle))
                l = int(floor(s / 2.0))
                r = int(ceil(s / 2.0))
                footer = lineChar * l + middle + lineChar * r

            print(footer)
            sys.stdout.flush()

    @contextmanager
    def _header(self, subsolver=None, width=DEFAULT_HEADER_WIDTH):
        """
        A contextmanager that prints both a header and a footer.

        Solver implementations can use this instead of `_print_header` and
        `_print_footer`.
        """
        self._print_header(subsolver, width)
        yield
        self._print_footer(width)

    @contextmanager
    def _enforced_verbosity(self, noStdOutAt = 0, noStdErrAt = -1):
        """
        A contextmanager that forces the context to adhere to the user-specified
        verbosity level.

        :param int noStdOutAt: Don't print to stdout at or below this verbosity.
        :param int noStdErrAt: Don't print to stderr at or below this verbosity.
        """
        verbosity = self.ext.verbosity()

        if verbosity <= max(noStdOutAt, noStdErrAt):
            devNull = open(os.devnull, "w")

        if verbosity <= noStdOutAt:
            oldOut = sys.stdout
            sys.stdout = devNull

        if verbosity <= noStdErrAt:
            oldErr = sys.sdterr
            sys.stderr = devNull

        yield

        if verbosity <= noStdOutAt:
            sys.stdout = oldOut

        if verbosity <= noStdErrAt:
            sys.stderr = oldErr
