# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C)      2018 Maximilian Stahlberg
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

import os

# The Problem class is the user's main way of interfacing PICOS.
from .problem import Problem
new_problem = Problem

# Make character set changes available.
from .glyphs import ascii, latin1, unicode, default as default_charset

# Basic tools.
from .tools import import_cbf, new_param

# Constraints and expressions that cannot be created algebraically.
from .tools import ball, expcone, flow_Constraint, simplex, truncated_simplex

# Algebraic functions. (TODO: Give them a module of their own.)
from .tools import detrootn, diag, diag_vect, exp, geomean, kron, \
    kullback_leibler, lambda_max, lambda_min, log, logsumexp, lse, norm, \
    partial_trace, partial_transpose, sum, sumexp, sum_k_largest, \
    sum_k_largest_lambda, sum_k_smallest, sum_k_smallest_lambda, trace, tracepow

# Exceptions that the user might want to catch.
from .tools import DualizationError, NonConvexError, NotAppropriateSolverError,\
    QuadAsSocpError

LOCATION = os.path.realpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))
VERSION_FILE = os.path.join(LOCATION, ".version")

def get_version_info():
    with open(VERSION_FILE, "r") as versionFile:
        return tuple(versionFile.read().strip().split("."))

__version_info__ = get_version_info()
__version__ = '.'.join(__version_info__)
