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
from math import pi
from scipy import optimize
from pyIMD.analysis.curve_fit import fit_function

__author__ = 'Andreas P. Cuny'


def calculate_mass(spring_constant, res_freq_after_cell_load, res_freq_before_cell_load):
    """Calculates the mass given the spring constant of the cantilever and the resonance frequency without and with \
    cell attached to the cantilever.

    Args:

    spring_constant (`float`):            Stiffness of the cantilever [in N/m]
    res_freq_after_cell_load (`float`):   Resonance frequency of the cantilever AFTER the cell is picked up, at \
                                                 time point t [in kHz]
    res_freq_before_cell_load (`float`):  Resonance frequency of the cantilever BEFORE the cell is picked up \
                                                 [in kHz]


    Returns:
    mass (`float`):                        Returns data as float, which is the mass at time point t.

    """
    mass = (spring_constant / (4 * pi * pi) * (1 / (res_freq_after_cell_load*res_freq_after_cell_load) - 1 /
                                               (res_freq_before_cell_load*res_freq_before_cell_load))) * 1e6

    return mass


def calculate_resonance_frequencies(frequency_array, phase_array, initial_param_guess, lower_param_bounds,
                                    upper_param_bounds):

    """Calculate_resonance_frequencies calculates the resonance frequency
       from input frequency and phase array. It does so via fitting the phase response of a harmonic oscillator \
       (defined in pyIMD.analysis.curve_fit). The first fit parameter of the fit parameter array is the resonance \
       frequency.

    Args:
        frequency_array (`float array`):        Array of frequencies [in kHz]
        phase_array (`float array`):            Array of phase [in Rad]
        initial_param_guess (`float`):          Initial parameter guess (1x4 array)
        lower_param_bounds (`float`):           Lower bounds (1x4 array)
        upper_param_bounds (`float`):           Upper bounds (1x4 array)

    Returns:
        resonance_frequency (`float`):          Resonance frequency [in kHz]
    Returns:
        curve_fit_parameter (`float array`):    Curve fit parameters
                                                curve_fit_parameter[0] := Q factor (losses)

                                                curve_fit_parameter[1] := Linear factor accounting for a linear \
                                                background

                                                curve_fit_parameter[2] := Offset of the background
    """

    params, _ = optimize.curve_fit(fit_function, frequency_array.astype(float), phase_array.astype(float),
                                   p0=initial_param_guess, bounds=(lower_param_bounds, upper_param_bounds))

    resonance_frequency = params[0]
    return resonance_frequency, params[1:]


def calculate_position_correction(cell_position, cantilever_length):

    """Calculates the correction factor with which the measured mass needs to be
    multiplied to get all the mass present on the cantilever. This is needed as the cantilever is differently sensitive
    to mass, depending on the location where this mass is attached. The measurements are performed with the first mode \
    of vibration, which is described by the factor kL = 1.875. For higher modes, different would be used (4.694 for \
    the second , 7.855 for the third etc.)

    Args:
        cell_position (`float`):       Cell position from the free end of the cantilever [in micrometer]
        cantilever_length (`float`):   Cantilever length [in micrometer]

    Returns:
        correction_factor (`float`):   Returns a double which is the correction factor.
    """

    kL = 1.875
    cantilever_length = cantilever_length/1e6
    cell_position = cell_position/1e6
    k = kL / cantilever_length
    return (1/(0.5*((np.cos(k * (cantilever_length - cell_position)) - np.cosh(k * (cantilever_length - cell_position)))
                    - (np.cos(k * cantilever_length) + np.cosh(k*cantilever_length)) / (np.sin(k * cantilever_length) +
                                                                                        np.sinh(k * cantilever_length))
                    * (np.sin(k * (cantilever_length - cell_position)) - np.sinh(k *
                                                                                 (cantilever_length-cell_position)))))
            ** 2)
