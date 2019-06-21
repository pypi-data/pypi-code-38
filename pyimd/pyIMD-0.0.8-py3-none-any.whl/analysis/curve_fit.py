# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *     Gotthold Fläschner - formulas and implementation
# *******************************************************************************/

import numpy as np

__author__ = 'Andreas P. Cuny'


def fit_function(x, fn, q, a, b):
    """Defines the phase response of a damped harmonic oscillator (i.e. the cantilever with or without cell).
    It is called from calculate_resonance_frequencies, to be fitted to the data primarily to extract the natural resonance \
    frequency.

    Args:
         x (`float`):              Frequency (the independent variable of that function)
         fn (`float`):             Natural resonance frequency
         q (`float`):              Q factor (losses)
         a (`float`):              Linear factor accounting for a linear background
         b (`float`):              Constant Phase-Offset

    Returns:
        phase (`float`):           Returns the phase.
    """

    phase = -np.arctan(q * (fn * fn - x * x)/(fn * x)) + a * x + b
    return phase


