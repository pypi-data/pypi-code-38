"""
Solver interface for a *hynet*-specific QCQP.
"""

import logging
import abc

import numpy as np

from hynet.utilities.graph import get_graph_components
from hynet.qcqp.rank1approx import GraphTraversalRank1Approximator

_log = logging.getLogger(__name__)


class SolverInterface(abc.ABC):
    """
    Abstract base class for QCQP solvers.

    Derived classes implement a solver for the *hynet*-specific quadratically
    constrained quadratic program specified by an object of the class ``QCQP``.
    A solver may solve the nonconvex QCQP, its semidefinite relaxation (SDR),
    or its second-order cone relaxation (SOCR).

    Parameters
    ----------
    verbose : bool, optional
        If ``True``, the logging information of the solver is printed to the
        standard output.
    param : dict[str, object], optional
        Dictionary of parameters (``{'parameter_name': value}``) to modify the
        solver's default settings.
    rank1approx : Rank1Approximator, optional
        Rank-1 approximator for partial Hermitian matrices. This approximator
        is used in relaxation-based solvers.

    See Also
    --------
    hynet.qcqp.rank1approx : Rank-1 approximators.
    """
    def __init__(self, verbose=False, param=None, rank1approx=None):
        self.verbose = verbose
        # REMARK: It looks like everyone, at some point, has to stumble across
        # the highly unintuitive behavior of mutable defaults...for me it was
        # when the parameters of some solver popped up in another one. So be
        # aware and check out http://effbot.org/zone/default-values.htm ;)
        self.param = {} if param is None else param
        if rank1approx is None:
            self.rank1approx = GraphTraversalRank1Approximator()
        else:
            self.rank1approx = rank1approx

    def __str__(self):
        return self.name + ' (' + self.type.value + ')'

    @property
    @abc.abstractmethod
    def name(self):
        """Return the name of the solver."""

    @property
    @abc.abstractmethod
    def type(self):
        """Return the type of the solver as a SolverType."""

    @abc.abstractmethod
    def solve(self, qcqp):
        """
        Solve the given QCQP and return a ``QCQPResult`` object.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the QCQP.
        """

    @staticmethod
    def adjust_absolute_phase(qcqp, v):
        """
        Return ``v`` with absolute phase adjustment according to the root nodes.

        Due to the quadratic form in ``v``, the solution of the QCQP is
        ambiguous w.r.t. a common phase shift of the elements in ``v``
        associated with a connected component in the sparsity pattern. This
        method adjusts the absolute phase such that it is zero at the root
        node of the respective components.

        *Remark:* This method should be used in *QCQP solvers*. In SDR and SOCR
        solvers, the rank-1 approximation takes care of the absolute phase
        adjustment.

        Parameters
        ----------
        v : numpy.ndarray[.hynet_complex_]
            Optimizer ``v`` for the solved QCQP.

        Returns
        -------
        v : numpy.ndarray[.hynet_complex_]
            Optimizer ``v`` with absolute phase adjustment.
        """
        v_ = np.array(v)
        components = get_graph_components(np.arange(qcqp.dim_v), qcqp.edges,
                                          roots=qcqp.roots)
        for component in components:
            root = component[np.isin(component, qcqp.roots)]
            if len(root) == 0:  # pylint: disable=len-as-condition
                root = component[0]
            else:
                if len(root) > 1:
                    _log.warning("Sparsity pattern has ambiguous roots.")
                root = root[0]
            v_[component] *= np.exp(-1j * np.angle(v_[root]))
        return v_
