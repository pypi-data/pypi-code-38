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

""" Spectrogram module within the ketos library

    This module provides utilities to work with spectrograms.

    Spectrograms are two-dimensional visual representations of 
    sound waves, in which time is shown along the horizontal 
    axis, frequency along the vertical axis, and color is used 
    to indicate the sound amplitude. Read more on Wikipedia:
    https://en.wikipedia.org/wiki/Spectrogram

    The module contains the parent class Spectrogram, and three 
    child classes (MagSpectrogram, PowerSpectrogram, MelSpectrogram), 
    which inherit methods and attributes from the parent class.

    Note, however, that many of methods (e.g. crop) only work correctly 
    for the MagSpectrogram and PowerSpectrogram classes. See the documentation 
    of the individual methods for further details.

    Contents:
        Spectrogram class
        MagSpectrogram class
        PowerSpectrogram class
        MelSpectrogram class
"""

import numpy as np
from scipy.fftpack import dct
from scipy import ndimage
from skimage.transform import rescale
import matplotlib.pyplot as plt
import time
import datetime
import math
from ketos.audio_processing.audio_processing import make_frames, to_decibel, enhance_image
from ketos.audio_processing.audio import AudioSignal
from ketos.audio_processing.annotation import AnnotationHandler
from ketos.utils import random_floats
from tqdm import tqdm



def ensure_same_length(specs, pad=False):
    """ Ensure that all spectrograms have the same length

        Note that all spectrograms must have the same time resolution.
        If this is not the case, an assertion error will be thrown.
        
        Args:
            specs: list
                Input spectrograms
            pad: bool
                If True, the shorter spectrograms will be padded with zeros. If False, the longer spectrograms will be cropped (removing late times)
    
        Returns:   
            specs: list
                List of same-length spectrograms

        Example:

        >>> from ketos.audio_processing.audio import AudioSignal
        >>>
        >>> # Create two audio signals with different lengths
        >>> audio1 = AudioSignal.morlet(rate=100, frequency=5, width=1)   
        >>> audio2 = AudioSignal.morlet(rate=100, frequency=5, width=1.5)
        >>>
        >>> # Compute spectrograms
        >>> spec1 = MagSpectrogram(audio1, winlen=0.2, winstep=0.05)
        >>> spec2 = MagSpectrogram(audio2, winlen=0.2, winstep=0.05)
        >>>
        >>> # Print the durations
        >>> print('{0:.2f}, {1:.2f}'.format(spec1.duration(), spec2.duration()))
        5.85, 8.85
        >>>
        >>> # Ensure all spectrograms have same duration as the shortest spectrogram
        >>> specs = ensure_same_length([spec1, spec2])
        >>> print('{0:.2f}, {1:.2f}'.format(specs[0].duration(), specs[1].duration()))
        5.85, 5.85
    """
    if len(specs) == 0:
        return specs

    tres = specs[0].tres # time resolution of 1st spectrogram

    nt = list()
    for s in specs:
        assert s.tres == tres, 'Spectrograms must have the same time resolution' 
        nt.append(s.tbins())

    nt = np.array(nt)
    if pad: 
        n = np.max(nt)
        for s in specs:
            ns = s.tbins()
            if n-ns > 0:
                s.image = np.pad(s.image, pad_width=((0,n-ns),(0,0)), mode='constant')
                s.time_vector = np.append(s.time_vector, np.zeros(n-ns))
                s.file_vector = np.append(s.file_vector, np.zeros(n-ns))
    else: 
        n = np.min(nt)
        for s in specs:
            s.image = s.image[:n]
            s.time_vector = s.time_vector[:n]
            s.file_vector = s.file_vector[:n]

    return specs


def interbreed(specs1, specs2, num, smooth=True, smooth_par=5,\
            scale=(1,1), t_scale=(1,1), f_scale=(1,1), seed=1,\
            validation_function=None, progress_bar=False, min_peak_diff=None,\
            output_file=None, max_size=1E9, max_annotations=10):
    """ Interbreed spectrograms to create new ones.

        Interbreeding consists in adding/superimposing two spectrograms on top of each other.

        If the spectrograms have different lengths, the shorter of the two will be placed 
        within the larger one with a randomly generated time offset.

        The shorter spectrogram may also be subject to re-scaling along any of its dimensions, as 
        specified via the arguments t_scale_min, t_scale_max, f_scale_min, f_scale_max, scale_min, scale_max.

        Note that the spectrograms must have the same time and frequency resolution. Otherwise an assertion error will be thrown.

        Args:
            specs1: list
                First group of input spectrograms.
            specs2: list
                Second group of input spectrograms.
            num: int
                Number of spectrograms that will be created
            smooth: bool
                If True, a smoothing operation will be applied 
                to avoid sharp discontinuities in the resulting spetrogram
            smooth_par: int
                Smoothing parameter. The larger the value, the less 
                smoothing. Only applicable if smooth is set to True
            scale: tuple
                Scale the spectrogram that is being added by a random 
                number between [a,b)
            t_scale: tuple
                Scale the time axis of the spectrogram that is being added 
                by a random number between [a,b)
            f_scale: tuple
                Scale the frequency axis of the spectrogram that is being added 
                by a random number between [a,b)
            seed: int
                Seed for numpy's random number generator
            validation_function:
                This function is applied to each new spectrogram. 
                The function must accept 'spec1', 'spec2', and 'new_spec'. 
                Returns True or False. If True, the new spectrogram is accepted; 
                if False, it gets discarded.
            progress_bar: bool
                Option to display progress bar.
            min_peak_diff: float
                If specified, the following validation criterion is used:
                max(spec2) > max(spec1) + min_peak_diff
            output_file: str
                Full path to output database file (*.h5). If no output file is 
                provided (default), the spectrograms created are kept in memory 
                and passed as return argument; If an output file is provided, 
                the spectrograms are saved to disk.
            max_annotations: int
                Maximum number of annotations allowed for any spectrogram. 
                Only applicable if output_file is specified.
            max_size: int
                Maximum size of output database file in bytes
                If file exceeds this size, it will be split up into several 
                files with _000, _001, etc, appended to the filename.
                The default values is max_size=1E9 (1 Gbyte)
                Only applicable if output_file is specified.
        Returns:   
            specs: Spectrogram or list of Spectrograms
                Created spectrogram(s). Returns None if output_file is specified.

        Examples:
            >>> # extract saved spectrograms from database file
            >>> import tables
            >>> import ketos.data_handling.database_interface as di
            >>> db = tables.open_file("ketos/tests/assets/morlet.h5", "r") 
            >>> spec1 = di.load_specs(di.open_table(db, "/spec1"))[0]
            >>> spec2 = di.load_specs(di.open_table(db, "/spec2"))[0]
            >>> db.close()
            >>> 
            >>> # interbreed the two spectrograms once to make one new spectrogram
            >>> from ketos.audio_processing.spectrogram import interbreed
            >>> new_spec = interbreed([spec1], [spec2], num=1)
            >>>
            >>> # plot the original spectrograms and the new one
            >>> fig = spec1.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/spec1.png")
            >>> fig = spec2.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/spec2.png")
            >>> fig = new_spec.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/new_spec.png")

            .. image:: ../../../../ketos/tests/assets/tmp/spec1.png

            .. image:: ../../../../ketos/tests/assets/tmp/spec2.png

            .. image:: ../../../../ketos/tests/assets/tmp/new_spec.png

            >>> # Interbreed the two spectrograms to make 3 new spectrograms.
            >>> # Apply a random scaling factor between 0.0 and 5.0 to the spectrogram 
            >>> # that is being added.
            >>> # Only accept spectrograms with peak value at least two times 
            >>> # larger than either of the two parent spectrograms
            >>> def func(spec1, spec2, new_spec):
            ...     m1 = np.max(spec1.image)
            ...     m2 = np.max(spec2.image)
            ...     m = np.max(new_spec.image)
            ...     return m >= 2 * max(m1, m2)
            >>> new_specs = interbreed([spec1], [spec2], num=3, scale=(0,5), validation_function=func)
            >>>
            >>> # plot the first of the new spectrograms
            >>> fig = new_specs[0].plot()
            >>> fig.savefig("ketos/tests/assets/tmp/new_spec_x.png")

            .. image:: ../../../../ketos/tests/assets/tmp/new_spec_x.png

    """
    if output_file:
        from ketos.data_handling.database_interface import SpecWriter
        writer = SpecWriter(output_file=output_file, max_size=max_size, max_annotations=max_annotations)

    # set random seed
    np.random.seed(seed)

    # default validation function always returns True
    if validation_function is None:        
        def always_true(spec1, spec2, new_spec):
            return True

        validation_function = always_true

    if progress_bar:
        import sys
        nprog = max(1, int(num / 100.))

    specs_counter = 0
    specs = list()
    while specs_counter < num:
        
        N = num - len(specs)
        N = num - specs_counter

        # randomly select spectrograms
        _specs1 = np.random.choice(specs1, N, replace=True)
        _specs2 = np.random.choice(specs2, N, replace=True)

        # randomly sampled scaling factors
        sf_t = random_floats(size=N, low=t_scale[0], high=t_scale[1], seed=seed)
        sf_f = random_floats(size=N, low=f_scale[0], high=f_scale[1], seed=seed)
        sf = random_floats(size=N, low=scale[0], high=scale[1], seed=seed)
        seed += 1

        if N == 1:
            sf_t = [sf_t]
            sf_f = [sf_f]
            sf = [sf]

        for i in range(N):

            if progress_bar:
                if len(specs_counter) % nprog == 0:
                    sys.stdout.write('{0:.0f}% \r'.format(specs_counter / num * 100.))

            s1 = _specs1[i]
            s2 = _specs2[i]

            # time offset
            dt = s1.duration() - s2.duration()
            if dt != 0:
                rndm = np.random.random_sample()
                delay = np.abs(dt) * rndm
            else:
                delay = 0

            spec = s1.copy() # make a copy

            if min_peak_diff is not None:
                diff = sf[i] * np.max(s2.image) - np.max(s1.image)
                if diff < min_peak_diff:
                    continue

            # add the two spectrograms
            spec.add(spec=s2, delay=delay, scale=sf[i], make_copy=True,\
                    smooth=smooth, smooth_par=smooth_par, t_scale=sf_t[i], f_scale=sf_f[i])

            if validation_function(s1, s2, spec):
                if output_file:
                    writer.cd('/spec')
                    writer.write(spec)
                else:                    
                    specs.append(spec)
                
                specs_counter += 1

            if specs_counter >= num:
                break

    if progress_bar:
        print('100%')

    if output_file:
        writer.close()
        return None

    else:
        # if list has length 1, return the element rather than the list
        if len(specs) == 1:
            specs = specs[0]

        return specs


class Spectrogram(AnnotationHandler):
    """ Spectrogram

        Parent class for MagSpectrogram, PowerSpectrogram, and MelSpectrogram.
    
        The 0th axis is the time axis (t-axis).
        The 1st axis is the frequency axis (f-axis).
        
        Each axis is characterized by a starting value (tmin and fmin)
        and a resolution (tres and fres).

        Use the annotation method to add annotations to the spectrogram.

        Args:
            image: 2d numpy array
                Spectrogram image
            NFFT: int
                Number of points for the FFT. If None, set equal to the number of samples.
            tres: float
                Time resolution in seconds (i.e. bin size used for x axis)
            tmin: float
                Start time in seconds
            fres: float
                Frequency resolution in Hz (i.e. bin size used for y axis)
            fmin: float
                Minimum frequency in Hz (i.e. frequency value of bin 0)
            timestamp: datetime
                Spectrogram time stamp (default: None)
            flabels: list or array
               Labels for the frequency bins (optional)
            tag: str
                Identifier, typically the name of the wave file used to generate the spectrogram
            decibel: bool
                Use logarithmic z axis
            
        Attributes:
            image: 2d numpy array
                Spectrogram image
            NFFT: int
                Number of points for the FFT. If None, set equal to the number of samples.
            tres: float
                Time resolution in seconds (i.e. bin size used for x axis)
            tmin: float
                Start time in seconds
            fres: float
                Frequency resolution in Hz (i.e. bin size used for y axis)
            fmin: float
                Minimum frequency in Hz (i.e. frequency value of bin 0)
            timestamp: datetime
                Spectrogram time stamp (default: None)
            flabels: list or array
                Labels for the frequency bins (optional)
            file_dict: dict
                Wave files used to generate this spectrogram
            file_vector: 1d numpy array
                Associates a particular wave file with each time bin in the spectrogram
            time_vector: 1d numpy array
                Associated a particular time within a wave file with each time bin in the spectrogram
"""
    def __init__(self, image=np.zeros((2,2)), NFFT=0, tres=1, tmin=0, fres=1, fmin=0, timestamp=None, flabels=None, tag='', decibel=False):
        
        self.image = image
        self.NFFT = NFFT
        self.tres = tres
        self.tmin = tmin
        self.fres = fres
        self.fmin = fmin
        self.timestamp = timestamp
        self.flabels = flabels
        self.decibel = decibel

        super().__init__() # initialize AnnotationHandler

        # assign values to the file dictionary and the file and time vectors
        self.file_dict, self.file_vector, self.time_vector = self._create_tracking_data(tag)        

    def _create_tracking_data(self, tag):
        """ Creates a file dictionary, a file vector and a time vector

            Args:
                tag: str
                    Identifier, typically the name of the wave file used to generate the spectrogram

            Returns: 
                file_dict: dict
                    Wave files used to generate this spectrogram
                file_vector: 1d numpy array
                    Associates a particular wave file with each time bin in the spectrogram
                time_vector: 1d numpy array
                    Associated a particular time within a wave file with each time bin in the spectrogram

            Example:
                >>> from ketos.audio_processing.spectrogram import Spectrogram
                >>> spec = Spectrogram(tag='file.wav') # create a dummy spectrogram
                >>> print(spec.file_dict) # inspect the file dictionary
                {0: 'file.wav'}
        """                
        n = self.image.shape[0]
        time_vector = self.tres * np.arange(n, dtype=float) + self.tmin
        file_vector = np.zeros(n)
        file_dict = {0: tag}
        return file_dict, file_vector, time_vector

    def _crop_tracking_data(self, tlow=None, thigh=None, tpad=False, bin_no=False):
        """ Update tracking data in response to a cropping operation

            Args:
                tlow: float
                    Lower limit of time cut, measured in duration from the beginning of the spectrogram
                thigh: float
                    Upper limit of time cut, measured in duration from the beginning of the spectrogram start 
                bin_no: bool
                    Indicate if time cuts (tlow, thigh) are given in physical units (default) or 
                    bin numbers. 

            Returns:
                new_file_dict: dict
                    Cropped file dictionary
                new_file_vector: 1d numpy array
                    Cropped file vector
                new_time_vector: 1d numpy array
                    Cropped time vector
        """
        tbin1 = 0
        tbin2 = self.tbins()

        if tlow is not None: 
            if bin_no:
                tbin1 = tlow
            else:
                tbin1 = self._find_tbin(tlow, truncate=False)
        if thigh is not None: 
            if bin_no:
                tbin2 = thigh
            else:
                tbin2 = self._find_tbin(thigh, truncate=False, roundup=False) + 1 # when cropping, include upper bin
        
        N = len(self.time_vector)
        tbin1r = max(0, tbin1)
        tbin2r = min(N, tbin2)

        new_time_vector = self.time_vector.copy()
        new_time_vector = new_time_vector[tbin1r:tbin2r]

        file_vector = self.file_vector.copy()
        file_vector = file_vector[tbin1r:tbin2r]

        if tpad:
            if tbin1 < 0:
                new_time_vector = np.insert(new_time_vector, 0, np.zeros(-tbin1))
                file_vector = np.insert(file_vector, 0, np.zeros(-tbin1))
            if tbin2 > N:
                new_time_vector = np.append(new_time_vector, np.zeros(tbin2-N))
                file_vector = np.append(file_vector, np.zeros(tbin2-N))

        new_file_dict = {}
        new_file_vector = file_vector.copy()
        new_key = 0
        for it in self.file_dict.items():
            key = it[0]
            val = it[1]
            if np.any(file_vector == key):
                new_file_dict[new_key] = val
                new_file_vector[file_vector == key] = new_key
                new_key += 1

        return new_time_vector, new_file_vector, new_file_dict

    def get_time_vector(self):
        """ Get the spectrogram's time vector

            Returns:
                v: 1d numpy array
                    Time vector
        """
        v = self.time_vector
        return v

    def get_file_vector(self):
        """ Get the spectrogram's file vector

            Returns:
                v: 1d numpy array
                    File vector
        """
        v = self.file_vector
        return v

    def get_file_dict(self):
        """ Get the spectrogram's file dictionary

            Returns:
                d: dict
                    File dictionary
        """
        d = self.file_dict
        return d

    def copy(self):
        """ Make a deep copy of the spectrogram.

            Returns:
                spec: Spectrogram
                    Spectrogram copy.
        """
        spec = self.__class__()
        spec.image = np.copy(self.image)
        spec.NFFT = self.NFFT
        spec.tres = self.tres
        spec.tmin = self.tmin
        spec.fres = self.fres
        spec.fmin = self.fmin
        spec.timestamp = self.timestamp
        spec.flabels = self.flabels
        spec.time_vector = self.time_vector.copy()
        spec.file_vector = self.file_vector.copy()
        spec.file_dict = self.file_dict.copy()
        spec.labels = self.labels.copy()
        spec.boxes = list()
        for b in self.boxes:
            spec.boxes.append(b.copy())

        return spec

    def _make_spec(self, audio_signal, winlen, winstep, hamming=True, NFFT=None, timestamp=None, compute_phase=False, decibel=False):
        """ Create spectrogram from audio signal
        
            Args:
                signal: AudioSignal
                    Audio signal 
                winlen: float
                    Window size in seconds
                winstep: float
                    Step size in seconds 
                hamming: bool
                    Apply Hamming window
                NFFT: int
                    Number of points for the FFT. If None, set equal to the number of samples.
                timestamp: datetime
                    Spectrogram time stamp (default: None)
                compute_phase: bool
                    Compute phase spectrogram in addition to magnitude spectrogram
                decibel: bool
                    Use logarithmic (decibel) scale.

            Returns:
                image: numpy.array
                    Magnitude spectrogram
                NFFT: int, int
                    Number of points used for the FFT
                fres: int
                    Frequency resolution
                phase_change: numpy.array
                    Phase change spectrogram. Only computed if compute_phase=True.
        """
        # Make frames
        frames = audio_signal.make_frames(winlen, winstep) 

        # Apply Hamming window    
        if hamming:
            frames *= np.hamming(frames.shape[1])

        # Compute fast fourier transform
        fft = np.fft.rfft(frames, n=NFFT)

        # Compute magnitude
        image = np.abs(fft)

        # Compute phase
        if compute_phase:
            phase = np.angle(fft)

            # phase discontinuity due to mismatch between step size and bin frequency
            N = int(round(winstep * audio_signal.rate))
            T = N / audio_signal.rate
            f = np.arange(image.shape[1], dtype=np.float64)
            f += 0.5
            f *= audio_signal.rate / 2. / image.shape[1]
            p = f * T
            jump = 2*np.pi * (p - np.floor(p))
            corr = np.repeat([jump], image.shape[0], axis=0)
            
            # observed phase difference
            shifted = np.append(phase, [phase[-1,:]], axis=0)
            shifted = shifted[1:,:]
            diff = shifted - phase

            # observed phase difference corrected for discontinuity
            diff[diff < 0] = diff[diff < 0] + 2*np.pi
            diff -= corr
            diff[diff < 0] = diff[diff < 0] + 2*np.pi

            # mirror at pi
            diff[diff > np.pi] = 2*np.pi - diff[diff > np.pi]

        else:
            diff = None

        # Number of points used for FFT
        if NFFT is None:
            NFFT = frames.shape[1]
        
        # Frequency resolution
        fres = audio_signal.rate / 2. / image.shape[1]

        # use logarithmic axis
        if decibel:
            image = to_decibel(image)

        phase_change = diff
        return image, NFFT, fres, phase_change

    def get_data(self):
        """ Get the underlying data numpy array

            Returns:
                self.image: numpy array
                    Image
        """
        return self.image

    def annotate(self, labels, boxes):
        """ Add a set of annotations

            Args:
                labels: list(int)
                    Annotation labels
                boxes: list(tuple)
                    Annotation boxes, specifying the start and stop time of the annotation 
                    and, optionally, the minimum and maximum frequency.

            Example:
                >>> # create an audio signal
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> s = AudioSignal.morlet(rate=1000, frequency=300, width=1)
                >>> # compute the spectrogram
                >>> from ketos.audio_processing.spectrogram import Spectrogram
                >>> spec = MagSpectrogram(s, winlen=0.2, winstep=0.05)
                >>> # add two annotations
                >>> spec.annotate(labels=[1,2], boxes=[[1.5,4.5],[5.0,5.4]])
                >>> # show the spectrogram with the annotation that has label=1
                >>> fig = spec.plot(label=1)
                >>> fig.savefig("ketos/tests/assets/tmp/spec_label1.png")

                .. image:: ../../../../ketos/tests/assets/tmp/spec_label1.png

        """
        super().annotate(labels, boxes)
        for b in self.boxes:
            if b[3] == math.inf:
                b[3] = self.fmax()

    def _find_bin(self, x, bins, x_min, x_max, truncate=False, roundup=True):
        """ Find bin corresponding to given value

            If the value coincides with a bin boundary, the high bin number will 
            be return if roundup is True (default), or the lower bin number if roundup is False.

            If Truncate is False (default):
             * Returns -1, if x < x_min
             * Returns N, if x >= x_max, where N is the number of bins

            If Truncate is True:
             * Returns 0, if x < x_min
             * Returns N-1, if x >= x_max, where N is the number of bins

            Args:
                x: float
                    Value
                truncate: bool
                    Return 0 if below the lower range, and N-1 if above the upper range, where N is the number of bins
                roundup: bool
                    Return lower or higher bin number, if value coincides with a bin boundary

            Returns:
                bin : int
                    Bin number
        """
        epsilon = 1E-12

        if np.ndim(x) == 0:
            scalar = True
            x = [x]
        else:
            scalar = False

        x = np.array(x)
        dx = (x_max - x_min) / bins

        dx_int = int(dx)
        if abs(dx - dx_int) < epsilon:
            dx = dx_int

        b = (x - x_min) / dx

        idx = np.logical_or(abs(b%1)<epsilon, abs(b%1-1)<epsilon)

        if roundup:
            b[idx] += epsilon
        else:
            b[idx] -= epsilon

        if truncate:
            b[b < 0] = 0
            b[b >= bins] = bins - 1
        else:
            b[b < 0] = b[b < 0] - 1

        b = b.astype(dtype=int, copy=False)

        if scalar:
            b = b[0]

        return b

    def _find_tbin(self, t, truncate=False, roundup=True):
        """ Find bin corresponding to given time.

            Returns -1, if t < t_min
            Returns N, if t > t_max, where N is the number of time bins

            Args:
                t: float
                   Time since spectrogram start in duration
                truncate: bool
                    Return 0 if below the lower range, and N-1 if above the upper range, where N is the number of bins
                roundup: bool
                    Return lower or higher bin number, if value coincides with a bin boundary

            Returns:
                bin : int
                    Bin number
        """
        tmax = self.tmin + self.tbins() * self.tres
        bin = self._find_bin(x=t, bins=self.tbins(), x_min=self.tmin, x_max=tmax, truncate=truncate, roundup=roundup)
        return bin

    def _tbin_low(self, bin):
        """ Get the lower time value of the specified time bin.

            Args:
                bin: int
                    Bin number
        """
        t = self.tmin + bin * self.tres
        return t

    def _find_fbin(self, f, truncate=False, roundup=True):
        """ Find bin corresponding to given frequency.

            Returns -1, if f < f_min.
            Returns N, if f > f_max, where N is the number of frequency bins.

            Args:
                f: float
                   Frequency in Hz 
                truncate: bool
                    Return 0 if below the lower range, and N-1 if above the upper range, where N is the number of bins
                roundup: bool
                    Return lower or higher bin number, if value coincides with a bin boundary

            Returns:
                bin: int
                     Bin number
        """
        bin = self._find_bin(x=f, bins=self.fbins(), x_min=self.fmin, x_max=self.fmax(), truncate=truncate, roundup=roundup)
        return bin

    def _fbin_low(self, bin):
        """ Get the lower frequency value of the specified frequency bin.

            Args:
                bin: int
                    Bin number
        """
        f = self.fmin + bin * self.fres
        return f

    def tbins(self):
        """ Get number of time bins

            Returns:
                n: int
                    Number of bins
        """
        n = self.image.shape[0]
        return n

    def fbins(self):
        """ Get number of frequency bins

            Returns:
                n: int
                    Number of bins
        """
        n = self.image.shape[1]
        return n

    def fmax(self):
        """ Get upper range of frequency axis

            Returns:
                fmax: float
                    Maximum frequency in Hz
        """
        fmax = self.fmin + self.fres * self.fbins()
        return fmax
        
    def duration(self):
        """ Get spectrogram duration

            Returns:
                t: float
                    Duration in seconds
        """
        t = self.tbins() * self.tres
        return t

    def get_label_vector(self, label):
        """ Get a vector indicating presence/absence (1/0) 
            of the specified annotation label for each 
            time bin.

            Args:
                label: int
                    Label of interest.

            Returns:
                y: numpy array
                    Vector of 0s and 1s with length equal to the number of 
                    time bins.
        """
        y = np.zeros(self.tbins())
        boi, _ = self._select_boxes(label)
        for b in boi:
            t1 = self._find_tbin(b[0])
            t2 = self._find_tbin(b[1], roundup=False) + 1  # include the upper bin 
            y[t1:t2] = 1

        return y

    def time_labels(self):
        """ Generates an array of labels for the time bins
            
            If the spectrogram was created with a timestamp, the labels 
            will be datetime objects.

            If the spectrogram was created without a timestamp, the labels 
            will be 't0', 't1', etc.

            Returns:
                img: list of str or datetime
                    Labels for the time bins
        """
        if self.timestamp is None:
            tax = ['t{0}'.format(t) for t in range(self.tbins())]

        else:
            tax = list()
            delta = datetime.timedelta(seconds=self.tres)
            t = self.timestamp + datetime.timedelta(seconds=self.tmin)
            for _ in range(self.tbins()):
                tax.append(t)
                t += delta
            
        return tax

    def frequency_labels(self):
        """ Generates an array of labels for the frequency bins
            
            This will return the value of the attribute flabels, or 
            simply 'f0', 'f1', etc., if this attribute was not set.

            Returns:
                img: list of str
                    Labels for the frequency bins
        """
        if self.flabels == None:
            self.flabels = ['f{0}'.format(x) for x in range(self.fbins())]
        
        return self.flabels

    def normalize(self):
        """ Normalize spectogram so that values range from 0 to 1

            Args:
                spec : numpy array
                    Spectogram to be normalized.
        """
        self.image = self.image - np.min(self.image)
        self.image = self.image / np.max(self.image)

    def _crop_image(self, tlow=None, thigh=None, flow=None, fhigh=None, tpad=False, fpad=False, bin_no=False):
        """ Crop image along time axis, frequency axis, or both.
            
            If the cropping box extends beyond the boarders of the spectrogram, 
            the cropped image is the overlap of the two.
            
            In general, the cuts will not coincide with bin divisions.             
            The cropping operation includes both the lower and upper bin.

            Args:
                tlow: float
                    Lower limit of time cut, measured in duration from the beginning of the spectrogram
                thigh: float
                    Upper limit of time cut, measured in duration from the beginning of the spectrogram start 
                flow: float
                    Lower limit on frequency cut in Hz
                fhigh: float
                    Upper limit on frequency cut in Hz
                tpad: bool
                    If tlow and/or thigh extends beyond the start and/or end times of the spectrogram,
                    pad the clipped spectrogram with zeros to ensure that it covers the specified time domain.
                fpad: bool
                    If necessary, pad with zeros along the frequency axis to ensure that 
                    the extracted spectrogram had the same frequency range as the source 
                    spectrogram.
                bin_no: bool
                    Indicate if time and frequency cuts (tlow, thigh, flow, fhigh) are given in physical units (default) or 
                    bin numbers. 

            Returns:
                img: 2d numpy array
                    Cropped image
                t1: int
                    Lower time bin
                f1: int
                    Lower frequency bin
        """
        Nt = self.tbins()
        Nf = self.fbins()
        
        t1 = 0
        t2 = Nt
        f1 = 0
        f2 = Nf

        if tlow is not None: 
            if bin_no:
                t1 = tlow
            else:
                t1 = self._find_tbin(tlow, truncate=False)
        if thigh is not None: 
            if bin_no:
                t2 = thigh
            else:
                t2 = self._find_tbin(thigh, truncate=False, roundup=False) + 1 # when cropping, include upper bin
        if flow is not None: 
            if bin_no:
                f1 = flow
            else:            
                f1 = self._find_fbin(flow, truncate=False)
        if fhigh is not None: 
            if bin_no:
                f2 = fhigh
            else:                        
                f2 = self._find_fbin(fhigh, truncate=False, roundup=False) + 1 # when cropping, include upper bin
            
        if t2 <= t1:
            img = None
        
        else:
            
            if tpad:
                Nt_crop = t2 - t1
            else:
                Nt_crop = min(t2, Nt) - max(t1, 0)

            if fpad:
                Nf_crop = self.image.shape[1]
            else:
                Nf_crop = min(f2, Nf) - max(f1, 0)
            
            if Nt_crop <= 0 or Nf_crop <= 0:
                img = None
                f1r = max(f1, 0)
            else:
                if np.ma.is_masked(self.image):
                    img = np.ma.zeros(shape=(Nt_crop, Nf_crop))
                else:
                    img = np.zeros(shape=(Nt_crop, Nf_crop))

                t1r = max(t1, 0)
                t2r = min(t2, Nt)
                t1_crop = max(-1*t1, 0)
                t2_crop = t1_crop + t2r - t1r

                f1r = max(f1, 0)
                f2r = min(f2, Nf)
                f1_crop = 0
                f2_crop = f2r - f1r

                img[t1_crop:t2_crop, f1_crop:f2_crop] = self.image[t1r:t2r, f1r:f2r]

        return img, t1, f1r

    def crop(self, tlow=None, thigh=None, flow=None, fhigh=None,\
        tpad=False, fpad=False, keep_time=True, make_copy=False, bin_no=False, **kwargs):
        """ Crop spectogram along time axis, frequency axis, or both.
            
            If the cropping box extends beyond the boarders of the spectrogram, 
            the cropped spectrogram is the overlap of the two.
            
            In general, the cuts will not coincide with bin divisions.             
            The cropping operation includes both the lower and upper bin.

            Args:
                tlow: float
                    Lower limit of time cut, measured in duration from the beginning of the spectrogram
                thigh: float
                    Upper limit of time cut, measured in duration from the beginning of the spectrogram start 
                flow: float
                    Lower limit on frequency cut in Hz
                fhigh: float
                    Upper limit on frequency cut in Hz
                tpad: bool
                    If tlow and/or thigh extends beyond the start and/or end times of the spectrogram,
                    pad the clipped spectrogram with zeros to ensure that it covers the specified time domain.
                fpad: bool
                    If necessary, pad with zeros along the frequency axis to ensure that 
                    the extracted spectrogram had the same frequency range as the source 
                    spectrogram.
                keep_time: bool
                    Keep the existing time axis. If false, the time axis will be shifted so t=0 corresponds to 
                    the first bin of the cropped spectrogram.
                make_copy: bool
                    Do not modify the present instance, but make a copy instead and applying the cropping operation to this copy
                bin_no: bool
                    Indicate if time and frequency cuts (tlow, thigh, flow, fhigh) are given in physical units (default) or 
                    bin numbers. 

            Returns:
                spec: Spectrogram
                    Cropped spectrogram, empy unless make_copy is True

            Examples: 
                >>> # create an audio signal
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> s = AudioSignal.morlet(rate=1000, frequency=300, width=1)
                >>> # compute the spectrogram
                >>> from ketos.audio_processing.spectrogram import Spectrogram
                >>> spec = MagSpectrogram(s, winlen=0.6, winstep=0.2)
                >>> # add an annotation
                >>> spec.annotate(labels=1, boxes=[1.5,4.5,250,350])
                >>> # show the spectrogram with the annotation that has label=1
                >>> fig = spec.plot(label=1)
                >>> fig.savefig("ketos/tests/assets/tmp/spec_orig.png")
                
                .. image:: ../../../../ketos/tests/assets/tmp/spec_orig.png
                
                >>> # now crop the spectrogram in time and frequency and display the result
                >>> spec.crop(tlow=2.1, thigh=5.6, flow=275, fhigh=406, keep_time=True)
                >>> fig = spec.plot(label=1)
                >>> fig.savefig("ketos/tests/assets/tmp/spec_cropped.png")

                .. image:: ../../../../ketos/tests/assets/tmp/spec_cropped.png

        """
        if make_copy:
            spec = self.copy()
        else:
            spec = self

        if bin_no:
            t1 = self._tbin_low(tlow)
            t2 = self._tbin_low(thigh)
            f1 = self._fbin_low(flow)
            f2 = self._fbin_low(fhigh)
        else:
            t1 = tlow
            t2 = thigh
            f1 = flow
            f2 = fhigh

        # if padding exceeds 'tpadmax' return None
        if tpad and 'tpadmax' in kwargs.keys():
            tmax = spec.duration() + spec.tmin
            pad_high = max(t2 - tmax, 0)
            pad_low = max(spec.tmin - t1, 0)
            padding = (pad_low + pad_high) / (t2 - t1)
            if padding > kwargs['tpadmax']:
                spec = None
                return spec

        # crop labels and boxes
        spec.labels, spec.boxes = spec.get_cropped_annotations(t1=t1, t2=t2, f1=f1, f2=f2)

        # handle time vector, file vector and file dict
        spec.time_vector, spec.file_vector, spec.file_dict = spec._crop_tracking_data(tlow, thigh, tpad=tpad, bin_no=bin_no)

        # crop image
        spec.image, tbin1, fbin1 = spec._crop_image(tlow, thigh, flow, fhigh, tpad=tpad, fpad=fpad, bin_no=bin_no)

        # update frequency axis
        if not fpad:
            spec.fmin += spec.fres * fbin1

        # update time axis
        if keep_time: 
            spec.tmin += spec.tres * tbin1
        else:
            dt = spec.tmin + spec.tres * tbin1
            spec.tmin = 0
            spec._shift_annotations(-dt)      

        # handle flabels
        if spec.flabels != None:
            if not fpad:
                spec.flabels = spec.flabels[fbin1:fbin1+spec.image.shape[1]]

        if make_copy:
            return spec

    def extract(self, label, min_length=None, center=False, fpad=False, keep_time=False, make_copy=False):
        """ Extract those segments of the spectrogram where the specified label occurs. 

            After the selected segments have been extracted, the present instance contains the 
            remaining part of the spectrogram.

            If nothing remains, the image attribute of the present instance will be None

            Args:
                label: int
                    Annotation label of interest. 
                min_length: float
                    If necessary, extend the annotation boxes so that all extracted 
                    segments have a duration of at least min_length (in seconds) or 
                    longer.  
                center: bool
                    Place the annotation box at the center of the extracted segment 
                    (instead of placing it randomly).                     
                fpad: bool
                    If necessary, pad with zeros along the frequency axis to ensure that 
                    the extracted segments have the same frequency range as the source 
                    spectrogram.
                keep_time: bool
                    If True, the extracted segments keep the time from the present instance. 
                    If False, the time axis of each extracted segment starts at t=0
                make_copy: bool
                    If true, the present instance is unaffected by the extraction operation.

            Returns:
                specs: list(Spectrogram)
                    List of clipped spectrograms.       

            Example:         
                >>> # create an audio signal
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> s = AudioSignal.morlet(rate=1000, frequency=300, width=1)
                >>> # compute the spectrogram
                >>> from ketos.audio_processing.spectrogram import Spectrogram
                >>> spec = MagSpectrogram(s, winlen=0.6, winstep=0.2)
                >>> # add an annotation
                >>> spec.annotate(labels=1, boxes=[1.5,4.5,250,350])
                >>> # show the spectrogram with the annotation that has label=1
                >>> fig = spec.plot(label=1)
                >>> fig.savefig("ketos/tests/assets/tmp/spec_orig.png")
                
                .. image:: ../../../../ketos/tests/assets/tmp/spec_orig.png
                
                >>> # extract the annotated region of the spectrogram
                >>> roi = spec.extract(label=1, keep_time=True)
                >>> # display the extracted region and what is left
                >>> fig = roi[0].plot()
                >>> fig.savefig("ketos/tests/assets/tmp/spec_extracted.png")
                >>> fig = spec.plot()
                >>> fig.savefig("ketos/tests/assets/tmp/spec_left.png")

                .. image:: ../../../../ketos/tests/assets/tmp/spec_extracted.png

                .. image:: ../../../../ketos/tests/assets/tmp/spec_left.png

        """
        if make_copy:
            s = self.copy()
        else:
            s = self

        # select boxes of interest
        boi, idx = s._select_boxes(label)

        # stretch to achieve minimum length, if necessary
        boi = s._stretch(boxes=boi, min_length=min_length, center=center)

        # extract
        res = s._clip(boxes=boi, fpad=fpad, keep_time=keep_time)

        # remove extracted labels
        s.delete_annotations(idx)
        
        return res

    def segment(self, number=1, length=None, pad=False, keep_time=False, make_copy=False, progress_bar=False, overlap=None, **kwargs):
        """ Split the spectrogram into a number of equally long segments, 
            either by specifying number of segments or segment duration.

            Args:
                number: int
                    Number of segments.
                length: float
                    Duration of each segment in seconds (only applicable if number=1)
                pad: bool
                    If True, pad spectrogram with zeros if necessary to ensure 
                    that bins are used.
                keep_time: bool
                    If True, the extracted segments keep the time from the present instance. 
                    If False, the time axis of each extracted segment starts at t=0
                make_copy: bool
                    If true, the present instance is unaffected by the extraction operation.
                progress_bar: bool
                    Option to display progress bar. Default is False.
                overlap: float [0,1]
                    This parameter can be used to create overlapping segments. Its value gives the 
                    fractional overlap of segments. E.g. overlap=0.8 will result in segments having 
                    80% overlap. Only applicable if 'length' is specified. 

            Returns:
                segs: list
                    List of segments

            Example:
                >>> # create an audio signal
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> s = AudioSignal.morlet(rate=1000, frequency=300, width=1, dfdt=10)
                >>> # compute the spectrogram
                >>> from ketos.audio_processing.spectrogram import MagSpectrogram
                >>> spec = MagSpectrogram(s, winlen=0.6, winstep=0.2)
                >>> # split the spectrogram into three equally long segments
                >>> segs = spec.segment(number=3, keep_time=True)
                >>> # display the segments
                >>> fig = segs[0].plot()
                >>> fig.savefig("ketos/tests/assets/tmp/segs_1.png")
                >>> fig = segs[1].plot()
                >>> fig.savefig("ketos/tests/assets/tmp/segs_2.png")
                >>> fig = segs[2].plot()
                >>> fig.savefig("ketos/tests/assets/tmp/segs_3.png")

                .. image:: ../../../../ketos/tests/assets/tmp/segs_1.png

                .. image:: ../../../../ketos/tests/assets/tmp/segs_2.png

                .. image:: ../../../../ketos/tests/assets/tmp/segs_3.png

        """
        do_overlap = False

        if make_copy:
            spec = self.copy()
        else:
            spec = self

        if pad:
            f = np.ceil
        else:
            f = np.floor

        if number > 1:
            bins = int(f(spec.tbins() / number))
            bins1 = bins
        
        elif length is not None and length != self.duration():
            bins = int(np.ceil(length / spec.tres))
            number = int(f(spec.tbins() / bins))
            bins1 = bins

            if overlap is not None and pad is False:
                winstep = int((1-overlap) * bins)
                number = int(np.floor((spec.tbins()-bins) / winstep)) + 1
                bins1 = winstep
                do_overlap = True

        elif length == self.duration():
            return [spec]

        t1 = np.arange(number, dtype=int) * bins1
        t2 = t1 + bins
        boxes = np.array([t1,t2])
        boxes = np.swapaxes(boxes, 0, 1)
        boxes = np.pad(boxes, ((0,0),(0,1)), mode='constant', constant_values=0)
        boxes = np.pad(boxes, ((0,0),(0,1)), mode='constant', constant_values=spec.fbins())

        segs = spec._clip(boxes=boxes, keep_time=keep_time, tpad=pad, bin_no=True, make_copy=do_overlap, progress_bar=progress_bar, **kwargs)
        
        return segs

    def _select_boxes(self, label):
        """ Select boxes corresponding to a specified label.

            Args:
                label: int
                    Label of interest

            Returns:
                res: list
                    Selected boxes
                idx: list
                    Indices of selected boxes
        """  
        res, idx = list(), list()
        if len(self.labels) == 0:
            return res, idx

        for i, (b, l) in enumerate(zip(self.boxes, self.labels)):
            if l == label:
                res.append(b)
                idx.append(i)

        return res, idx

    def _stretch(self, boxes, min_length, center=False):
        """ Stretch boxes to ensure that all have a minimum length.

            Args:
                boxes: list
                    Input boxes
                min_length: float
                    Minimum time length of each box
                center: bool
                    If True, box is stretched equally on both sides.
                    If False, the distribution of stretch is random.

            Returns:
                res: list
                    stretchted boxes
        """ 
        if min_length is None:
            return boxes

        res = list()
        for b in boxes:
            b = b.copy()
            t1 = b[0]
            t2 = b[1]
            dt = min_length - (t2 - t1)
            if dt > 0:
                if center:
                    r = 0.5001
                else:
                    r = np.random.random_sample()
                t1 -= r * dt
                t2 += (1-r) * dt
                if t1 < 0:
                    t2 -= t1
                    t1 = 0

                t1 = self.tmin + np.floor((t1-self.tmin)/self.tres) * self.tres                
                t2 = self.tmin + np.floor((t2-self.tmin)/self.tres) * self.tres                

            b[0] = t1
            b[1] = t2
            res.append(b)

        return res

    def _clip(self, boxes, tpad=False, fpad=False, keep_time=False, bin_no=False, progress_bar=False, make_copy=False, **kwargs):
        """ Extract boxed areas from spectrogram.

            After clipping, this instance contains the remaining part of the spectrogram.
            See, however, the argument make_copy.

            Args:
                boxes: numpy array
                    2d numpy array with shape=(?,4) 
                tpad: bool
                    If box extends beyond the start and/or end times of the spectrogram,
                    pad the clipped spectrogram with zeros to ensure that it has the same 
                    duration as the box.
                fpad: bool
                    If necessary, pad with zeros along the frequency axis to ensure that 
                    the extracted spectrogram has the same frequency range as the source 
                    spectrogram.
                keep_time: bool
                    If True, the extracted segments keep the time from the present instance. 
                    If False, the time axis of each extracted segment starts at t=0
                bin_no: bool
                    Indicate if boxes are given in physical units (default) or 
                    bin numbers. 
                progress_bar: bool
                    Option to display progress bar. Default is False.
                make_copy: bool
                    If True, this instance is unaffected by the clipping.

            Returns:
                specs: list(Spectrogram)
                    List of clipped spectrograms.                
        """
        if boxes is None or len(boxes) == 0:
            return list()

        if np.ndim(boxes) == 1:
            boxes = [boxes]

        # sort boxes in chronological order
        boxes = sorted(boxes, key=lambda box: box[0])

        boxes = np.array(boxes)
        N = boxes.shape[0]

        tlow = boxes[:,0]
        thigh = boxes[:,1]
        flow = boxes[:,2]
        fhigh = boxes[:,3]

        # loop over boxes
        specs = list()
        for i in tqdm(range(N), disable = not progress_bar):
            spec = self.crop(tlow=tlow[i], thigh=thigh[i], flow=flow[i], fhigh=fhigh[i],\
                tpad=tpad, fpad=fpad, keep_time=keep_time, make_copy=True, bin_no=bin_no, **kwargs)
            
            if spec is not None:
                specs.append(spec)

        if not make_copy:

            # convert from time to bin numbers
            if bin_no:
                t1 = tlow
                t2 = thigh
            else:
                t1 = self._find_tbin(tlow, truncate=True) 
                t2 = self._find_tbin(thigh, truncate=True, roundup=False) + 1 # when cropping, include upper bin

            # complement
            t2 = np.insert(t2, 0, 0)
            t1 = np.append(t1, self.tbins())
            t2max = 0
            for i in range(len(t1)):
                t2max = max(t2[i], t2max)

                if t2max <= t1[i]:
                    if t2max == 0:
                        img_c = self.image[t2max:t1[i]]
                        time_vector = self.time_vector[t2max:t1[i]]
                        file_vector = self.file_vector[t2max:t1[i]]
                    else:
                        img_c = np.append(img_c, self.image[t2max:t1[i]], axis=0)
                        time_vector = np.append(time_vector, self.time_vector[t2max:t1[i]])
                        file_vector = np.append(file_vector, self.file_vector[t2max:t1[i]])

            if img_c.shape[0] == 0:
                img_c = None

            self.image = img_c
            self.time_vector = time_vector
            self.file_vector = file_vector
            self.tmin = 0

        return specs

    def tonal_noise_reduction(self, method='MEDIAN', **kwargs):
        """ Reduce continuous tonal noise produced by e.g. ships and slowly varying background noise

            Currently, offers the following two methods:

                1. MEDIAN: Subtracts from each row the median value of that row.
                
                2. RUNNING_MEAN: Subtracts from each row the running mean of that row.
                
            The running mean is computed according to the formula given in Baumgartner & Mussoline, JASA 129, 2889 (2011); doi: 10.1121/1.3562166

            Args:
                method: str
                    Options are 'MEDIAN' and 'RUNNING_MEAN'
            
            Optional args:
                time_constant: float
                    Time constant used for the computation of the running mean (in seconds).
                    Must be provided if the method 'RUNNING_MEAN' is chosen.

            Example:
                >>> # read audio file
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> aud = AudioSignal.from_wav('ketos/tests/assets/grunt1.wav')
                >>> # compute the spectrogram
                >>> from ketos.audio_processing.spectrogram import MagSpectrogram
                >>> spec = MagSpectrogram(aud, winlen=0.2, winstep=0.02, decibel=True)
                >>> # keep only frequencies below 800 Hz
                >>> spec.crop(fhigh=800)
                >>> # show spectrogram as is
                >>> fig = spec.plot()
                >>> fig.savefig("ketos/tests/assets/tmp/spec_before_tonal.png")
                >>> # tonal noise reduction
                >>> spec.tonal_noise_reduction()
                >>> # show modified spectrogram
                >>> fig = spec.plot()
                >>> fig.savefig("ketos/tests/assets/tmp/spec_after_tonal.png")

                .. image:: ../../../../ketos/tests/assets/tmp/spec_before_tonal.png

                .. image:: ../../../../ketos/tests/assets/tmp/spec_after_tonal.png

        """
        if method is 'MEDIAN':
            self.image = self.image - np.median(self.image, axis=0)
        
        elif method is 'RUNNING_MEAN':
            assert 'time_constant' in kwargs.keys(), 'method RUNNING_MEAN requires time_constant input argument'
            self.image = self._tonal_noise_reduction_running_mean(kwargs['time_constant'])

        else:
            print('Invalid tonal noise reduction method:',method)
            print('Available options are: MEDIAN, RUNNING_MEAN')
            print('Spectrogram is unchanged')

    def _tonal_noise_reduction_running_mean(self, time_constant):
        """ Reduce continuous tonal noise produced by e.g. ships and slowly varying background noise 
            by subtracting from each row a running mean, computed according to the formula given in 
            Baumgartner & Mussoline, Journal of the Acoustical Society of America 129, 2889 (2011); doi: 10.1121/1.3562166

            Args:
                time_constant: float
                    Time constant used for the computation of the running mean (in seconds).

            Returns:
                new_img : 2d numpy array
                    Corrected spetrogram image
        """
        dt = self.tres
        T = time_constant
        eps = 1 - np.exp((np.log(0.15) * dt / T))
        nx, ny = self.image.shape
        rmean = np.average(self.image, axis=0)
        new_img = np.zeros(shape=(nx,ny))
        for ix in range(nx):
            new_img[ix,:] = self.image[ix,:] - rmean # subtract running mean
            rmean = (1 - eps) * rmean + eps * self.image[ix,:] # update running mean

        return new_img

    def average(self, axis=None, tlow=None, thigh=None, flow=None, fhigh=None):
        """ Compute average magnitude within specified time and frequency regions.
            
            If the region extends beyond the boarders of the spectrogram, 
            only the overlap region is used for the computation.

            If there is no overlap, NaN is returned.

            Args:
                axis: bool
                    Axis along which average is computed, where 0 is the time axis and 1 is the frequency axis. If axis=None, the average is computed along both axes.
                tlow: float
                    Lower limit of time cut, measured in duration from the beginning of the spectrogram
                thigh: float
                    Upper limit of time cut, measured in duration from the beginning of the spectrogram start 
                flow: float
                    Lower limit on frequency cut in Hz
                fhigh: float
                    Upper limit on frequency cut in Hz

            Returns:
                avg : float or numpy array
                    Average magnitude
        """
        m, _, _ = self._crop_image(tlow, thigh, flow, fhigh)

        if m is None or m.size == 0: 
            return np.nan

        if np.ma.is_masked(m):
            avg = np.ma.average(m, axis=axis)
        else:
            avg = np.average(m, axis=axis)

        return avg

    def median(self, axis=None, tlow=None, thigh=None, flow=None, fhigh=None):
        """ Compute median magnitude within specified time and frequency regions.
            
            If the region extends beyond the boarders of the spectrogram, 
            only the overlap region is used for the computation.

            If there is no overlap, NaN is returned.

            Args:
                axis: bool
                    Axis along which median is computed, where 0 is the time axis and 1 is the frequency axis. If axis=None, the average is computed along both axes.
                tlow: float
                    Lower limit of time cut, measured in duration from the beginning of the spectrogram
                thigh: float
                    Upper limit of time cut, measured in duration from the beginning of the spectrogram start 
                flow: float
                    Lower limit on frequency cut in Hz
                fhigh: float
                    Upper limit on frequency cut in Hz

            Returns:
                med : float or numpy array
                    Median magnitude
        """
        m, _, _ = self._crop_image(tlow, thigh, flow, fhigh)

        if m is None or m.size == 0: 
            return np.nan

        if np.ma.is_masked(m):
            med = np.ma.median(m, axis=axis)
        else:
            med = np.median(m, axis=axis)

        return med
            
    def blur_gaussian(self, tsigma, fsigma):
        """ Blur the spectrogram using a Gaussian filter.

            This uses the Gaussian filter method from the scipy.ndimage package:
            
                https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html

            Args:
                tsigma: float
                    Gaussian kernel standard deviation along time axis. Must be strictly positive.
                fsigma: float
                    Gaussian kernel standard deviation along frequency axis.

            Examples:
            
            >>> from ketos.audio_processing.spectrogram import Spectrogram
            >>> from ketos.audio_processing.audio import AudioSignal
            >>> import matplotlib.pyplot as plt
            >>> # create audio signal
            >>> s = AudioSignal.morlet(rate=1000, frequency=300, width=1)
            >>> # create spectrogram
            >>> spec = MagSpectrogram(s, winlen=0.2, winstep=0.05)
            >>> # show image
            >>> spec.plot()
            <Figure size 640x480 with 2 Axes>
            
            >>> plt.show()
            >>> # apply very small amount (0.01 sec) of horizontal blur
            >>> # and significant amount of vertical blur (30 Hz)  
            >>> spec.blur_gaussian(tsigma=0.01, fsigma=30)
            >>> # show blurred image
            >>> spec.plot()
            <Figure size 640x480 with 2 Axes>

            >>> plt.show()
            
            .. image:: ../../_static/morlet_spectrogram.png

            .. image:: ../../_static/morlet_spectrogram_blurred.png

        """
        assert tsigma > 0, "tsigma must be strictly positive"

        if fsigma < 0:
            fsigma = 0
        
        sigmaX = tsigma / self.tres
        sigmaY = fsigma / self.fres
        
        self.image = ndimage.gaussian_filter(input=self.image, sigma=(sigmaX,sigmaY))

    def enhance(self, img, a=1, b=1):
        """ Enhance regions of high intensity while suppressing regions of low intensity.

            See :func:`utils.morlet_func`

            Args:
                img : numpy array
                    Image to be processed. 
                a: float
                    Parameter determining which regions of the image will be considered "high intensity" 
                    and which regions will be considered "low intensity".
                b: float
                    Parameter determining how sharpen the transition from "low intensity" to "high intensity" is.

            Example:

        """
        self.image = enhance_image(self.image, a=a, b=b)
    
    def add(self, spec, delay=0, scale=1, make_copy=False, smooth=False, keep_time=False, t_scale=1, f_scale=1, **kwargs):
        """ Add another spectrogram on top of this spectrogram.

            Meta-data (e.g. annotations) will also be added.

            The spectrograms must have the same time and frequency resolution.
            The output spectrogram always has the same dimensions (time x frequency) as the original spectrogram.

            Args:
                spec: Spectrogram
                    Spectrogram to be added
                delay: float
                    Shift the spectrograms by this many seconds
                scale: float
                    Scaling factor for spectrogram to be added 
                make_copy: bool
                    Make a copy of the spectrogram that is being added, so that the instance provided as input argument 
                    to the method is unchanged.       
                smooth: bool
                    Smoothen the edges of the spectrogram that is being added.
                keep_time: bool
                    If True, the extracted segments keep the time from the present instance. 
                    If False, the time axis of each extracted segment starts at t=0
                t_scale: float
                    Scale the time axis of the spectrogram that is being added by this factor
                f_scale: float
                    Scale the frequency axis of the spectrogram that is being added by this factor

            Optional args:
                smooth_par: int
                    This parameter can be used to control the amount of smoothing.
                    A value of 1 gives the largest effect. The larger the value, the smaller 
                    the effect.

            Example:
                >>> # read audio file
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> aud = AudioSignal.from_wav('ketos/tests/assets/grunt1.wav')
                >>> # compute the spectrogram
                >>> from ketos.audio_processing.spectrogram import MagSpectrogram
                >>> spec = MagSpectrogram(aud, winlen=0.2, winstep=0.02, decibel=True)
                >>> # keep only frequencies below 800 Hz
                >>> spec.crop(fhigh=800)
                >>> # make a copy
                >>> spec_copy = spec.copy()
                >>> # perform tonal noise reduction on copied spectrogram and crop time
                >>> spec_copy.tonal_noise_reduction()
                >>> spec_copy.crop(tlow=0.9, thigh=1.7)
                >>> # show orignal spectrogram
                >>> fig = spec.plot()
                >>> fig.savefig("ketos/tests/assets/tmp/grunt1_orig.png")
                >>> # place the tonal-noise-corrected and cropped spectrogram on top of 
                >>> # the original spectrogram, shifted by 1.8 seconds
                >>> spec.add(spec_copy, delay=1.8)
                >>> fig = spec.plot()
                >>> fig.savefig("ketos/tests/assets/tmp/grunt1_added.png")

                .. image:: ../../../../ketos/tests/assets/tmp/grunt1_orig.png

                .. image:: ../../../../ketos/tests/assets/tmp/grunt1_added.png

        """
        assert self.tres == spec.tres, 'It is not possible to add spectrograms with different time resolutions'
        assert self.fres == spec.fres, 'It is not possible to add spectrograms with different frequency resolutions'

        # make copy
        if make_copy:
            sp = spec.copy()
        else:
            sp = spec

        # stretch/squeeze
        sp._scale_time_axis(scale=t_scale, preserve_shape=False)
        sp._scale_freq_axis(scale=f_scale, preserve_shape=True)

        # crop spectrogram
        if delay < 0:
            tlow = sp.tmin - delay
        else:
            tlow = sp.tmin
        thigh = sp.tmin + self.duration() - delay  

        sp.crop(tlow, thigh, self.fmin, self.fmax(), keep_time=keep_time)

        # fade-in/fade-out
        if smooth:

            smooth_par = 5
            if 'smooth_par' in kwargs.keys():
                smooth_par = kwargs['smooth_par']

            sigmas = 3
            p = 2 * np.ceil(smooth_par)
            nt = sp.tbins()
            if nt % 2 == 0:
                mu = nt / 2.
            else:
                mu = (nt - 1) / 2
            sigp = np.power(mu, p) / np.power(sigmas, 2)
            t = np.arange(nt)
            envf = np.exp(-np.power(t-mu, p) / (2 * sigp)) # envelop function = exp(-x^p/2*a^p)
            for i in range(sp.fbins()):
                sp.image[:,i] *= envf # multiply rows by envelope function

        # add
        nt = sp.tbins()
        nf = sp.fbins()
        t1 = self._find_tbin(self.tmin + delay)
        f1 = self._find_fbin(sp.fmin)
        self.image[t1:t1+nt,f1:f1+nf] += scale * sp.image

        # add annotations
        sp._shift_annotations(delay=delay)
        self.annotate(labels=sp.labels, boxes=sp.boxes)

        n = self.image.shape[0]
        self.time_vector = self.tmin + self.tres * np.arange(n)
        self.file_vector = np.zeros(n)
        self.file_dict = {0: 'fake'}

    def _scale_time_axis(self, scale, preserve_shape=True):
        """ Scale the spectrogram's time axis by a constant factor

            If preserve_shape is False, this operation simply stretches (scale > 1)
            or squeezes (scale < 1) the spectrogram lengthwise (i.e. along the time axis) 
            by the specified scale factor.  

            If preserve_shape is True, the effect of this operation is to stretch or 
            squeeze the spectrogram lengthwise by the specified scale factor, then

                i) if stretched, remove the section that extends beyond the original length
                ii) if squeezed, extend the spectrogram so that its length matches that of 
                the original spectrogram by appending to it part of the original spectrogram

            Args:
                scale: float
                    Scaling factor
                preserve_shape: bool
                    If True, the time axis will have the same length after rescaling as it had before.
                    If False, the length will change.

        """
        flip_pad = False

        if scale == 1:
            return
        
        else:
            n = self.image.shape[0]
            scaled_image = rescale(self.image, (scale, 1), anti_aliasing=True, multichannel=False)
            dn = n - scaled_image.shape[0]

            if not preserve_shape:
                self.image = scaled_image

            else:
                if dn < 0:
                    self.image = scaled_image[:n,:]
                
                elif dn > 0:
                    pad = self.image[n-dn:,:]
                    if flip_pad: 
                        pad = np.flip(pad, axis=0)
                    
                    self.image = np.concatenate((scaled_image, pad), axis=0)

                assert self.image.shape[0] == n, 'Ups. Something went wrong while attempting to rescale the time axis.'                

        # update annotations
        self._scale_annotations(scale)

    def _scale_freq_axis(self, scale, preserve_shape=True):
        """ Scale the spectrogram's frequency axis by a constant factor

            If preserve_shape is False, this operation simply stretches (scale > 1)
            or squeezes (scale < 1) the spectrogram heightwise (i.e. along the frequency axis) 
            by the specified scale factor.  

            If preserve_shape is True, the effect of this operation is to stretch or 
            squeeze the spectrogram heightwise by the specified scale factor, then

                i) if stretched, remove the section that extends beyond the original height
                ii) if squeezed, extend the spectrogram so that its height matches that of 
                the original spectrogram by appending to it part of the original spectrogram

            Args:
                scale: float
                    Scaling factor
                preserve_shape: bool
                    If True, the time axis will have the same height after rescaling as it had before.
                    If False, the height will change.

        """
        pad_with_gaussian_noise = False
        flip_pad = False

        if scale == 1:
            return
        
        else:
            n = self.image.shape[1]
            scaled_image = rescale(self.image, (1, scale), anti_aliasing=True, multichannel=False, mode='constant')
            dn = n - scaled_image.shape[1]

            if not preserve_shape:
                self.image = scaled_image

            else:
                if dn < 0:
                    self.image = scaled_image[:,:n]
                
                elif dn > 0:
                    pad = self.image[:,n-dn:]
                    if flip_pad: 
                        pad = np.flip(pad, axis=1)

                    if pad_with_gaussian_noise:
                        mean = np.mean(self.image, axis=1)
                        std = np.std(self.image, axis=1)
                        pad = np.zeros(shape=(self.image.shape[0],dn))
                        for i, (m,s) in enumerate(zip(mean, std)):
                            pad[i,:] = np.random.normal(loc=m, scale=s, size=(1,dn))

                    # pad image
                    self.image = np.concatenate((scaled_image, pad), axis=1)

                assert self.image.shape[1] == n, 'Ups. Something went wrong while attempting to rescale the frequency axis.'                

    def append(self, spec):
        """ Append another spectrogram to this spectrogram.

            Includes any meta-data associated with the spectrogram (e.g. annotations).

            The spectrograms must have the same time and frequency resolutions and share the same frequency range.

            Args:
                spec: Spectrogram
                    Spectrogram to be appended
        """
        assert self.tres == spec.tres, 'It is not possible to append spectrograms with different time resolutions'
        assert self.fres == spec.fres, 'It is not possible to append spectrograms with different frequency resolutions'

        assert np.all(self.image.shape[1] == spec.image.shape[1]), 'It is not possible to add spectrograms with different frequency range'

        # add annotations
        spec._shift_annotations(delay=self.duration())
        self.annotate(labels=spec.labels, boxes=spec.boxes)

        # add time and file info
        self.time_vector = np.append(self.time_vector, spec.time_vector)

        # join dictionaries
        new_keys = {}
        for it in spec.file_dict.items():
            key = it[0]
            value = it[1]
            if value not in self.file_dict.values():
                n = len(self.file_dict)
                self.file_dict[n] = value
                new_keys[key] = n
            else:
                existing_key = self._get_key(file=value)
                new_keys[key] = existing_key

        # update keys
        file_vec = list()
        for f in spec.file_vector:
            file_vec.append(new_keys[f])

        # join file vectors
        self.file_vector = np.append(self.file_vector, file_vec)

        # append image
        self.image = np.append(self.image, spec.image, axis=0)

    def _get_key(self, file):
        res = None
        for it in self.file_dict.items():
            key = it[0]
            value = it[1]
            if file == value:
                res = key

        return res

    def plot(self, label=None, pred=None, feat=None, conf=None):
        """ Plot the spectrogram with proper axes ranges and labels.

            Optionally, also display selected label, binary predictions, features, and confidence levels.

            All plotted quantities share the same time axis, and are assumed to span the 
            same period of time as the spectrogram.

            Note: The resulting figure can be shown (fig.show())
            or saved (fig.savefig(file_name))

            Args:
                spec: Spectrogram
                    spectrogram to be plotted
                label: int
                    Label of interest
                pred: 1d array
                    Binary prediction for each time bin in the spectrogram
                feat: 2d array
                    Feature vector for each time bin in the spectrogram
                conf: 1d array
                    Confidence level of prediction for each time bin in the spectrogram
            
            Returns:
            fig: matplotlib.figure.Figure
            A figure object.

            Example:
                >>> # extract saved spectrogram from database file
                >>> import tables
                >>> import ketos.data_handling.database_interface as di
                >>> db = tables.open_file("ketos/tests/assets/cod.h5", "r") 
                >>> table = di.open_table(db, "/sig") 
                >>> spectrogram = di.load_specs(table)[0]
                >>> db.close()
                >>> 
                >>> # plot the spectrogram and label '1'
                >>> import matplotlib.pyplot as plt
                >>> fig = spectrogram.plot(label=1)
                >>> plt.show()
        """
        nrows = 1
        if (label is not None): 
            nrows += 1
        if (pred is not None): 
            nrows += 1
        if (feat is not None): 
            nrows += 1
        if (conf is not None): 
            nrows += 1

        if nrows == 1:
            figsize=(6.4, 4.8)
        else:
            figsize=(8, 1+1.5*nrows)            
        
        fig, ax = plt.subplots(nrows=nrows, ncols=1, figsize=figsize, sharex=True)

        if nrows == 1:
            ax0 = ax
        else:
            ax0 = ax[-1]

        t1 = self.tmin
        t2 = self.tmin+self.duration()

        # spectrogram
        x = self.image
        img_plot = ax0.imshow(x.T, aspect='auto', origin='lower', extent=(t1, t2, self.fmin, self.fmax()))
        ax0.set_xlabel('Time (s)')
        ax0.set_ylabel('Frequency (Hz)')
        fig.colorbar(img_plot, ax=ax0, format='%+2.0f dB')

        row = -2

        # labels
        if label is not None:
            labels = self.get_label_vector(label)
            n = len(labels)
            t_axis = np.arange(n, dtype=float)
            dt = self.duration() / n
            t_axis *= dt 
            t_axis += 0.5 * dt + self.tmin
            ax[row].plot(t_axis, labels, color='C1')
            ax[row].set_xlim(t1, t2)
            ax[row].set_ylim(-0.1, 1.1)
            ax[row].set_ylabel('label')
            fig.colorbar(img_plot, ax=ax[row]).ax.set_visible(False)
            row -= 1

        # predictions
        if pred is not None:
            n = len(pred)
            t_axis = np.arange(n, dtype=float)
            dt = self.duration() / n
            t_axis *= dt 
            t_axis += 0.5 * dt + self.tmin
            ax[row].plot(t_axis, pred, color='C2')
            ax[row].set_xlim(t1, t2)
            ax[row].set_ylim(-0.1, 1.1)
            ax[row].set_ylabel('prediction')
            fig.colorbar(img_plot, ax=ax[row]).ax.set_visible(False)  
            row -= 1

        # feat
        if feat is not None:
            m = np.mean(feat, axis=0)
            idx = np.argwhere(m != 0)
            idx = np.squeeze(idx)
            x = feat[:,idx]
            x = x / np.max(x, axis=0)
            img_plot = ax[row].imshow(x.T, aspect='auto', origin='lower', extent=(t1, t2, 0, 1))
            ax[row].set_ylabel('feature #')
            fig.colorbar(img_plot, ax=ax[row])
            row -= 1

        # confidence
        if conf is not None:
            n = len(conf)
            t_axis = np.arange(n, dtype=float)
            dt = self.duration() / n
            t_axis *= dt 
            t_axis += 0.5 * dt + self.tmin
            ax[row].plot(t_axis, conf, color='C3')
            ax[row].set_xlim(t1, t2)
            ax[row].set_ylim(-0.1, 1.1)
            ax[row].set_ylabel('confidence')
            fig.colorbar(img_plot, ax=ax[row]).ax.set_visible(False)  
            row -= 1

        return fig


class MagSpectrogram(Spectrogram):
    """ Magnitude Spectrogram
    
        The 0th axis is the time axis (t-axis).
        The 1st axis is the frequency axis (f-axis).
        
        Each axis is characterized by a starting value (tmin and fmin)
        and a resolution or bin size (tres and fres).

        Args:
            signal: AudioSignal
                    And instance of the :class:`audio_signal.AudioSignal` class 
            winlen: float
                Window size in seconds
            winstep: float
                Step size in seconds 
            hamming: bool
                Apply Hamming window
            NFFT: int
                Number of points for the FFT. If None, set equal to the number of samples.
            timestamp: datetime
                Spectrogram time stamp (default: None)
            flabels: list of strings
                List of labels for the frequency bins.     
            compute_phase: bool
                Compute phase spectrogram in addition to magnitude spectrogram
            decibel: bool
                Use logarithmic (decibel) scale.
            tag: str
                Identifier, typically the name of the wave file used to generate the spectrogram.
                If no tag is provided, the tag from the audio_signal will be used.
            decibel: bool
                Use logarithmic z axis
    """
    def __init__(self, audio_signal=None, winlen=None, winstep=1, timestamp=None,
                 flabels=None, hamming=True, NFFT=None, compute_phase=False, decibel=False, tag=''):

        super(MagSpectrogram, self).__init__(timestamp=timestamp, tres=winstep, flabels=flabels, tag=tag, decibel=decibel)

        if audio_signal is not None:
            self.image, self.NFFT, self.fres, self.phase_change = self.make_mag_spec(audio_signal, winlen, winstep, hamming, NFFT, timestamp, compute_phase, decibel)
            if tag is '':
                tag = audio_signal.tag

        self.file_dict, self.file_vector, self.time_vector = self._create_tracking_data(tag) 

    def make_mag_spec(self, audio_signal, winlen, winstep, hamming=True, NFFT=None, timestamp=None, compute_phase=False, decibel=False):
        """ Create magnitude spectrogram from audio signal
        
            Args:
                signal: AudioSignal
                    Audio signal 
                winlen: float
                    Window size in seconds
                winstep: float
                    Step size in seconds 
                hamming: bool
                    Apply Hamming window
                NFFT: int
                    Number of points for the FFT. If None, set equal to the number of samples.
                timestamp: datetime
                    Spectrogram time stamp (default: None)
                compute_phase: bool
                    Compute phase spectrogram in addition to magnitude spectrogram
                decibel: bool
                    Use logarithmic (decibel) scale.

            Returns:
                (image, NFFT, fres):numpy.array,int, int
                A tuple with the resulting magnitude spectrogram, the NFFT, the frequency resolution
                and the phase spectrogram (only if compute_phase=True).
        """

        image, NFFT, fres, phase_change = self._make_spec(audio_signal, winlen, winstep, hamming, NFFT, timestamp, compute_phase, decibel)
        
        return image, NFFT, fres, phase_change

    def audio_signal(self):
        """ Generate audio signal from magnitude spectrogram

            Note that the current implementation does not account for the effect of 
            the Hamming window function, nor does it take into account phase 
            information. 

            An improved implementation is planned for release 2.0.0.
            
            Returns:
                a: AudioSignal
                    Audio signal
        """
        y = np.fft.irfft(self.image)
        d = self.tres * self.fres * (y.shape[1] + 1)
        N = int(np.ceil(y.shape[0] * d))
        s = np.zeros(N)
        for i in range(y.shape[0]):
            i0 = i * d
            for j in range(0, y.shape[1]):
                k = int(np.ceil(i0 + j))
                if k < N:
                    s[k] += y[i,j]
        rate = int(np.ceil((N+1) / self.duration()))
        a = AudioSignal(rate=rate, data=s[:N])
        return a


class PowerSpectrogram(Spectrogram):
    """ Creates a Power Spectrogram from an :class:`audio_signal.AudioSignal`
    
        The 0th axis is the time axis (t-axis).
        The 1st axis is the frequency axis (f-axis).
        
        Each axis is characterized by a starting value (tmin and fmin)
        and a resolution or bin size (tres and fres).

        Args:
            signal: AudioSignal
                    And instance of the :class:`audio_signal.AudioSignal` class 
            winlen: float
                Window size in seconds
            winstep: float
                Step size in seconds 
            hamming: bool
                Apply Hamming window
            NFFT: int
                Number of points for the FFT. If None, set equal to the number of samples.
            timestamp: datetime
                Spectrogram time stamp (default: None)
            flabels:list of strings
                List of labels for the frequency bins.
            compute_phase: bool
                Compute phase spectrogram in addition to power spectrogram                        
            decibel: bool
                Use logarithmic (decibel) scale.
            tag: str
                Identifier, typically the name of the wave file used to generate the spectrogram
            decibel: bool
                Use logarithmic z axis
    """
    def __init__(self, audio_signal, winlen, winstep,flabels=None,
                 hamming=True, NFFT=None, timestamp=None, compute_phase=False, decibel=False, tag=''):

        super(PowerSpectrogram, self).__init__(timestamp=timestamp, tres=winstep, flabels=flabels, tag=tag, decibel=decibel)

        if audio_signal is not None:
            self.image, self.NFFT, self.fres, self.phase_change = self.make_power_spec(audio_signal, winlen, winstep, hamming, NFFT, timestamp, compute_phase, decibel)
            if tag is '':
                tag = audio_signal.tag

        self.file_dict, self.file_vector, self.time_vector = self._create_tracking_data(tag) 

    def make_power_spec(self, audio_signal, winlen, winstep, hamming=True, NFFT=None, timestamp=None, compute_phase=False, decibel=False):
        """ Create spectrogram from audio signal
        
            Args:
                signal: AudioSignal
                    Audio signal 
                winlen: float
                    Window size in seconds
                winstep: float
                    Step size in seconds 
                hamming: bool
                    Apply Hamming window
                NFFT: int
                    Number of points for the FFT. If None, set equal to the number of samples.
                timestamp: datetime
                    Spectrogram time stamp (default: None)
                compute_phase: bool
                    Compute phase spectrogram in addition to power spectrogram
                decibel: bool
                    Use logarithmic (decibel) scale.

            Returns:
                (power_spec, NFFT, fres, phase):numpy.array,int,int,numpy.array
                A tuple with the resulting power spectrogram, the NFFT, the frequency resolution, 
                and the phase spectrogram (only if compute_phase=True).
        """

        image, NFFT, fres, phase_change = self._make_spec(audio_signal, winlen, winstep, hamming, NFFT, timestamp, compute_phase, decibel)
        power_spec = (1.0/NFFT) * (image ** 2)
        
        return power_spec, NFFT, fres, phase_change

       
    
class MelSpectrogram(Spectrogram):
    """ Creates a Mel Spectrogram from an :class:`audio_signal.AudioSignal`
    
        The 0th axis is the time axis (t-axis).
        The 1st axis is the frequency axis (f-axis).
        
        Each axis is characterized by a starting value (tmin and fmin)
        and a resolution or bin size (tres and fres).

        Args:
            signal: AudioSignal
                    And instance of the :class:`audio_signal.AudioSignal` class 
            winlen: float
                Window size in seconds
            winstep: float
                Step size in seconds 
            hamming: bool
                Apply Hamming window
            NFFT: int
                Number of points for the FFT. If None, set equal to the number of samples.
            timestamp: datetime
                Spectrogram time stamp (default: None)
            flabels: list of strings
                List of labels for the frequency bins.
            tag: str
                Identifier, typically the name of the wave file used to generate the spectrogram
            decibel: bool
                Use logarithmic z axis
    """


    def __init__(self, audio_signal, winlen, winstep,flabels=None, hamming=True, 
                 NFFT=None, timestamp=None, tag='', decibel=False, **kwargs):

        super(MelSpectrogram, self).__init__(timestamp=timestamp, tres=winstep, flabels=flabels, tag=tag, decibel=decibel)

        if audio_signal is not None:
            self.image, self.filter_banks, self.NFFT, self.fres = self.make_mel_spec(audio_signal, winlen, winstep, hamming=hamming, NFFT=NFFT, timestamp=timestamp, **kwargs)
            if tag is '':
                tag = audio_signal.tag

        self.file_dict, self.file_vector, self.time_vector = self._create_tracking_data(tag) 


    def make_mel_spec(self, audio_signal, winlen, winstep, n_filters=40,
                         n_ceps=20, cep_lifter=20, hamming=True, NFFT=None, timestamp=None):
        """ Create a Mel spectrogram from audio signal
    
        Args:
            signal: AudioSignal
                Audio signal 
            winlen: float
                Window size in seconds
            winstep: float
                Step size in seconds 
            n_filters: int
                The number of filters in the filter bank.
            n_ceps: int
                The number of Mel-frequency cepstrums.
            cep_lifters: int
                The number of cepstum filters.
            hamming: bool
                Apply Hamming window
            NFFT: int
                Number of points for the FFT. If None, set equal to the number of samples.
            timestamp: datetime
                Spectrogram time stamp (default: None)

        Returns:
            mel_spec: numpy.array
                Array containing the Mel spectrogram
            filter_banks: numpy.array
                Array containing the filter banks
            NFFT: int
                The number of points used for creating the magnitude spectrogram
                (Calculated if not given)
            fres: int
                The calculated frequency resolution
           
        """

        image, NFFT, fres, _ = self._make_spec(audio_signal, winlen, winstep, hamming, NFFT, timestamp, decibel=False)
        power_spec = (1.0/NFFT) * (image ** 2)
        
        low_freq_mel = 0
        high_freq_mel = (2595 * np.log10(1 + (audio_signal.rate / 2) / 700))  # Convert Hz to Mel
        mel_points = np.linspace(low_freq_mel, high_freq_mel, n_filters + 2)  # Equally spaced in Mel scale
        hz_points = (700 * (10**(mel_points / 2595) - 1))  # Convert Mel to Hz
        bin = np.floor((NFFT + 1) * hz_points / audio_signal.rate)

        fbank = np.zeros((n_filters, int(np.floor(NFFT / 2 + 1))))
        for m in range(1, n_filters + 1):
            f_m_minus = int(bin[m - 1])   # left
            f_m = int(bin[m])             # center
            f_m_plus = int(bin[m + 1])    # right

            for k in range(f_m_minus, f_m):
                fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
            for k in range(f_m, f_m_plus):
                fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])

        filter_banks = np.dot(power_spec, fbank.T)
        filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)  # Numerical Stability
        filter_banks = 20 * np.log10(filter_banks)  # dB
        
        
        mel_spec = dct(filter_banks, type=2, axis=1, norm='ortho')[:, 1 : (n_ceps + 1)] # Keep 2-13
                
        (nframes, ncoeff) = mel_spec.shape
        n = np.arange(ncoeff)
        lift = 1 + (cep_lifter / 2) * np.sin(np.pi * n / cep_lifter)
        mel_spec *= lift  
        
        return mel_spec, filter_banks, NFFT, fres

    def plot(self, filter_bank=False):
        """ Plot the spectrogram with proper axes ranges and labels.

            Note: The resulting figure can be shown (fig.show())
            or saved (fig.savefig(file_name))

            Args:
                filter_bank: bool
                    Plot the filter banks if True. If false (default) print the mel spectrogram.
            
            Returns:
            fig: matplotlib.figure.Figure
            A figure object.

        """
        if filter_bank:
            img = self.filter_banks
        else:
            img = self.image

        fig, ax = plt.subplots()
        img_plot = ax.imshow(img.T,aspect='auto',origin='lower',extent=(self.tmin,self.tmin+self.duration(),self.fmin,self.fmax()))
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        if self.decibel:
            fig.colorbar(img_plot,format='%+2.0f dB')
        else:
            fig.colorbar(img_plot,format='%+2.0f')  
        return fig
