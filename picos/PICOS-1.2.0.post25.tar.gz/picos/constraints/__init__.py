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
# This file serves as a helper to include all constraint types.
#-------------------------------------------------------------------------------

# Import the constraint base classes (for the automatic API documentation).
from .constraint import Constraint, MetaConstraint

# Import the native constraints.
from .con_affine  import AffineConstraint
from .con_expcone import ExpConeConstraint
from .con_lmi     import LMIConstraint
from .con_quad    import QuadConstraint
from .con_rsoc    import RSOCConstraint
from .con_soc     import SOCConstraint

# Import the derived constraints.
from .meta_absolute import AbsoluteValueConstraint
from .meta_detrootn import DetRootNConstraint
from .meta_flow     import FlowConstraint
from .meta_geomean  import GeoMeanConstraint
from .meta_kldiv    import KullbackLeiblerConstraint
from .meta_log      import LogConstraint
from .meta_lse      import LSEConstraint
from .meta_pnorm    import PNormConstraint
from .meta_pqnorm   import PQNormConstraint
from .meta_simplex  import SymTruncSimplexConstraint
from .meta_sumexp   import SumExpConstraint
from .meta_sumk     import SumExtremesConstraint
from .meta_tracepow import TracePowConstraint
