#pylint: disable=no-member
"""
Numeric types and enumerations in *hynet*.
"""

from enum import Enum

import numpy as np
from scipy.sparse import coo_matrix

hynet_id_ = np.int64
hynet_int_ = np.int64
hynet_float_ = np.float64
hynet_complex_ = np.complex128
hynet_sparse_ = coo_matrix

# REMARK to sparse matrices in *hynet*:
# -------------------------------------
#
# First of all, KEEP THE COORDINATE SPARSITY FORMAT, even if the definition
# suggests that it may be modified ;) For performance reasons, I had to utilize
# its particular data organisation and a modification would break some code.
#
# Anyway, after several rounds of performance optimization the selection of the
# SciPy COO format is well motivated. Besides the fast creation of sparse
# matrices (e.g. in SystemModel) and enabling of efficient data reorganisation
# (e.g. in QCQP), the most profound reason for its choice is memory efficiency.
# For larger grids, thousands of sparse matrices are generated to construct the
# OPF QCQP and, for the originally employed CSR format (which is beneficial for
# slicing, indexing, and arithmetic), this soon leads to QCQP objects of 100MB
# and more. This high memory consumption is a particular issue with parallel
# and distributed processing, where certain objects are pickled. For example,
# during the constraint generation in SystemModel.get_opf_problem, this caused
# Python's multiprocessing package to crash for the 13659-bus grid of the
# PGLib. Switching to the COO format reduced the memory consumption
# considerably, e.g., for scenario 0 of the German 2030 NEP grid with 1524
# buses the pickle of its QCQP object was reduced from 113.7MB to 7.9MB, i.e.,
# by 93%.
#
# Finally, a particularity of COO matrices should be kept in mind, e.g., if a
# a new solver interface is implemented. This format permits duplicate entries,
# i.e., the matrix' attributes ``row``, ``col``, and ``data`` can contain
# entries that refer to the same matrix element, in which case they should be
# summed up. This is performed, e.g., during a conversion to CSR or CSC.
#
if hynet_sparse_(((1, 2), ((0, 0), (0, 0))), shape=(1, 1)).tocsr()[0, 0] != 3:
    raise RuntimeError("Sparse matrix initialization is incompatible.")

hynet_eps = np.finfo(hynet_float_).eps  # Machine epsilon


class BusType(Enum):
    """Type of voltage waveform experienced at the bus."""
    AC = 'ac'
    DC = 'dc'

    def __str__(self):
        return self.value.upper()


class BranchType(Enum):
    """Type of entity modeled by the branch."""
    LINE = 'line'
    TRANSFORMER = 'transformer'

    def __str__(self):
        return self.value.upper()


class InjectorType(Enum):
    """Type of entity modeled by the injector."""
    # Categories
    CONVENTIONAL = 'conventional'
    RENEWABLE = 'renewable'
    PROSUMER = 'prosumer'
    LOAD = 'load'
    COMPENSATION = 'compensation'

    # Subcategories for conventional generation
    COAL = 'conventional:coal'
    GAS = 'conventional:gas'
    NUCLEAR = 'conventional:nuclear'

    # Subcategories for renewables
    HYDRO = 'renewable:hydro'
    WIND = 'renewable:wind'
    PV = 'renewable:pv'
    BIOMASS = 'renewable:biomass'
    GEOTHERMAL = 'renewable:geothermal'

    def is_conventional(self):
        """Return ``True`` if it is a conventional generation utility."""
        return self.value.startswith('conventional')

    def is_renewable(self):
        """Return ``True`` if it is a renewables-based generation utility."""
        return self.value.startswith('renewable')

    def is_prosumer(self):
        """Return ``True`` if it is a prosumer."""
        return self.value.startswith('prosumer')

    def is_load(self):
        """Return ``True`` if it is a load."""
        return self.value.startswith('load')

    def is_compensation(self):
        """Return ``True`` if it is a reactive power compensator."""
        return self.value.startswith('compensation')

    def __str__(self):
        """
        Return a formatted string for the injector type.

        This formatted string is generated from the value of the element, which
        a hierarchy of categories separated by a colon, i.e.,
        ::
          category:subcategory:subsubcategory

        During formatting, any underscores are replaced by blanks.
        """
        categories = self.value.replace('_', ' ').split(':')
        type_string = categories.pop(0)
        if categories:
            type_string += ' (' + '/'.join(categories) + ')'
        return type_string.upper()


class EntityType(Enum):
    """Type of entity that is deactivated in a scenario."""
    BUS = 'bus'
    BRANCH = 'branch'
    CONVERTER = 'converter'
    SHUNT = 'shunt'
    INJECTOR = 'injector'

    def __str__(self):
        return self.value.upper()

    def __lt__(self, other):
        # REMARK: This operator is required by SQLAlchemy as EntityType is
        # part of the primary key in DBScenarioInactivity
        return self.value < other.value


class SolverType(Enum):
    """Type of problem that can be solved with the solver."""
    QCQP = 'QCQP'
    SDR = 'SDR'
    SOCR = 'SOCR'


class SolverStatus(Enum):
    """Status returned by a solver after performing an optimization."""
    SOLVED = 0
    INACCURATE = 1
    UNBOUNDED = -1
    INFEASIBLE = -2
    FAILED = -4


class DBInfoKey(Enum):
    """Valid keys for the ``db_info`` table in a *hynet* grid database."""
    VERSION = "version"
    GRID_NAME = "grid_name"
    BASE_MVA = "base_mva"
    DESCRIPTION = "description"

    def __str__(self):
        return self.value
