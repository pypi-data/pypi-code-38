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

""" spectrogram_filters module within the ketos library

    This module contains various filters that can be applied to spectrograms.

    Filters are implemented as classes, which are required to have the 
    attribute name and the method apply. 

    Contents:
        FAVThresholdFilter class
        FAVFilter class
        HarmonicFilter class
        FrequencyFilter class
        WindowFilter class
        WindowSubtractionFilter class
"""

import numpy as np
import pandas as pd
from ketos.audio_processing.spectrogram import Spectrogram
from ketos.utils import nearest_values



class FAVThresholdFilter():
    """ Modified Frequency Amplitude Variation (FAV) filter 
        combined with thresholding operation.

        Args:
            threshold: float
                Peak detection threshold 
            winlen: int
                Length of smoothing window
        
        Attributes:
            threshold: float
                Peak detection threshold, in units of std. dev.
            winlen: int
                Length of smoothing window
            name: str
                Filter name
            std: numpy array
                Standard deviation of the smoothened spectrum 
    """

    def __init__(self, threshold=3.0, winlen=7):

        self.threshold = threshold
        self.winlen = winlen
        self.name = "FAV"
        self.std = None
        self.FAV = FAVFilter(winlen)

    def apply(self, spec):
        """ Apply FAV thresholding filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        f = self.FAV
        N = self.winlen
        orig = spec.copy()

        # apply FAV filter
        f.apply(spec)

        z = np.empty((spec.image.shape[0],2))

        # loop over 1st dimension
        m = spec.image.shape[0]
        for i in range(m):
            x = spec.image[i]

            # thresholding operation
            y = x * (x > self.threshold * f.std[i])

            # find peaks
            y1 = np.r_[y[1:], 0]
            y2 = np.r_[0, y[:-1]]
            peaks = np.argwhere(np.logical_and(y > y1, y >= y2))
            peaks = np.squeeze(peaks)
            if np.ndim(peaks) == 0:
                peaks = np.array([peaks])

            # number of peaks and max strength
            num_peaks = len(peaks)
            max_strength = 0
            for p1 in peaks:
                p2 = p1 + max(2, int(N/2))
                max_strength = max(max_strength, np.max(orig.image[i,p1:p2]))

            z[i,0] = num_peaks
            z[i,1] = max_strength / 100.                                   

        spec.image = z
        spec.flabels = ['num_peaks', 'max_peak_strength']


class FAVFilter():
    """ Modified Frequency Amplitude Variation (FAV) filter.

        Algorithm based on Reis et al. "Automatic Detection of Vessel 
        Signatures in Audio Recordings with Spectral Amplitude Variation 
        Signature" (2019).

        First, the spectrogram is smoothened along the frequency axis 
        using a Blackman filter.
    
        Second, the difference between neighboring bins is computed, 
        also along the frequency axis, and raised to the 3rd power.        

        Third, the resulting matrix is shifted by 3 bins, along the 
        frequency axis, inverted, and multiplied with the unshifted matrix. 

        Finally, only positive values are retained.

        The result of this set of operations is to emphasize narrow 
        peaks in the frequency spectrum. (Here narrow implies narrower than 
        roughly half of the Blackman filter.)

        Args:
            winlen: int
                Length of smoothing window
        
        Attributes:
            winlen: int
                Length of smoothing window
            name: str
                Filter name
            std: numpy array
                Standard deviation of the smoothened spectrum 
    """

    def __init__(self, winlen=7):

        self.winlen = winlen
        self.name = "FAV"
        self.std = None

    def apply(self, spec):
        """ Apply FAV filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        x = spec.image
        N = self.winlen
        D = x.ndim

        assert D == 2, "FAVFilter.apply only accepts 2 dimensional arrays."
        assert x.shape[1] > N, "Frequency axis must be longer than window size."

        if N > 1:        
            # pad with reflected copies
            x = np.swapaxes(x,0,1)
            s = np.r_[x[N-1:0:-1], x, x[-2:-N-1:-1]]  
            x = np.swapaxes(x,0,1)        
            s = np.swapaxes(s,0,1)

            # blackman averaging filter
            w = np.blackman(N)

            # convolution
            K = x.shape[0]
            M = x.shape[1]
            y = np.empty((K,M+N-1))
            for i in range(s.shape[0]):
                y[i] = np.convolve(w/w.sum(), s[i], mode='valid')

            # remove ends
            k1 = int(N/2)
            k2 = -k1 + 2 - N%2
            x = y[:,k1:k2]

        # compute standard deviation
        self.std = np.std(x, axis=1)

        # difference to power of 3
        x = np.power(np.diff(x, axis=1), 3)

        # shift, invert and multiply by itself
        if N > 1:
            L = int(N/2)
        else:
            L = 1
        y = -x[:, L:]
        y = np.concatenate((y,np.zeros((y.shape[0],L))), axis=1)
        x = x * y
        x = x * (x > 0)

        spec.image = x


class HarmonicFilter():
    """ Performs Fast Fourier Transform (FFT) of the frequency axis.

        Attributes:
            name: str
                Filter name
    """

    def __init__(self):

        self.name = "Harmonic"

    def apply(self, spec):
        """ Apply harmonic filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        h = np.abs(np.fft.rfft(spec.image, axis=1))
        new_img = h[:,1:]

        flabels = list()
        for i in range(new_img.shape[1]):
            f = 2 * float(i) / float(new_img.shape[1]) * (spec.fmax() - spec.fmin)
            flabels.append("{0:.1f}Hz".format(f))

        spec.image = new_img
        spec.flabels = flabels


class CroppingFilter():
    """ Crops along the frequency dimension.

        Args:
            flow: float
                Lower bound on frequency in Hz
            fhigh: float
                Upper bound on frequency in Hz

        Attributes:
            name: str
                Filter name
    """

    def __init__(self, flow=None, fhigh=None):

        self.flow = flow
        self.fhigh = fhigh
        self.name = "Cropping"

    def apply(self, spec):
        """ Apply frequency cropping filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        spec.crop(flow=self.flow, fhigh=self.fhigh)


class FrequencyFilter():
    """ Splits the frequency axis into bands and computes 
        the average sound magnitude within each band.

        Args:
            bands: list(Interval)
                Frequency bands in Hz
            names: list(str)
                Names of the frequency bands

        Attributes:
            name: str
                Filter name
    """

    def __init__(self, bands, names=None):

        self.bands = bands
        self.names = names
        self.name = "Frequency"

    def apply(self, spec):
        """ Apply frequency filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        nt = spec.tbins()
        nf = len(self.bands)

        new_img = np.ma.zeros(shape=(nt,nf))

        for i in range(nf):
            b = self.bands[i]
            new_img[:,i] = spec.average(axis=1, flow=b.low, fhigh=b.high)

        # discard frequency bands with NaN's
        not_nan = ~np.any(np.isnan(new_img), axis=0)
        new_img = new_img[:, not_nan]
        names = [i for (i, v) in zip(self.names, not_nan) if v]

        # mask zeros
        new_img = np.ma.masked_values(new_img, 0)

        spec.image = new_img
        spec.flabels = names


class WindowFilter():
    """ Applies a windowed median/average filter to the spectrogram.

        Args:
            window_size: float
                Window size in seconds
            step_size: float
                Step size in seconds
            filter_func: 
                Filtering function. Default is np.ma.median

        Attributes:
            name: str
                Filter name
    """

    def __init__(self, window_size, step_size, filter_func=np.ma.median):

        self.window_size = window_size
        self.step_size = step_size
        self.filter_func = filter_func

        if filter_func is np.ma.median:
            self.name = "Median"
        elif filter_func is np.ma.average:
            self.name = "Average"
        else:
            self.name = "Window"
            

    def apply(self, spec):
        """ Apply filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        step = int(np.ceil(self.step_size / spec.tres))
        window = int(np.ceil(self.window_size / spec.tres))
        
        nt = spec.tbins()
        nf = spec.fbins()
        
        n = int(np.ceil(nt/step))

        img = spec.image
        new_img = np.zeros(shape=(n,nf))

        for i in range(n):
            i1 = i * step
            i2 = min(nt-1, i1 + window)
            new_img[i,:] = self.filter_func(img[i1:i2+1,:], axis=0)  # ignore entries with value=0

        # mask zeros
        new_img = np.ma.masked_values(new_img, 0)    

        spec.image = new_img
        spec.tres = step * spec.tres


class WindowSubtractionFilter():
    """ Applied a windowed median/average subtraction filter to the spectrogram.

        Args:
            window_size: float
                Window size in seconds
            filter_func: 
                Filtering function. Default is np.ma.median

        Attributes:
            name: str
                Filter name
    """

    def __init__(self, window_size, filter_func=np.ma.median):

        self.window_size = window_size
        self.filter_func = filter_func

        if filter_func is np.ma.median:
            self.name = "Median Subtraction"
        elif filter_func is np.ma.average:
            self.name = "Average Subtraction"
        else:
            self.name = "Window Subtraction"

    def apply(self, spec):
        """ Apply filter to spectrogram

            Args:
                spec: Spectrogram
                    Spectrogram to which filter will be applied 
        """
        window = 1 + 2 * int(0.5 * self.window_size / spec.tres)
        
        nt = spec.tbins()
        nf = spec.fbins()

        img = spec.image
        new_img = np.zeros(shape=(nt,nf))

        # loop over time bins
        for i in range(nt):

            # local median
            v = nearest_values(x=img, i=i, n=window)
            med = self.filter_func(v, axis=0)
            
            new_img[i,:] = img[i,:] - med
        
        spec.image = new_img

