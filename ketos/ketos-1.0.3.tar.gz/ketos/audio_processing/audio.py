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

""" audio module within the ketos library

    This module provides utilities to work with audio data.

    Contents:
        AudioSignal class: 
        TimeStampedAudioSignal class
"""

import numpy as np
import datetime
import math
import scipy.io.wavfile as wave
from scipy import interpolate
from ketos.utils import morlet_func
import ketos.audio_processing.audio_processing as ap
import matplotlib.pyplot as plt
from scipy.integrate import quadrature
from scipy.stats import norm
from tqdm import tqdm
from ketos.audio_processing.annotation import AnnotationHandler
from ketos.data_handling.data_handling import read_wave
from ketos.utils import ensure_dir


class AudioSignal(AnnotationHandler):
    """ Audio signal

        Args:
            rate: float
                Sampling rate in Hz
            data: 1d numpy array
                Audio data 
            tag: str
                Meta-data string (optional)
            tstart: float
                Start time in seconds (optional)

        Attributes:
            rate: float
                Sampling rate in Hz
            data: 1d numpy array
                Audio data 
            tag: str
                Meta-data string
            tmin: float
                Start time in seconds              
            file_dict: dict
                Wave files used to generate this spectrogram
            file_vector: 1d numpy array
                Associates a particular wave file with each time bin in the spectrogram
            time_vector: 1d numpy array
                Associated a particular time within a wave file with each time bin in the spectrogram                
    """
    def __init__(self, rate, data, tag='', tstart=0):

        self.rate = float(rate)
        self.data = data.astype(dtype=np.float32)
        self.tag = tag
        self.tmin = tstart

        super(AudioSignal, self).__init__() # initialize AnnotationHandler

        n = self.data.shape[0]
        self.time_vector = (1. / self.rate) * np.arange(n) + self.tmin
        self.file_vector = np.zeros(n)
        self.file_dict = {0: tag}

    @classmethod
    def from_wav(cls, path, channel=0):
        """ Generate audio signal from wave file

            The tag attribute will be set equal to the file name.

            Args:
                path: str
                    Path to input wave file
                channel: int
                    In the case of stereo recordings, this argument is used 
                    to specify which channel to read from. Default is 0.

            Returns:
                Instance of AudioSignal
                    Audio signal from wave file

            Example:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # read audio signal from wav file
            >>> a = AudioSignal.from_wav('ketos/tests/assets/grunt1.wav')
            >>> # show signal
            >>> fig = a.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_grunt1.png")

            .. image:: ../../../../ketos/tests/assets/tmp/audio_grunt1.png

        """        
        rate, data = read_wave(file=path, channel=channel)
        return cls(rate, data, path[path.rfind('/')+1:])

    @classmethod
    def gaussian_noise(cls, rate, sigma, samples, tag=''):
        """ Generate Gaussian noise signal

            Args:
                rate: float
                    Sampling rate in Hz
                sigma: float
                    Standard deviation of the signal amplitude
                samples: int
                    Length of the audio signal given as the number of samples
                tag: str
                    Meta-data string (optional)

            Returns:
                Instance of AudioSignal
                    Audio signal sampling of Gaussian noise

            Example:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create gaussian noise with sampling rate of 10 Hz, standard deviation of 2.0 and 1000 samples
            >>> a = AudioSignal.gaussian_noise(rate=10, sigma=2.0, samples=1000)
            >>> # show signal
            >>> fig = a.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_noise.png")

            .. image:: ../../../../ketos/tests/assets/tmp/audio_noise.png

        """        
        assert sigma > 0, "sigma must be strictly positive"

        if tag == '':
            tag = "Gaussian_noise_sigma{0:.3f}".format(sigma)

        y = np.random.normal(loc=0, scale=sigma, size=samples)
        return cls(rate=rate, data=y, tag=tag)

    @classmethod
    def morlet(cls, rate, frequency, width, samples=None, height=1, displacement=0, dfdt=0, tag=''):
        """ Audio signal with the shape of the Morlet wavelet

            Uses :func:`util.morlet_func` to compute the Morlet wavelet.

            Args:
                rate: float
                    Sampling rate in Hz
                frequency: float
                    Frequency of the Morlet wavelet in Hz
                width: float
                    Width of the Morlet wavelet in seconds (sigma of the Gaussian envelope)
                samples: int
                    Length of the audio signal given as the number of samples (if no value is given, samples = 6 * width * rate)
                height: float
                    Peak value of the audio signal
                displacement: float
                    Peak position in seconds
                dfdt: float
                    Rate of change in frequency as a function of time in Hz per second.
                    If dfdt is non-zero, the frequency is computed as 
                        
                        f = frequency + (time - displacement) * dfdt 

                tag: str
                    Meta-data string (optional)

            Returns:
                Instance of AudioSignal
                    Audio signal sampling of the Morlet wavelet 

            Examples:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a Morlet wavelet with frequency of 3 Hz and 1-sigma width of envelope set to 2.0 seconds
            >>> wavelet1 = AudioSignal.morlet(rate=100., frequency=3., width=2.0)
            >>> # show signal
            >>> fig = wavelet1.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/morlet_standard.png")

            .. image:: ../../../../ketos/tests/assets/tmp/morlet_standard.png

            >>> # create another wavelet, but with frequency increasing linearly with time
            >>> wavelet2 = AudioSignal.morlet(rate=100., frequency=3., width=2.0, dfdt=0.3)
            >>> # show signal
            >>> fig = wavelet2.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/morlet_dfdt.png")

            .. image:: ../../../../ketos/tests/assets/tmp/morlet_dfdt.png

        """        
        if samples is None:
            samples = int(6 * width * rate)

        N = int(samples)

        # compute Morlet function at N equally spaced points
        dt = 1. / rate
        stop = (N-1.)/2. * dt
        start = -stop
        time = np.linspace(start, stop, N)
        y = morlet_func(time=time, frequency=frequency, width=width, displacement=displacement, norm=False, dfdt=dfdt)        
        y *= height
        
        if tag == '':
            tag = "Morlet_f{0:.0f}Hz_s{1:.3f}s".format(frequency, width) # this is just a string with some helpful info

        return cls(rate=rate, data=np.array(y), tag=tag)

    @classmethod
    def cosine(cls, rate, frequency, duration=1, height=1, displacement=0, tag=''):
        """ Audio signal with the shape of a cosine function

            Args:
                rate: float
                    Sampling rate in Hz
                frequency: float
                    Frequency of the Morlet wavelet in Hz
                duration: float
                    Duration of the signal in seconds
                height: float
                    Peak value of the audio signal
                displacement: float
                    Phase offset in fractions of 2*pi
                tag: str
                    Meta-data string (optional)

            Returns:
                Instance of AudioSignal
                    Audio signal sampling of the cosine function 

            Examples:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a Cosine wave with frequency of 7 Hz
            >>> cos = AudioSignal.cosine(rate=1000., frequency=7.)
            >>> # show signal
            >>> fig = cos.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/cosine_audio.png")

            .. image:: ../../../../ketos/tests/assets/tmp/cosine_audio.png

        """        
        N = int(duration * rate)

        # compute cosine function at N equally spaced points
        dt = 1. / rate
        stop = (N-1.)/2. * dt
        start = -stop
        time = np.linspace(start, stop, N)
        x = (time * frequency + displacement) * 2 * np.pi
        y = height * np.cos(x)
        
        if tag == '':
            tag = "cosine_f{0:.0f}Hz".format(frequency) # this is just a string with some helpful info

        return cls(rate=rate, data=np.array(y), tag=tag)

    def get_data(self):
        """ Get the underlying data contained in this object.
            
            Returns:
                self.data: numpy array
                    Data
        """
        return self.data

    def get_time_vector(self):
        """ Get the audio signal's time vector

            Returns:
                v: 1d numpy array
                    Time vector
        """
        v = self.time_vector
        return v

    def get_file_vector(self):
        """ Get the audio signal's file vector

            Returns:
                v: 1d numpy array
                    File vector
        """
        v = self.file_vector
        return v

    def get_file_dict(self):
        """ Get the audio signal's file dictionary

            Returns:
                d: dict
                    File dictionary
        """
        d = self.file_dict
        return d

    def make_frames(self, winlen, winstep, zero_padding=False):
        """ Split the signal into frames of length 'winlen' with consecutive 
            frames being shifted by an amount 'winstep'. 
            
            If 'winstep' < 'winlen', the frames overlap.

        Args: 
            signal: AudioSignal
                The signal to be framed.
            winlen: float
                The window length in seconds.
            winstep: float
                The window step (or stride) in seconds.
            zero_padding: bool
                If necessary, pad the signal with zeros at the end to make sure that all frames have equal number of samples.
                This assures that sample are not truncated from the original signal.

        Returns:
            frames: numpy array
                2-d array with padded frames.
        """
        rate = self.rate
        sig = self.data

        winlen = int(round(winlen * rate))
        winstep = int(round(winstep * rate))

        frames = ap.make_frames(sig, winlen, winstep, zero_padding)
        return frames

    def to_wav(self, path):
        """ Save audio signal to wave file

            Args:
                path: str
                    Path to output wave file
        """        
        ensure_dir(path)
        wave.write(filename=path, rate=int(self.rate), data=self.data.astype(dtype=np.int16))

    def empty(self):
        """ Check if the signal contains any data

            Returns:
                bool
                    True if the length of the data array is zero or array is None
        """  
        if self.data is None:
            return True
        elif len(self.data) == 0:
            return True
        
        return False

    def duration(self):
        """ Signal duration in seconds

            Returns:
                s: float
                   Signal duration in seconds
        """    
        s = float(len(self.data)) / float(self.rate)
        return s

    def max(self):
        """ Maximum value of the signal

            Returns:
                v: float
                   Maximum value of the data array
        """    
        v = max(self.data)
        return v

    def min(self):
        """ Minimum value of the signal

            Returns:
                v: float
                   Minimum value of the data array
        """    
        v = min(self.data)
        return v

    def std(self):
        """ Standard deviation of the signal

            Returns:
                v: float
                   Standard deviation of the data array
        """   
        v = np.std(self.data) 
        return v

    def average(self):
        """ Average value of the signal

            Returns:
                v: float
                   Average value of the data array
        """   
        v = np.average(self.data)
        return v

    def median(self):
        """ Median value of the signal

            Returns:
                v: float
                   Median value of the data array
        """   
        v = np.median(self.data)
        return v

    def plot(self):
        """ Plot the signal with proper axes ranges and labels
            
            Example:
            
            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a morlet wavelet
            >>> a = AudioSignal.morlet(rate=100, frequency=5, width=1)
            >>> # plot the wave form
            >>> fig = a.plot()

            .. image:: ../../_static/morlet.png

        """
        fig, ax = plt.subplots(nrows=1)
        start = 0.5 / self.rate
        stop = self.duration() - 0.5 / self.rate
        num = len(self.data)
        ax.plot(np.linspace(start=start, stop=stop, num=num), self.data)
        ax = plt.gca()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Signal')
        return fig

    def _selection(self, begin, end):
        """ Convert time range to sample range.

            Args:
                begin: float
                    Start time of selection window in seconds
                end: float
                    End time of selection window in seconds

            Returns:
                i1: int
                    Start sample no.
                i2: int
                    End sample no.
        """   
        i1 = 0
        i2 = len(self.data)

        if begin is not None:
            begin = max(0, begin)
            i1 = int(begin * self.rate)
            i1 = max(i1, 0)

        if end is not None:
            end = min(self.duration(), end)
            i2 = int(end * self.rate)
            i2 = min(i2, len(self.data))

        return i1, i2

    def _crop(self, i1, i2):
        """ Select a portion of the audio data

            Args:
                i1: int
                    Start bin of selection window
                end: int
                    End bin of selection window

            Returns:
                cropped_data: numpy array
                   Selected portion of the audio data
        """
        if i2 > i1:
            self.data = self.data[i1:i2] 
        else:
            self.data = None           

    def crop(self, begin=None, end=None, make_copy=False):
        """ Clip audio signal

            Args:
                begin: float
                    Start time of selection window in seconds
                end: float
                    End time of selection window in seconds
                make_copy: bool
                    Create a new instance instead of modifying the present instance

            Returns:
                cropped_signal: AudioSignal
                    None, unless make_copy is True

            Example:
            
            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a morlet wavelet
            >>> a1 = AudioSignal.morlet(rate=100, frequency=5, width=1)
            >>> # crop the first 1 second
            >>> a2 = a1.crop(end=1.0, make_copy=True)
            >>> # show the wave forms
            >>> fig = a1.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_orig.png")
            >>> fig = a2.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_cropped.png")

            .. image:: ../../../../ketos/tests/assets/tmp/audio_orig.png

            .. image:: ../../../../ketos/tests/assets/tmp/audio_cropped.png

        """ 
        if make_copy:
            x = self.copy()
        else:
            x = self

        i1, i2 = x._selection(begin, end)
        x._crop(i1, i2)

        if make_copy:
            return x

    def clip(self, boxes):
        """ Extract boxed intervals from audio signal.

            After clipping, this instance contains the remaining part of the audio signal.

            Args:
                boxes: numpy array
                    2d numpy array with shape (?,2)   

            Returns:
                segs: list(AudioSignal)
                    List of clipped audio signals.                

            Example:
            
            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a morlet wavelet
            >>> a = AudioSignal.morlet(rate=100, frequency=5, width=1)
            >>> # clip segment between 1.0-1.8 sec and again between 3.1-3.8 sec
            >>> segs = a.clip(boxes=[[1.0, 1.8],[3.1, 3.8]])
            >>> # show the wave forms
            >>> fig = a.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_whats_left.png")
            >>> fig = segs[0].plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_clip_1.png")
            >>> fig = segs[1].plot()
            >>> fig.savefig("ketos/tests/assets/tmp/audio_clip_2.png")

            .. image:: ../../../../ketos/tests/assets/tmp/audio_whats_left.png

            .. image:: ../../../../ketos/tests/assets/tmp/audio_clip_1.png

            .. image:: ../../../../ketos/tests/assets/tmp/audio_clip_2.png

        """ 

        if np.ndim(boxes) == 1:
            boxes = [boxes]

        # sort boxes in chronological order
        sorted(boxes, key=lambda box: box[0])

        boxes = np.array(boxes)
        N = boxes.shape[0]

        # get cuts
        segs = list()

        # loop over boxes
        t1, t2 = list(), list()
        for i in range(N):
            
            b = boxes[i]

            assert len(b) >= 2, "box must have dimension 2 or greater"

            begin = b[0]
            end = b[1]
            t1i, t2i = self._selection(begin, end)

            data = self.data[t1i:t2i]
            seg = AudioSignal(rate=self.rate, data=data)

            segs.append(seg)
            t1.append(t1i)
            t2.append(t2i)

        # complement
        t2 = np.insert(t2, 0, 0)
        t1 = np.append(t1, len(self.data))
        t2max = 0
        for i in range(len(t1)):
            t2max = max(t2[i], t2max)
            if t2max < t1[i]:
                if t2max == 0:
                    data_c = self.data[t2max:t1[i]]
                else:
                    data_c = np.append(data_c, self.data[t2max:t1[i]], axis=0)

        self.data = data_c
        self.tmin = 0

        return segs

    def append(self, signal, delay=None, n_smooth=0, max_length=None):
        """ Append another audio signal to this signal.

            The two audio signals must have the same samling rate.
            
            If delay is None or 0, a smooth transition is made between the 
            two signals. The width of the smoothing region where the two signals 
            overlap is specified via the argument n_smooth.

            Note that the current implementation of the smoothing procedure is 
            quite slow, so it is advisable to use small overlap regions.

            If n_smooth is 0, the two signals are joint without any smoothing.

            If delay > 0, a signal with zero sound intensity and duration 
            delay is added between the two audio signals. 

            If the length of the combined signal exceeds max_length, only the 
            first max_length samples will be kept. 

            Args:
                signal: AudioSignal
                    Audio signal to be merged.
                delay: float
                    Delay between the two audio signals in seconds. 
                n_smooth: int
                    Width of the smoothing/overlap region (number of samples).
                max_length: int
                    Maximum length of the combined signal (number of samples).

            Returns:
                append_time: float
                    Start time of appended part in seconds from the beginning of the original signal.

            Example:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a morlet wavelet
            >>> mor = AudioSignal.morlet(rate=100, frequency=5, width=1)
            >>> # create a cosine wave
            >>> cos = AudioSignal.cosine(rate=100, frequency=3, duration=4)
            >>> # append the cosine wave to the morlet wavelet, using a overlap of 100 bins
            >>> mor.append(signal=cos, n_smooth=100)
            5.0
            >>> # show the wave form
            >>> fig = mor.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/morlet_cosine.png")

            .. image:: ../../../../ketos/tests/assets/tmp/morlet_cosine.png

        """   
        assert self.rate == signal.rate, "Cannot merge audio signals with different sampling rates."

        # if appending signal to itself, make a copy
        if signal is self:
            signal = self.copy()

        if delay is None:
            delay = 0

        delay = max(0, delay)
        if max_length is not None:
            delay = min(max_length / self.rate, delay)

        # ensure that overlap region is shorter than either signals
        n_smooth = min(n_smooth, len(self.data) - 1)
        n_smooth = min(n_smooth, len(signal.data) - 1)

        # compute total length
        len_tot = self.merged_length(signal, delay, n_smooth)

        append_time = len(self.data) / self.rate

        # extract data from overlap region
        if delay == 0 and n_smooth > 0:

            # signal 1
            a = self.split(-n_smooth)

            # signal 2
            b = signal.split(n_smooth)

            # superimpose a and b
            # TODO: If possible, vectorize this loop for faster execution
            # TODO: Cache values returned by _smoothclamp to avoid repeated calculation
            # TODO: Use coarser binning for smoothing function to speed things up even more
            c = np.empty(n_smooth)
            for i in range(n_smooth):
                w = _smoothclamp(i, 0, n_smooth-1)
                c[i] = (1.-w) * a.data[i] + w * b.data[i]
            
            append_time = len(self.data) / self.rate

            # append
            self.data = np.append(self.data, c)

        elif delay > 0:
            z = np.zeros(int(delay * self.rate))
            self.data = np.append(self.data, z)
            append_time = len(self.data) / self.rate
            
        self.data = np.append(self.data, signal.data) 
        
        assert len(self.data) == len_tot # check that length of merged signal is as expected

        # mask inserted zeros
        if delay > 0:
            self.data = np.ma.masked_values(self.data, 0)

        # remove all appended data from signal        
        if max_length is not None:
            if len_tot > max_length:
                self._crop(i1=0, i2=max_length)
                i2 = len(signal.data)
                i1 = max(0, i2 - (len_tot - max_length))
                signal._crop(i1=i1, i2=i2)
            else:
                signal.data = None
        else:
            signal.data = None
        
        return append_time

    def split(self, s):
        """ Split audio signal.

            After splitting, this instance contains the remaining part of the audio signal.        

            Args:
                s: int
                    If s >= 0, select samples [:s]. If s < 0, select samples [-s:]
                    
            Returns:
                Instance of AudioSignal
                    Selected part of the audio signal.
        """   
        if s is None or s == math.inf:
            s = len(self.data)
        
        if s >= 0:
            v = self.data[:s]
            self._crop(i1=s,i2=len(self.data))
        else:
            v = self.data[s:]
            self._crop(i1=0,i2=len(self.data)+s)
 
        return AudioSignal(rate=self.rate, data=v, tag=self.tag)

    def merged_length(self, signal=None, delay=None, n_smooth=None):
        """ Compute sample size of merged signal (without actually merging the signals)

            Args:
                signal: AudioSignal
                    Audio signal to be merged
                delay: float
                    Delay between the two audio signals in seconds.
        """   
        if signal is None:
            return len(self.data)

        assert self.rate == signal.rate, "Cannot merge audio signals with different sampling rates."

        if delay is None:
            delay = 0
            
        if n_smooth is None:
            n_smooth = 0

        m = len(self.data)
        n = len(signal.data)
        l = m + n
        
        if delay > 0:
            l += int(delay * self.rate)
        elif delay == 0:
            l -= n_smooth
        
        return l

    def add_gaussian_noise(self, sigma):
        """ Add Gaussian noise to the signal

            Args:
                sigma: float
                    Standard deviation of the gaussian noise

            Example:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a morlet wavelet
            >>> morlet = AudioSignal.morlet(rate=100, frequency=2.5, width=1)
            >>> morlet_pure = morlet.copy() # make a copy
            >>> # add some noise
            >>> morlet.add_gaussian_noise(sigma=0.3)
            >>> # show the wave form
            >>> fig = morlet_pure.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/morlet_wo_noise.png")
            >>> fig = morlet.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/morlet_w_noise.png")

            .. image:: ../../../../ketos/tests/assets/tmp/morlet_wo_noise.png

            .. image:: ../../../../ketos/tests/assets/tmp/morlet_w_noise.png

        """
        noise = AudioSignal.gaussian_noise(rate=self.rate, sigma=sigma, samples=len(self.data))
        self.add(noise)

    def add(self, signal, delay=0, scale=1):
        """ Add the amplitudes of the two audio signals.
        
            The audio signals must have the same sampling rates.

            The summed signal always has the same length as the present instance.

            If the audio signals have different lengths and/or a non-zero delay is selected, 
            only the overlap region will be affected by the operation.
            
            If the overlap region is empty, the original signal is unchanged.

            Args:
                signal: AudioSignal
                    Audio signal to be added
                delay: float
                    Shift the audio signal by this many seconds
                scale: float
                    Scaling factor for signal to be added

            Example:

            >>> from ketos.audio_processing.audio import AudioSignal
            >>> # create a morlet wavelet
            >>> mor = AudioSignal.morlet(rate=100, frequency=5, width=1)
            >>> # create a cosine wave
            >>> cos = AudioSignal.cosine(rate=100, frequency=3, duration=4)
            >>> # add the cosine on top of the morlet wavelet, with a delay of 2 sec and a scaling factor of 0.3
            >>> mor.add(signal=cos, delay=2.0, scale=0.3)
            >>> # show the wave form
            >>> fig = mor.plot()
            >>> fig.savefig("ketos/tests/assets/tmp/morlet_cosine_added.png")

            .. image:: ../../../../ketos/tests/assets/tmp/morlet_cosine_added.png

        """
        assert self.rate == signal.rate, "Cannot add audio signals with different sampling rates."

        if delay >= 0:
            i_min = int(delay * self.rate)
            j_min = 0
            i_max = min(self.data.shape[0], signal.data.shape[0] + i_min)
            j_max = min(signal.data.shape[0], self.data.shape[0] - i_min)
            
        else:
            i_min = 0
            j_min = int(-delay * self.rate)
            i_max = min(self.data.shape[0], signal.data.shape[0] - j_min)
            j_max = min(signal.data.shape[0], self.data.shape[0] + j_min)
            
        if i_max > i_min and i_max > 0 and j_max > j_min and j_max > 0:
            self.data[i_min:i_max] += scale * signal.data[j_min:j_max]

    def resample(self, new_rate):
        """ Resample the acoustic signal with an arbitrary sampling rate.

        Note: Code adapted from Kahl et al. (2017)
              Paper: http://ceur-ws.org/Vol-1866/paper_143.pdf
              Code:  https://github.com/kahst/BirdCLEF2017/blob/master/birdCLEF_spec.py  

        Args:
            new_rate: int
                New sampling rate in Hz
        """
        if len(self.data) < 2:
            self.rate = new_rate

        else:                
            orig_rate = self.rate
            sig = self.data

            duration = sig.shape[0] / orig_rate

            time_old  = np.linspace(0, duration, sig.shape[0])
            time_new  = np.linspace(0, duration, int(sig.shape[0] * new_rate / orig_rate))

            interpolator = interpolate.interp1d(time_old, sig.T)
            new_audio = interpolator(time_new).T

            new_sig = np.round(new_audio).astype(sig.dtype)

            self.rate = new_rate
            self.data = new_sig

    def copy(self):
        """ Makes a hard copy of the present instance.

            Returns:
                Instance of TimeStampedAudioSignal
                    Copied signal
        """                
        data = np.copy(self.data)
        return AudioSignal(rate=self.rate, data=data, tag=self.tag, tstart=self.tmin)

def _smoothclamp(x, mi, mx): 
        """ Smoothing function
        """    
        return (lambda t: np.where(t < 0 , 0, np.where( t <= 1 , 3*t**2-2*t**3, 1 ) ) )( (x-mi)/(mx-mi) )


class TimeStampedAudioSignal(AudioSignal):
    """ Audio signal with global time stamp and optionally a tag 
        that may be used to indicate the source.

        Args:
            rate: int
                Sampling rate in Hz
            data: 1d numpy array
                Audio data 
            time_stamp: datetime
                Global time stamp marking start of audio recording
            tag: str
                Optional argument that may be used to indicate the source.
    """

    def __init__(self, rate, data, time_stamp, tag=""):
        AudioSignal.__init__(self, rate, data, tag)
        self.time_stamp = time_stamp

    @classmethod
    def from_audio_signal(cls, audio_signal, time_stamp, tag=""):
        """ Initialize time stamped audio signal from regular audio signal.

            Args:
                audio_signal: AudioSignal
                    Audio signal
                time_stamp: datetime
                    Global time stamp marking start of audio recording
                tag: str
                    Optional argument that may be used to indicate the source.
        """
        return cls(audio_signal.rate, audio_signal.data, time_stamp, tag)

    @classmethod
    def from_wav(cls, path, time_stamp):
        """ Generate time stamped audio signal from wave file

            Args:
                path: str
                    Path to input wave file
                time_stamp: datetime
                    Global time stamp marking start of audio recording

            Returns:
                Instance of TimeStampedAudioSignal
                    Time stamped audio signal from wave file
        """        
        signal = super(TimeStampedAudioSignal, cls).from_wav(path=path)
        return cls.from_audio_signal(audio_signal=signal, time_stamp=time_stamp)

    def copy(self):
        """ Makes a copy of the time stamped audio signal.

            Returns:
                Instance of TimeStampedAudioSignal
                    Copied signal
        """                
        signal = super(TimeStampedAudioSignal, self).copy()
        return self.from_audio_signal(audio_signal=signal, time_stamp=self.time_stamp)

    def begin(self):
        """ Get global time stamp marking the start of the audio signal.

            Returns:
                t: datetime
                Global time stamp marking the start of audio the recording
        """
        t = self.time_stamp
        return t

    def end(self):
        """ Get global time stamp marking the end of the audio signal.

            Returns:
                t: datetime
                Global time stamp marking the end of audio the recording
        """
        duration = len(self.data) / self.rate
        delta = datetime.timedelta(seconds=duration)
        t = self.begin() + delta
        return t 

    def _crop(self, i1, i2):
        """ Crop time-stamped audio signal using [i1, i2] as cropping range

            Args:
                i1: int
                    Lower bound of cropping interval
                i2: int
                    Upper bound of cropping interval
        """   
        dt = max(0, i1/self.rate)
        dt = min(self.duration(), dt)
        self.time_stamp += datetime.timedelta(microseconds=1e6*dt) # update time stamp

        super(TimeStampedAudioSignal, self)._crop(i1, i2)   # crop signal
        
    def crop(self, begin=None, end=None):
        """ Crop time-stamped audio signal

            Args:
                begin: datetime
                    Start date and time of selection window
                end: datetime
                    End date and time of selection window
        """   
        b, e = None, None
        
        if begin is not None:
            b = (begin - self.begin()).total_seconds()
        if end is not None:
            e = (end - self.begin()).total_seconds()

        i1, i2 = self._selection(b, e)
        
        self._crop(i1, i2)

    def split(self, s):
        """ Split time-stamped audio signal.

            After splitting, this instance contains the remaining part of the audio signal.        

            Args:
                s: int
                    If s >= 0, select samples [:s]. If s < 0, select samples [-s:]
                    
            Returns:
                Instance of TimeStampedAudioSignal
                    Selected part of the audio signal.
        """   
        if s is None:
            s = len(self.data)

        if s >= 0:
            t = self.begin()
        else:
            dt = -s / self.rate
            t = self.end() - datetime.timedelta(microseconds=1e6*dt) # update time stamp
            
        a = super(TimeStampedAudioSignal, self).split(s)
        return self.from_audio_signal(audio_signal=a, time_stamp=t)

    def append(self, signal, delay=None, n_smooth=0, max_length=None):
        """ Combine two time-stamped audio signals.

            If delay is None (default), the delay will be determined from the 
            two audio signals' time stamps.

            See :meth:`audio_signal.append` for more details.

            Args:
                signal: AudioSignal
                    Audio signal to be merged
                delay: float
                    Delay between the two audio signals in seconds.
                    
            Returns:
                t: datetime
                    Start time of appended part.
        """   
        if delay is None:
            delay = self.delay(signal)

        dt = super(TimeStampedAudioSignal, self).append(signal=signal, delay=delay, n_smooth=n_smooth, max_length=max_length)
        t = self.begin() + datetime.timedelta(microseconds=1e6*dt)
        return t

    def delay(self, signal):
        """ Compute delay between two time stamped audio signals, defined 
            as the time difference between the end of the first signal and 
            the beginning of the second signal.

            Args:
                signal: TimeStampedAudioSignal
                    Audio signal

            Returns:
                d: float
                    Delay in seconds
        """   
        d = None
        
        if isinstance(signal, TimeStampedAudioSignal):
            d = (signal.begin() - self.end()).total_seconds()
        
        return d
