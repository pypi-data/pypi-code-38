# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" Unit tests for the 'utils' module within the ketos library
"""

import pytest
import numpy as np
import pandas as pd
from ketos.utils import tostring, morlet_func, octave_bands, random_floats, nearest_values, detect_peaks


@pytest.mark.test_tostring
def test_tostring():
    box = (1,2,3)
    s = tostring(box)
    assert s == '[1,2,3]'
    box = [1,2,3]
    s = tostring(box)
    assert s == '[1,2,3]'
    box = np.array([1,2,3])
    s = tostring(box)
    assert s == '[1,2,3]'
    box = [[1,2,3],[1,2]]
    s = tostring(box)
    assert s == '[[1,2,3],[1,2]]'

@pytest.mark.test_octave_bands
def test_octave_bands():
    fc, fmin, fmax = octave_bands(1, 3)
    assert fc[0] == 62.5
    assert fc[1] == 125.
    assert fc[2] == 250.

@pytest.mark.test_morlet_func
def test_morlet_func_single_time():
    time = 0.5
    f = morlet_func(time=time, frequency=10, width=3, displacement=0)
    assert f == pytest.approx(0.42768108, abs=1E-5) 

@pytest.mark.test_morlet_func
def test_morlet_func_multiple_times():
    time = np.array([-1., 0., 0.5])
    f = morlet_func(time=time, frequency=10, width=3, displacement=0)
    assert f[0] == pytest.approx(0.41022718, abs=1E-5) 
    assert f[1] == pytest.approx(0.43366254, abs=1E-5) 
    assert f[2] == pytest.approx(0.42768108, abs=1E-5) 

@pytest.mark.test_morlet_func
def test_morlet_func_with_dfdt_nonzero():
    time = 0.5
    f = morlet_func(time=time, frequency=10, width=3, displacement=0, dfdt=0.5)
    assert f == pytest.approx(0.302416, abs=1E-5) 

@pytest.mark.test_random_floats
def test_random_floats():
    x = random_floats(3, 0.4, 7.2)
    assert x[0] == pytest.approx(3.23574963, abs=1e-5)
    assert x[1] == pytest.approx(5.29820656, abs=1e-5)
    assert x[2] == pytest.approx(0.40077775, abs=1e-5)

@pytest.mark.test_nearest_values
def test_nearest_values():
    x = np.array([1.0, 4.0, 5.1, 6.0, 0.2, 0.3, 10.0])
    y = nearest_values(x=x, i=3, n=3)
    assert np.all(y == [5.1, 6.0, 0.2])
    y = nearest_values(x=x, i=0, n=3)
    assert np.all(y == [1.0, 4.0, 5.1])
    y = nearest_values(x=x, i=0, n=4)
    assert np.all(y == [1.0, 4.0, 5.1, 6.0])
    y = nearest_values(x=x, i=6, n=4)
    assert np.all(y == [10.0, 0.3, 0.2, 6.0])

def test_detect_peaks():
    # create a two time series, where only the first contains a peak
    d = {'series1' : pd.Series([1.0, 2.3, 22.0, 2.2, 1.5]), 'series2': pd.Series([1.0, 2.3, 1.8, 2.2, 1.5])}
    df = pd.DataFrame(d)
    # detect peaks with multiplicity 1 and prominence of at least 2.0
    peaks = detect_peaks(df=df, multiplicity=1, prominence=2.0)
    assert np.all(peaks == [0, 0, 1, 0, 0])
    # try again, but this time require multiplicity 2
    peaks = detect_peaks(df=df, multiplicity=2, prominence=2.0)
    assert np.all(peaks == [0, 0, 0, 0, 0])
