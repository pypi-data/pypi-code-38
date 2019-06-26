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

""" Utilities module within the ketos library

    This module provides a number of auxiliary methods.
"""

import os
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def ensure_dir(file_path):
    """ Ensure that destination directory exists.

        If the directory does not exist, it is created.
        If it already exists, nothing happens.
        
        Args:
            file_path: str
                Full path to destination
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def random_floats(size=1, low=0, high=1, seed=1):
    """ Returns a random number or numpy array of randum numbers uniformly distributed in the half-open interval [low, high)
        
        Args:
            size: int
                Number of random numbers to be generated
            low: float
                Lower value
            high: float
                Upper value (not included)
            seed: int
                Seed for the random number generator

        Returns:
            res: float or numpy array
                Generated random number(s)

        Example:
            >>> from ketos.utils import random_floats
            >>> 
            >>> x = random_floats(3, 0.4, 7.2)
            >>> print(x)
            [3.23574963 5.29820656 0.40077775]
    """

    assert high >= low, "Upper limit must be greater than or equal to lower limit"
    assert size >= 1, "Size must be an int greater than or equal to 1"

    np.random.seed(seed)

    if high == low:
        if size == 1:
            res = high
        else:
            res = np.ones(size, dtype=float) * high
    
    else:
        rndm = np.random.random_sample(size)
        res = low + (high - low) * rndm
        if len(res) == 1:
            res = np.float(res)

    return res

def ndim(a):
    """ Returns the number of dimensions of a list/tuple/array.
        
        Args:
            a: list, tuple or numpy array
                Object that we wish to obtain the dimension of 

        Returns:
            n: int
                Number of dimensions

        Example:
            >>> from ketos.utils import ndim
            >>> 
            >>> x = [[0, 1, 2, 3],(4, 5)]
            >>> print(ndim(x))
            2
    """
    if not (type(a) == list or type(a) == tuple or type(a) == np.ndarray):
        return 0

    if len(a) == 0:
        return 1

    n = 1 + ndim(a[0])
    return n

def tostring(box, decimals=None):
    """ Convert an array, tuple or list into a string.

        Args:
            box: array, tuple or list
                Array, tuple or list that will be converted into a string.
            decimals: int
                Number of decimals that will be kept in the conversion to string.

        Returns:
            s: str
                String representation of array/tuple/list.

        Example:
            >>> from ketos.utils import tostring
            >>> 
            >>> y = [[0, 1, 2, 3],(4, 5)]
            >>> print(tostring(y))
            [[0,1,2,3],[4,5]]
    """
    if box is None:
        return ''

    box = np.array(box)

    if decimals is not None:
        box = np.around(box, decimals=int(decimals))

    box = box.tolist()

    s = str(box)
    s = s.replace(' ', '')
    s = s.replace('(', '[')
    s = s.replace(')', ']')

    return s

def octave_bands(band_min=-1, band_max=9):
    """ Compute the min, central, and max frequency value 
        of the specified octave bands, using the following 
        formulas,

            f_centre = 10^3 * 2^p ,
            f_min = f_centre / sqrt(2) ,
            f_max = f_centre * sqrt(2) ,

        where p = band_number - 5

        Args:
            band_min: int
                Lower octave band
            band_max: int
                Upper octave band

        Returns:
            fcentre: numpy array
                Central frequency of each band (in Hz)
            flow: numpy array
                Minimum frequency of each band (in Hz)
            fhigh: numpy array
                Maximum frequency of each band (in Hz)

        Example:
            >>> from ketos.utils import octave_bands
            >>> 
            >>> fc, fmin, fmax = octave_bands(1, 3)
            >>> print(fc)
            [ 62.5 125.  250. ]
    """
    p = np.arange(band_min-5., band_max-4.)
    fcentre = np.power(10.,3) * np.power(2.,p)
    fd = np.sqrt(2.)
    flow = fcentre / fd
    fhigh = fcentre * fd
    return fcentre, flow, fhigh

def octave_bands_json(band_min, band_max):
    """ Produce a string of the specified octave bands
        in json format

        Args:
            band_min: int
                Lower octave band
            band_max: int
                Upper octave band

        Returns:
            s: str
                json format string

        Example:
            >>> from ketos.utils import octave_bands_json
            >>> 
            >>> s = octave_bands_json(1, 2)
    """
    fcentre, flow, fhigh = octave_bands(band_min, band_max)

    s = "\"frequency_bands\": [\n"
    n = len(flow)
    for i in range(n):
        s += "\t{\n"
        s += "\t\t\"name\": \"{0:.0f}Hz\",\n".format(fcentre[i])
        s += "\t\t\"range\": [\"{0:.1f}Hz\", \"{1:.1f}Hz\"]".format(flow[i],fhigh[i])
        endpar = "\n\t}"
        if i < n-1:
            endpar += ","

        s += endpar + "\n"

    s += "]"
    return s

def morlet_func(time, frequency, width, displacement, norm=True, dfdt=0):
    """ Compute Morlet wavelet function

        The function is implemented as in Eq. (15) in John Ashmead, "Morlet Wavelets in Quantum Mechanics",
        Quanta 2012; 1: 58-70, with the replacement f -> 2*pi*f*s, to allow f to be identified with the 
        physical frequency.

        Args:
            time: float or numpy array
               Time in seconds at which the function is to be evaluated
            frequency: float
                Wavelet frequency in Hz
            width: float
                Wavelet width in seconds (1-sigma width of the Gaussian envelope function)
            displacement: float
                Wavelet centroid in seconds
            norm: bool
                Include [pi^1/4*sqrt(sigma)]^-1 normalization factor
            dfdt: float
                Rate of change in frequency as a function of time in Hz per second.
                If dfdt is non-zero, the frequency is computed as 
                    
                    f = frequency + (time - displacement) * dfdt 

        Returns:
            y: float or numpy array
                Value of Morlet wavelet function at time t

        Example:
            >>> from ketos.utils import morlet_func
            >>> 
            >>> time = np.array([-1., 0., 0.5])
            >>> f = morlet_func(time=time, frequency=10, width=3, displacement=0)
            >>> print(f)
            [0.41022718 0.43366254 0.42768108]
    """
    if dfdt != 0:
        frequency += (time - displacement) * dfdt
    
    assert np.all(frequency > 0), "Frequency must be a strictly positive float"
    assert width > 0, "Width must be a strictly positive float"

    t = time
    w = 2 * np.pi * frequency * width
    s = width
    l = displacement
    x = (t-l)/s

    y = (np.exp(1j*w*x) - np.exp(-0.5*(w**2))) * np.exp(-0.5*(x**2))

    if norm:
        y *= (s * np.sqrt(np.pi) * (1 + np.exp(-w**2) - 2*np.exp(-0.75*w**2)) )**-0.5

    return np.real(y)


def nearest_values(x, i, n):
    """ Returns the n values nearest to index i from the array x.

        Here, nearest refers to the position in the array, not 
        the value.

        Args:
            x: numpy array
                Input values
            i: int
                Index
            n: int
                Number of neighboring values

        Returns:
            y: numpy array
                n values nearest to index i from the array x 

        Example:
            >>> from ketos.utils import nearest_values
            >>> 
            >>> x = np.array([1.0, 4.0, 5.1, 6.0, 0.2, 0.3, 10.0])
            >>> y = nearest_values(x=x, i=3, n=3)
            >>> print(y)
            [5.1 6.  0.2]
    """
    if n >= x.shape[0]:
        return x

    if n%2 == 0:
        i1 = int(i - n/2)
        i2 = int(i + n/2 - 1)
    else:
        i1 = int(i - (n-1)/2)
        i2 = int(i + (n-1)/2)

    if i1 >= 0 and i2 < x.shape[0]:
        return x[i1:i2+1]

    v = list()
    v.append(x[i])
    k = 1
    while len(v) < n:
        if k%2 == 0:
            d = k/2
        else:
            d = (k+1)/2
        j = int(i + np.power(-1,k) * d)
        if j >= 0 and j < x.shape[0]:
            v.append(x[j])
        k += 1
    v = np.array(v)
    return v


def detect_peaks(df, distance=1, multiplicity=1, prominence=1.0, height=None, threshold=None):
    """ Detect peaks in time-series data.

        The time-series data is provided in the form of a Pandas DataFrame object, where 
        each column contains a different time series.

        This is essentially a wrapper around a SciPy's find_peaks method:

            https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html

        Args:
            df: Pandas DataFrame
                Data frame containing the input data.
            distance: int
                Minimum distance between adjacent peaks
            multiplicity: int
                Number of time series in which peaks must appear to be counted.
            prominence: float
                Required prominence of the peaks. The prominence of a peak measures how much a peak 
                stands out from the surrounding baseline of the signal and is defined as the vertical 
                distance between the peak and its lowest contour line. See also 
                https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html#scipy.signal.peak_prominences
            height: float
                Required absolute height of the peaks.
            threshold: float
                Required threshold of peaks (the vertical distance to its neighbouring samples).

        Returns:
            y: Pandas DataFrame 
                Data frame containing the detected peaks

        Example:
            >>> from ketos.utils import detect_peaks
            >>> import pandas as pd
            >>>
            >>> # create a two time series, where only the first contains a peak
            >>> d = {'series1' : pd.Series([1.0, 2.3, 22.0, 2.2, 1.5]), 'series2': pd.Series([1.0, 2.3, 1.8, 2.2, 1.5])}
            >>> df = pd.DataFrame(d)
            >>> 
            >>> # detect peaks with multiplicity 1 and prominence of at least 2.0
            >>> peaks = detect_peaks(df=df, multiplicity=1, prominence=2.0)
            >>> print(peaks)
            [0 0 1 0 0]
            >>> 
            >>> # try again, but this time require multiplicity 2
            >>> peaks = detect_peaks(df=df, multiplicity=2, prominence=2.0)
            >>> print(peaks)
            [0 0 0 0 0]
    """
    peaks = pd.DataFrame(index=df.index)

    for column in df:
        x = df[column]
        m = np.median(np.abs(x - np.median(x)))
        if prominence > 0:
            min_prominence = m * prominence
        else:
            min_prominence = None
        positions, _ = find_peaks(x, height=height, threshold=threshold, distance=distance, prominence=(min_prominence,None))
        y = np.zeros(len(x))
        y[positions] = 1
        peaks[column] = y

    # sum across each row
    peaks = peaks.sum(axis=1) 

    # create column of FALSEs (no detection) and TRUES (detection)
    detections = pd.DataFrame((peaks >= multiplicity)) 

    # convert to 0s and 1s and extract numpy array
    res = detections[detections.columns[0]].astype(int).values 

    return res


def get_member(cls, member_name):
    """ Query class member by name.

        Returns ValueError if class does not contain a member by that name.

        Args:
            cls: Class
                Class
            member_name: str
                Member name

        Returns:
            member: 
                The class member
    """
    for name, member in cls.__members__.items():
        if member_name == name:
            return member

    s = ", ".join(name for name, _ in cls.__members__.items())
    raise ValueError("Unknown value \'{0}\'. Select between: {1}".format(member_name, s))
