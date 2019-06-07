"""
Regression test to verify the proper installation of *hynet* at the user.
"""

from hynet.types_ import SolverType, SolverStatus
from hynet.solver import AVAILABLE_SOLVERS
from hynet.opf.calc import calc_opf
from hynet.test.regression import OPFVerificationData, verify_opf_result
from hynet.test.system import TEST_SYSTEM, REFERENCE_SOLUTION


def test_installation(verbose=True):  # pylint: disable=too-many-branches
    """
    Verify the OPF solution of a test system for all available solvers.

    Parameters
    ----------
    verbose : bool, optional
        If True (default), the test is documented to the standard output.

    Returns
    -------
    success : bool
        True if the test was passed, False otherwise.
    """
    if not AVAILABLE_SOLVERS:
        if verbose:
            print("ERROR: No supported solvers were found.")
        return False

    try:
        solvers = [solver_class() for solver_class in AVAILABLE_SOLVERS]
    except Exception as exception:  # pylint: disable=broad-except
        if verbose:
            print("ERROR: " + str(exception))
        return False

    success = True
    width = max([len(str(solver)) for solver in solvers]) + 3
    for solver in solvers:
        solver_name = str(solver)
        message = solver_name + ' ' + '.'*(width - len(solver_name)) + ' '

        try:
            result = calc_opf(TEST_SYSTEM, solver=solver)
        except Exception as exception:  # pylint: disable=broad-except
            if verbose:
                print(message + "ERROR: " + str(exception))
            success = False
            continue

        if result.solver_status != SolverStatus.SOLVED:
            message += ("ERROR: Solver failed with status '" +
                        result.solver_status.name + "'.")
            success = False
        elif result.empty:
            message += "ERROR: The solver did not return any result data."
            success = False
        else:
            tolerance = 5e-4 if solver.type == SolverType.QCQP else 5e-3
            try:
                verify_opf_result(OPFVerificationData.create(result),
                                  REFERENCE_SOLUTION,
                                  tolerance)
            except ValueError as exception:
                message += "ERROR: " + str(exception)
                success = False
            else:
                message += "OK"
        if verbose:
            print(message)

    return success
