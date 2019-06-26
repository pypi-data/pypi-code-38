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

""" Unit tests for the 'audio' module within the ketos library
"""

import pytest
import ketos.audio_processing.audio as aud
import datetime
import numpy as np



def test_time_stamped_audio_signal_has_correct_begin_and_end_times(sine_audio):
    audio = sine_audio
    today = datetime.datetime.today()
    audio.time_stamp = today 
    seconds = sine_audio.duration()
    duration = datetime.timedelta(seconds=seconds)
    assert audio.begin() == today
    assert audio.end() == today + duration

def test_crop_audio_signal(sine_audio):
    audio = sine_audio
    seconds = len(audio.data) / audio.rate
    crop_begin = audio.begin() + datetime.timedelta(seconds=seconds/10.)
    crop_end = audio.end() - datetime.timedelta(seconds=seconds/10.)
    audio_cropped = audio
    audio_cropped.crop(begin=crop_begin, end=crop_end)
    seconds_cropped = len(audio_cropped.data) / audio_cropped.rate
    assert seconds_cropped/seconds == pytest.approx(8./10., rel=1./audio.rate)
    assert audio_cropped.begin() == crop_begin


def test_split_with_positive_sample_id(sine_audio):
    audio = sine_audio 
    t0 = audio.time_stamp
    first = audio.data[0]
    last = audio.data[-1]
    n = len(audio.data)
    m = int(0.1*n)
    dt = m / audio.rate
    s = audio.split(m)
    assert len(s.data) == m
    assert len(audio.data) == n-m
    assert first == s.data[0]
    assert last == audio.data[-1]
    assert audio.time_stamp == t0 + datetime.timedelta(microseconds=1e6*dt)
    assert s.time_stamp == t0

def test_split_with_sample_larger_than_length(sine_audio):
    audio = sine_audio
    n = len(audio.data)
    m = int(1.5*n)
    s = audio.split(m)
    assert len(s.data) == n
    assert audio.empty() == True

def test_split_with_negative_sample_id(sine_audio):
    audio = sine_audio
    t0 = audio.begin()
    t1 = audio.end()
    first = audio.data[0]
    last = audio.data[-1]
    n = len(audio.data)
    m = -int(0.2*n)
    dt = -m / audio.rate
    s = audio.split(m)
    assert len(s.data) == -m
    assert len(audio.data) == n+m
    assert first == audio.data[0]
    assert last == s.data[-1]
    assert s.time_stamp == t1 - datetime.timedelta(microseconds=1e6*dt)
    assert audio.time_stamp == t0

def test_append_audio_signal_to_itself(sine_audio):
    audio = sine_audio
    len_sum = 2 * len(audio.data)
    audio_copy = audio.copy()
    audio_copy.time_stamp = audio.end()
    audio.append(audio_copy)
    assert len(audio.data) == len_sum
    
def test_segment_audio_signal(sine_audio):
    lentot = sine_audio.duration()
    segs = sine_audio.segment(lentot/3)
    assert len(segs) == 3
    # recover original full length signal by concatenating segments
    v = segs[0].data
    for s in segs[1:]:
        v = np.concatenate((v, s.data))
    # check that the recovered audio signal matches the original
    assert np.all(v == sine_audio.data)
    # check behaviour when length is larger than 0.5 of total length
    segs = sine_audio.segment(0.8*lentot)
    assert len(segs) == 1
    assert segs[0].duration() == pytest.approx(0.8*lentot, abs=0.01)

def test_segment_audio_signal_w_annotations(sine_audio):
    lentot = sine_audio.duration()    
    # add some annotations
    t1 = 0.1 * lentot
    t2 = 0.2 * lentot
    sine_audio.annotate(labels=1, boxes=[t1, t2])
    t1 = 0.4 * lentot
    t2 = 0.6 * lentot
    sine_audio.annotate(labels=1, boxes=[t1, t2])
    t1 = 0.45 * lentot
    t2 = 0.95 * lentot
    sine_audio.annotate(labels=1, boxes=[t1, t2])
    # segment
    segs = sine_audio.segment(length=lentot/3, keep_time=True)
    assert len(segs) == 3
    # 1st segment should have one annotation
    s = segs[0]
    assert len(s.labels) == 1
    assert s.boxes[0][1] == 0.2 * lentot
    # 2nd segment should have two annotations
    s = segs[1]
    assert len(s.labels) == 2
    assert s.boxes[0][0] == 0.4 * lentot
    assert s.boxes[1][1] == 0.95 * lentot
    # 3rd segment should have one annotation
    s = segs[2]
    assert len(s.labels) == 1
    assert s.boxes[0][0] == 0.45 * lentot
    assert s.boxes[0][1] == 0.95 * lentot

def test_append_audio_signal_without_time_stamp_to_itself(sine_audio_without_time_stamp): 
    len_sum = 2 * len(sine_audio_without_time_stamp.data)
    sine_audio_without_time_stamp.append(sine_audio_without_time_stamp)
    assert len(sine_audio_without_time_stamp.data) == len_sum

def test_append_with_smoothing(sine_audio):
    audio = sine_audio
    t = audio.duration()
    at = audio.append(signal=audio, n_smooth=100)
    assert audio.duration() == pytest.approx(2.*t - 100/audio.rate, rel=1./audio.rate)
    assert at == audio.begin() + datetime.timedelta(microseconds=1e6*(t - 100/audio.rate))

def test_append_with_delay(sine_audio):
    audio = sine_audio
    t = audio.duration()
    delay = 3.0
    audio.append(signal=audio, delay=3)
    assert audio.duration() == 2.*t + 3.0

def test_append_with_max_length(sine_audio):
    audio = sine_audio
    audio2 = audio.copy()
    t = audio.duration()
    n = len(audio.data)
    nmax = int(1.5 * n)
    audio.append(signal=audio2, max_length=nmax)
    assert len(audio.data) == nmax
    assert len(audio2.data) == 2*n - nmax

def test_append_with_max_length_and_smooth(sine_audio):
    audio = sine_audio
    audio2 = audio.copy()
    t = audio.duration()
    n = len(audio.data)
    nmax = int(1.5 * n)
    n_smooth = 200
    audio.append(signal=audio2, n_smooth=n_smooth, max_length=nmax)
    assert len(audio.data) == nmax
    assert len(audio2.data) == 2*n - n_smooth - nmax

def test_append_with_max_length_and_delay(sine_audio):
    audio = sine_audio
    audio2 = audio.copy()
    t = audio.duration()
    n = len(audio.data)
    nmax = int(1.5 * n)
    delay = t
    audio.append(signal=audio2, delay=t, max_length=nmax)
    assert len(audio.data) == nmax
    assert len(audio2.data) == n
    assert np.ma.is_masked(audio.data[-1]) 

def test_append_delay_determined_from_time_stamps(sine_audio):
    audio = sine_audio
    audio2 = audio.copy()
    dt = 5.
    audio2.time_stamp = audio.end() + datetime.timedelta(microseconds=1e6*dt)
    t = audio.duration()
    n = len(audio.data)
    audio.append(signal=audio2)
    assert audio.duration() == 2*t + dt
    assert np.ma.is_masked(audio.data[n]) 
    
def test_add_identical_audio_signals(sine_audio):
    audio = sine_audio
    t = audio.duration()
    v = np.copy(audio.data)
    audio.add(signal=audio)
    assert audio.duration() == t
    assert np.all(audio.data == 2*v)
    
def test_add_identical_audio_signals_with_delay(sine_audio):
    audio = sine_audio
    t = audio.duration()
    v = np.copy(audio.data)
    delay = 1
    audio.add(signal=audio, delay=delay)
    assert audio.duration() == t
    i = int(audio.rate * delay)
    assert audio.data[5] == v[5]
    assert audio.data[i+5] == v[i+5] + v[5]    
    
def test_add_identical_audio_signals_with_scaling_factor(sine_audio):
    audio = sine_audio
    v = np.copy(audio.data)
    audio.add(signal=audio, scale=0.5)
    assert np.all(audio.data == 1.5*v)

def test_morlet_with_default_params():
    mor = aud.AudioSignal.morlet(rate=4000, frequency=20, width=1)
    assert len(mor.data) == int(6*1*4000) # check number of samples
    assert max(mor.data) == pytest.approx(1, abs=0.01) # check max signal is 1
    assert np.argmax(mor.data) == pytest.approx(0.5*len(mor.data), abs=1) # check peak is centered
    assert mor.data[0] == pytest.approx(0, abs=0.02) # check signal is approx zero at start

def test_gaussian_noise():
    noise = aud.AudioSignal.gaussian_noise(rate=2000, sigma=2, samples=40000)
    assert noise.std() == pytest.approx(2, rel=0.05) # check standard deviation
    assert noise.average() == pytest.approx(0, abs=6*2/np.sqrt(40000)) # check mean
    assert noise.duration() == 20 # check length

def test_clip(sine_audio):
    audio = sine_audio
    segs = audio.clip(boxes=[[0.1, 0.4],[0.3, 0.7]])
    assert len(segs) == 2
    assert segs[0].duration() == pytest.approx(0.3, abs=2./audio.rate)
    assert segs[1].duration() == pytest.approx(0.4, abs=2./audio.rate)
    assert audio.duration() == pytest.approx(3.0-0.6, abs=2./audio.rate)

@pytest.mark.test_resample
def test_resampled_signal_has_correct_rate(sine_wave_file):
    signal = aud.AudioSignal.from_wav(sine_wave_file)

    new_signal = signal.copy()
    new_signal.resample(new_rate=22000)
    assert new_signal.rate == 22000

    new_signal = signal.copy()
    new_signal.resample(new_rate=2000)
    assert new_signal.rate == 2000

@pytest.mark.test_resample
def test_resampled_signal_has_correct_length(sine_wave_file):
    signal = aud.AudioSignal.from_wav(sine_wave_file)

    duration = signal.duration()

    new_signal = signal.copy()
    new_signal.resample(new_rate=22000)
    assert len(new_signal.data) == duration * new_signal.rate 

    new_signal = signal.copy()
    new_signal.resample(new_rate=2000)
    assert len(new_signal.data) == duration * new_signal.rate 

@pytest.mark.test_resample
def test_resampling_preserves_signal_shape(const_wave_file):
    signal = aud.AudioSignal.from_wav(const_wave_file)
    new_signal = signal.copy()
    new_signal.resample(new_rate=22000)

    n = min(len(signal.data), len(new_signal.data))
    for i in range(n):
        assert signal.data[i] == new_signal.data[i]

@pytest.mark.test_resample
def test_resampling_preserves_signal_frequency(sine_wave_file):
    signal = aud.AudioSignal.from_wav(sine_wave_file)
    rate = signal.rate
    sig = signal.data
    y = abs(np.fft.rfft(sig))
    freq = np.argmax(y)
    freqHz = freq * rate / len(sig)
    signal = aud.AudioSignal(rate, sig)
    new_signal = signal.copy()
    new_signal.resample(new_rate=22000)
    new_y = abs(np.fft.rfft(new_signal.data))
    new_freq = np.argmax(new_y)
    new_freqHz = new_freq * new_signal.rate / len(new_signal.data)

    assert freqHz == new_freqHz

@pytest.mark.test_make_frames
def test_signal_is_padded(sine_wave):
    rate, sig = sine_wave
    duration = len(sig) / rate
    winlen = 2*duration
    winstep = 2*duration
    signal = aud.AudioSignal(rate, sig)
    frames = signal.make_frames(winlen=winlen, winstep=winstep, zero_padding=True)
    assert frames.shape[0] == 1
    assert frames.shape[1] == 2*len(sig)
    assert frames[0, len(sig)] == 0
    assert frames[0, 2*len(sig)-1] == 0

@pytest.mark.test_make_frames
def test_can_make_overlapping_frames(sine_wave):
    rate, sig = sine_wave
    duration = len(sig) / rate
    winlen = duration/2
    winstep = duration/4
    signal = aud.AudioSignal(rate, sig)
    frames = signal.make_frames(winlen=winlen, winstep=winstep)
    assert frames.shape[0] == 3
    assert frames.shape[1] == len(sig)/2

@pytest.mark.test_make_frames
def test_can_make_non_overlapping_frames(sine_wave):
    rate, sig = sine_wave
    duration = len(sig) / rate
    winlen = duration/4
    winstep = duration/2
    signal = aud.AudioSignal(rate, sig)
    frames = signal.make_frames(winlen, winstep)
    assert frames.shape[0] == 2
    assert frames.shape[1] == len(sig)/4

@pytest.mark.test_make_frames
def test_first_frame_matches_original_signal(sine_wave):
    rate, sig = sine_wave
    duration = len(sig) / rate
    winlen = duration/4
    winstep = duration/10
    signal = aud.AudioSignal(rate, sig)
    frames = signal.make_frames(winlen, winstep)
    assert frames.shape[0] == 8
    for i in range(int(winlen*rate)):
        assert sig[i] == pytest.approx(frames[0,i], rel=1E-6)

@pytest.mark.test_make_frames
def test_window_length_can_exceed_duration(sine_wave):
    rate, sig = sine_wave
    duration = len(sig) / rate
    winlen = 2 * duration
    winstep = duration
    signal = aud.AudioSignal(rate, sig)
    frames = signal.make_frames(winlen, winstep)
    assert frames.shape[0] == 1

