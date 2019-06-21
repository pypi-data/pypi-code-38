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

""" Unit tests for the 'spectrogram' module within the ketos library
"""

import pytest
import numpy as np
from ketos.audio_processing.spectrogram import MagSpectrogram, PowerSpectrogram, MelSpectrogram, Spectrogram, interbreed, ensure_same_length
from ketos.data_handling.parsing import Interval
from ketos.audio_processing.audio import AudioSignal
import ketos.data_handling.database_interface as di
import datetime
import math
import os
import tables


current_dir = os.path.dirname(os.path.realpath(__file__))
path_to_assets = os.path.join(os.path.dirname(current_dir),"assets")
path_to_tmp = os.path.join(path_to_assets,'tmp')


def test_init_mag_spectrogram_from_sine_wave(sine_audio):
    
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    NFFT = 256
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep, NFFT=NFFT)
    mag = spec.image
    for i in range(mag.shape[0]):
        freq = np.argmax(mag[i])
        freqHz = freq * spec.fres
        assert freqHz == pytest.approx(2000, abs=spec.fres)
    
    assert spec.NFFT == NFFT
    assert spec.tres == winstep
    assert spec.fmin == 0    

def test_init_power_spectrogram_from_sine_wave(sine_audio):
    
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    NFFT = 256
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep, NFFT=NFFT)
    mag = spec.image
    for i in range(mag.shape[0]):
        freq = np.argmax(mag[i])
        freqHz = freq * spec.fres
        assert freqHz == pytest.approx(2000, abs=spec.fres)
    
    assert spec.NFFT == NFFT
    assert spec.tres == winstep
    assert spec.fmin == 0
    
def test_init_mel_spectrogram_from_sine_wave(sine_audio):
    
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    NFFT = 256
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep, NFFT=NFFT)
    mag = spec.image
    for i in range(mag.shape[0]):
        freq = np.argmax(mag[i])
        freqHz = freq * spec.fres
        assert freqHz == pytest.approx(1360, abs=spec.fres)
    
    assert spec.NFFT == NFFT
    assert spec.tres == winstep
    assert spec.fmin == 0

def test_init_mel_spectrogram_with_kwargs(sine_audio):
    
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    NFFT = 256
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep, NFFT=NFFT, n_filters=80, n_ceps=40)
    mag = spec.image
    for i in range(mag.shape[0]):
        freq = np.argmax(mag[i])
        freqHz = freq * spec.fres
        assert freqHz == pytest.approx(4444, abs=spec.fres)
    
    assert spec.NFFT == NFFT
    assert spec.tres == winstep
    assert spec.fmin == 0
    assert spec.image.shape[1] == 40

def test_find_bins():    
    img = np.ones(shape=(20,30))
    spec = Spectrogram(image=img, fmin=60.5, fres=0.5)
    b = spec._find_tbin(t=[-0.5, 4.5, 99])
    assert b[0] == -1
    assert b[1] == 4
    assert b[2] == 99 #img.shape[0]
    b = spec._find_fbin(f=[30, 61.2])
    assert b[0] == int((30-60.5)/0.5)
    assert b[1] == 1
    b = spec._find_fbin(f=[200])
    assert b[0] == int((200-60.5)/0.5) #img.shape[1]

def test_find_bins_with_truncation():    
    img = np.ones(shape=(20,30))
    spec = Spectrogram(image=img, fmin=60.5, fres=0.5)
    b = spec._find_tbin(t=[-0.5, 4.5, 99], truncate=True)
    assert b[0] == 0
    assert b[1] == 4
    assert b[2] == img.shape[0]-1
    b = spec._find_fbin(f=[30, 61.2], truncate=True)
    assert b[0] == 0
    assert b[1] == 1
    b = spec._find_fbin(f=[200], truncate=True)
    assert b[0] == img.shape[1]-1

def test_clip_one_box():    
    img = np.ones(shape=(20,30))
    img[6,0] = 1.2
    img[13,0] = 1.66
    spec = Spectrogram(image=img, fmin=60.5, fres=0.5)
    box = [5.1, 10.5, 30., 64.3]
    y = spec._clip(boxes=box)
    assert len(y) == 1
    assert y[0].image.shape[0] == 6
    assert y[0].image.shape[1] == 8
    assert y[0].fmin == 60.5
    assert spec.image.shape[0] == img.shape[0] - y[0].image.shape[0]
    assert y[0].image[1,0] == 1.2
    assert spec.image[7,0] == 1.66

def test_clip_2d_box():    
    img = np.ones(shape=(20,30))
    img[6,0] = 1.2
    img[13,0] = 1.66
    spec = Spectrogram(image=img, fmin=60.5, fres=0.5)
    box = [5.1, 10.5, 0, 3000]
    y = spec._clip(boxes=box)
    assert len(y) == 1
    assert y[0].image.shape[0] == 6
    assert y[0].image.shape[1] == img.shape[1]

def test_clip_two_boxes():    
    img = np.ones(shape=(20,30))
    spec = Spectrogram(image=img, fmin=60.5, fres=0.5)
    box1 = [5.1, 10.5, 30., 64.3]
    box2 = (6.1, 11.5, 64.1, 65.1)
    y = spec._clip(boxes=[box1,box2])
    assert len(y) == 2
    assert y[0].image.shape[0] == 6
    assert y[0].image.shape[1] == 8
    assert y[0].fmin == 60.5
    assert y[1].image.shape[0] == 6
    assert y[1].image.shape[1] == 3
    assert y[1].fmin == 64.0
    assert spec.image.shape[0] == img.shape[0] - 7

def test_append_spectrogram(sine_audio):
    spec1 = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    spec2 = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    size = spec1.image.shape
    spec1.append(spec2)
    assert spec1.image.shape[0] == 2*size[0]
    assert spec1.image.shape[1] == size[1]

def test_sum_spectrogram_has_same_shape_as_original(sine_audio):
    spec1 = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    orig_shape = spec1.image.shape
    spec2 = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    spec2.crop(tlow=1.0, thigh=2.5, flow=1000, fhigh=4000)
    spec1.add(spec2, delay=0, scale=1)
    assert spec1.image.shape == orig_shape

def test_add_spectrograms_with_different_shapes(sine_audio):
    spec1 = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    v_00 = spec1.image[0,0]
    t = spec1._find_tbin(1.5)
    f = spec1._find_fbin(2000)
    v_tf = spec1.image[t,f]
    spec2 = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    spec2.crop(tlow=1.0, thigh=2.5, flow=1000, fhigh=4000)
    spec1.add(spec2, delay=1.0, scale=1.3)
    assert spec1.image[0,0] == v_00 # values outside addition region are unchanged
    assert spec1.image[t,f] == pytest.approx(2.3 * v_tf, rel=0.001) # values outside addition region have changed

def test_add_spectrograms_with_smoothing():
    spec1 = Spectrogram(image=np.ones((100,100)))
    spec2 = spec1.copy()
    spec1.add(spec2, smooth=True, smooth_par=5)
    assert spec1.image[50,50] == pytest.approx(2.0, abs=0.0001)
    assert spec1.image[0,50] == pytest.approx(1.01, abs=0.01)
    assert spec1.image[9,50] == pytest.approx(1.50, abs=0.06)

def test_cropped_mag_spectrogram_has_correct_size(sine_audio):
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    spec.crop(fhigh=4000)
    assert spec.image.shape == (57, 24)
    spec.crop(flow=1000)
    assert spec.image.shape == (57, 19)

def test_cropped_power_spectrogram_has_correct_size(sine_audio):
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    spec.crop(fhigh=4000)
    assert spec.image.shape == (57, 24)
    spec.crop(flow=1000)
    assert spec.image.shape == (57, 19)

# TODO: Fix cropping method so it also works for Mel spectrograms
@pytest.mark.xfail
def test_cropped_mel_spectrogram_has_correct_size(sine_audio):
   spec = MelSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
   spec.crop(fhigh=4000)
   assert spec.image.shape == (57, 20)
   spec.crop(flow=1000)
   assert spec.image.shape == (57, 15)
   spec.crop(tlow=1.0)
   assert spec.image.shape == (37, 15)
   spec.crop(thigh=2.5)
   assert spec.image.shape == (30, 15)

def test_mag_compute_average_and_median_without_cropping(sine_audio):
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average()
    med = spec.median()
    assert avg == pytest.approx(8620, abs=2.0)
    assert med == pytest.approx(970, abs=2.0)

def test_mag_compute_average_and_median_without_cropping(sine_audio):
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average()
    med = spec.median()
    assert avg == pytest.approx(8620, abs=2.0)
    assert med == pytest.approx(970, abs=2.0)
    
def test_power_compute_average_and_median_without_cropping(sine_audio):
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average()
    med = spec.median()
    assert avg == pytest.approx(3567190, abs=2.0)
    assert med == pytest.approx(3677, abs=2.0)

def test_mel_compute_average_and_median_without_cropping(sine_audio):
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average()
    med = spec.median()
    assert avg == pytest.approx(-260, abs=2.0)
    assert med == pytest.approx(-172, abs=2.0)

def test_mag_compute_average_and_median_with_cropping(sine_audio):
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average(tlow=0, thigh=0.4)
    med = spec.median(flow=1000, fhigh=2000)
    assert avg == pytest.approx(8618, abs=0.5)
    assert med == pytest.approx(33923.9, abs=0.5)   

def test_power_compute_average_and_median_with_cropping(sine_audio):
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average(tlow=0, thigh=0.4)
    med = spec.median(flow=1000, fhigh=2000)
    assert avg == pytest.approx(3567190, abs=1.0)
    assert med == pytest.approx(4495422.5, abs=0.5)   

def test_mel_compute_average_and_median_with_cropping(sine_audio):
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average(tlow=0, thigh=0.4)
    med = spec.median(flow=1000, fhigh=2000)
    assert avg == pytest.approx(-259, abs=1.0)
    assert med == pytest.approx(211.8, abs=1.0) 

def test_mag_compute_average_with_axis(sine_audio):
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average(tlow=1, thigh=1.2, axis=1)
    assert avg.shape == (4,)
    expected =  np.array([8618.055108, 8618.055108, 8618.055108, 8618.055108])
    np.testing.assert_array_almost_equal(avg, expected, decimal=1)

def test_power_compute_average_with_axis(sine_audio):
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = 0.01 * spec.average(tlow=1, thigh=1.2, axis=1)
    assert avg.shape == (4,)
    expected = 0.01 * np.array([3567190.528536, 3567190.528536, 3567190.528536, 3567190.528536])
    np.testing.assert_array_almost_equal(avg, expected, decimal=1)

def test_mel_compute_average_with_axis(sine_audio):
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    avg = spec.average(tlow=1, thigh=1.2, axis=1)
    assert avg.shape == (4,)
    expected =  np.array([-259.345679, -259.345679, -259.345679, -259.345679])
    np.testing.assert_array_almost_equal(avg, expected, decimal=1)
        
def test_mag_spectrogram_has_correct_time_axis(sine_audio):
    now = datetime.datetime.today()
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=1, winstep=1, NFFT=256, timestamp=now)
    assert len(spec.time_labels()) == 3
    assert spec.time_labels()[0] == now
    assert spec.time_labels()[1] == now + datetime.timedelta(seconds=1)
    assert spec.time_labels()[2] == now + datetime.timedelta(seconds=2)   
    
def test_power_spectrogram_has_correct_time_axis(sine_audio):
    now = datetime.datetime.today()
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=1, winstep=1, NFFT=256, timestamp=now)
    assert len(spec.time_labels()) == 3
    assert spec.time_labels()[0] == now
    assert spec.time_labels()[1] == now + datetime.timedelta(seconds=1)
    assert spec.time_labels()[2] == now + datetime.timedelta(seconds=2)   

def test_mel_spectrogram_has_correct_time_axis(sine_audio):
    now = datetime.datetime.today()
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=1, winstep=1, NFFT=256, timestamp=now)
    assert len(spec.time_labels()) == 3
    assert spec.time_labels()[0] == now
    assert spec.time_labels()[1] == now + datetime.timedelta(seconds=1)
    assert spec.time_labels()[2] == now + datetime.timedelta(seconds=2)

def test_mag_spectrogram_has_correct_NFFT(sine_audio):
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep)
    
    assert spec.NFFT == int(round(winlen * sine_audio.rate))

def test_power_spectrogram_has_correct_NFFT(sine_audio):
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    spec = PowerSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep)
    
    assert spec.NFFT == int(round(winlen * sine_audio.rate))

def test_mel_spectrogram_has_correct_NFFT(sine_audio):
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    spec = MelSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep)
    
    assert spec.NFFT == int(round(winlen * sine_audio.rate))

def test_blur_time_axis():
    spec = Spectrogram()
    img = np.zeros((21,21))
    img[10,10] = 1
    spec.image = img
    sig = 2.0
    spec.blur_gaussian(tsigma=sig, fsigma=0.01)
    xy = spec.image / np.max(spec.image)
    x = xy[:,10]
    assert x[10] == pytest.approx(1, rel=0.001)
    assert x[9] == pytest.approx(np.exp(-pow(1,2)/(2.*pow(sig,2))), rel=0.001)
    assert x[8] == pytest.approx(np.exp(-pow(2,2)/(2.*pow(sig,2))), rel=0.001)    
    assert xy[10,9] == pytest.approx(0, rel=0.001) 
    
def test_blur_freq_axis():
    spec = Spectrogram()
    img = np.zeros((21,21))
    img[10,10] = 1
    spec.image = img
    sig = 4.2
    spec.blur_gaussian(tsigma=0.01, fsigma=sig)
    xy = spec.image / np.max(spec.image)
    y = xy[10,:]
    assert y[10] == pytest.approx(1, rel=0.001)
    assert y[9] == pytest.approx(np.exp(-pow(1,2)/(2.*pow(sig,2))), rel=0.001)
    assert y[8] == pytest.approx(np.exp(-pow(2,2)/(2.*pow(sig,2))), rel=0.001)    
    assert xy[9,10] == pytest.approx(0, rel=0.001) 

def test_create_audio_from_spectrogram(sine_audio):
    duration = sine_audio.duration()
    winlen = duration/4
    winstep = duration/10
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=winlen, winstep=winstep)
    audio = spec.audio_signal()
    assert audio.rate == sine_audio.rate

def test_annotate():
    spec = Spectrogram()
    spec.annotate(labels=1, boxes=[1,2,3,4])
    spec.annotate(labels=[2,3], boxes=[[1,2,3,4],[5,6,7,8]])
    assert len(spec.labels) == 3
    spec.delete_annotations(id=[0,1])
    assert len(spec.labels) == 1
    assert spec.labels[0] == 3

def test_crop_with_copy_true():
    img = np.zeros((19,31))
    spec = Spectrogram(image=img, tag='file.wav')
    labels = [1,2]
    box1 = [14.,17.,0.,29.]
    box2 = [2.1,13.0,1.1,28.5]
    boxes = [box1, box2]
    spec.annotate(labels=labels, boxes=boxes)
    scut = spec.crop(2,5,24,27, make_copy=True)
    # check that start time is as expected
    assert scut.tmin == 2    
    # check that annotations have been correctly carried over
    assert len(scut.labels) == 1
    assert scut.labels[0] == 2
    assert scut.boxes[0][0] == pytest.approx(2.1, abs=0.001)
    assert scut.boxes[0][1] == pytest.approx(5.0, abs=0.001)
    assert scut.boxes[0][2] == pytest.approx(24.0, abs=0.001)
    assert scut.boxes[0][3] == pytest.approx(27.0, abs=0.001)
    # check that file and time information have been correctly carried over
    assert spec.file_dict[0] == 'file.wav'
    n = len(scut.file_vector)
    assert n == scut.image.shape[0]
    for i in range(n):
        assert spec.file_vector[i] == 0
        assert spec.time_vector[i] == i * scut.tres

def test_extract_with_empty_remainder():
    img = np.zeros((19,31))
    spec = Spectrogram(image=img, tag='file.wav')
    spec.annotate(labels=1, boxes=[0,19])
    seg = spec.extract(label=1)
    assert spec.image is None
    assert np.all(seg[0].image == img) 

def test_extract_with_non_empty_remainder():
    img = np.zeros((19,31))
    spec = Spectrogram(image=img, tag='file.wav')
    spec.annotate(labels=[1,1], boxes=[[4,13],[5.1,6.4]])
    seg = spec.extract(label=1)
    assert spec.image.shape[0] == 10
    assert spec.image.shape[1] == img.shape[1]
    assert seg[0].image.shape[0] == 9
    assert seg[0].image.shape[1] == img.shape[1]
    assert seg[1].image.shape[0] == 2
    assert seg[1].image.shape[1] == img.shape[1]
    assert np.sum(spec.get_label_vector(1)) == 0
    assert np.sum(seg[0].get_label_vector(1)) == 9
    assert np.sum(seg[1].get_label_vector(1)) == 2
    assert seg[0].file_dict[0] == 'file.wav'
    assert seg[1].file_dict[0] == 'file.wav'
    assert len(seg[1].time_vector) == 2
    assert seg[1].time_vector[0] == 5
    assert seg[1].time_vector[1] == 6

@pytest.mark.test_stretch
def test_stretch():
    box1 = [1.0, 2.0]
    box2 = [0.5, 4.0]
    min_length = 2.0
    boxes = [box1, box2]
    spec = Spectrogram()
    spec.annotate(labels=[1,2], boxes=[box1,box2])
    boxes = spec._stretch(boxes=boxes, min_length=min_length)
    assert len(boxes) == 2
    assert boxes[0][1]-boxes[0][0] == pytest.approx(min_length, abs=0.0001)
    assert boxes[1][1]-boxes[1][0] > min_length

@pytest.mark.test_select_boxes
def test_select_boxes():
    box1 = [1.0, 2.0]
    box2 = [0.5, 4.0]
    labels = [1, 2]
    label = 1
    spec = Spectrogram()
    spec.annotate(labels=labels, boxes=[box1,box2])
    boxes, _ = spec._select_boxes(label=label)
    assert len(boxes) == 1
    assert boxes[0] == [1.0, 2.0, 0, 2]

@pytest.mark.test_segment
def test_segment_using_number():
    img = np.zeros((101,31))
    spec = Spectrogram(image=img)
    segs = spec.segment(number=3)
    assert len(segs) == 3
    assert segs[0].image.shape[0] == 33
    assert segs[0].image.shape[1] == 31

@pytest.mark.test_segment
def test_segment_using_length():
    img = np.zeros((101,31))
    spec = Spectrogram(image=img)
    spec.tres = 0.1
    assert spec.duration() == pytest.approx(10.1, abs=1E-6)
    segs = spec.segment(length=4.0)
    assert len(segs) == 2
    assert segs[0].image.shape[0] == 40
    assert segs[0].image.shape[1] == 31
    assert segs[1].image.shape[0] == 40
    assert segs[1].image.shape[1] == 31

@pytest.mark.test_segment
def test_segment_using_same_length_as_spectrogram_has_no_effect():
    img = np.zeros((101,31))
    spec = Spectrogram(image=img)
    spec.tres = 0.1
    assert spec.duration() == pytest.approx(10.1, abs=1E-6)
    segs = spec.segment(length=10.1)
    assert len(segs) == 1
    assert segs[0].image.shape[0] == 101

@pytest.mark.test_segment
def test_segment_using_length_w_overlap():
    img = np.zeros((101,31))
    spec = Spectrogram(image=img)
    spec.tres = 0.1
    assert spec.duration() == pytest.approx(10.1, abs=1E-6)
    segs = spec.segment(length=4.0, overlap=0.75)
    assert len(segs) == 7
    assert segs[0].image.shape[0] == 40
    assert segs[0].image.shape[1] == 31
    assert segs[1].image.shape[0] == 40
    assert segs[1].image.shape[1] == 31

@pytest.mark.test_copy_spectrogram
def test_copy_spectrogram():
    img = np.zeros((101,31))
    spec = Spectrogram(image=img, fmin=14, fres=0.1)
    spec2 = spec.copy()
    spec = None
    assert spec2.image.shape[0] == 101
    assert spec2.image.shape[1] == 31
    assert spec2.fmin == 14
    assert spec2.fres == 0.1

@pytest.mark.test_copy_mag_spectrogram
def test_copy_mag_spectrogram(sine_audio):
    spec = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec2 = spec.copy()
    assert spec2.image.shape[0] == spec.image.shape[0]
    assert spec2.image.shape[1] == spec.image.shape[1]
    assert spec2.tmin == spec.tmin
    assert spec2.tres == spec.tres

@pytest.mark.test_interbreed
def test_interbreed_spectrograms_with_default_args():
    s1 = Spectrogram(image=np.ones((100,100)))
    s2 = s1.copy()
    specs = interbreed(specs1=[s1], specs2=[s2], num=9)
    assert len(specs) == 9
    assert specs[0].duration() == 100

@pytest.mark.test_interbreed
def test_interbreed_spectrograms_with_validation_function():
    s1 = Spectrogram(image=np.ones((100,100)))
    s2 = s1.copy()
    def check_max(spec1, spec2, new_spec):
        m1 = np.max(spec1.image)
        m2 = np.max(spec2.image)
        m = np.max(new_spec.image)
        return m > m1 + 0.5 * m2

    specs = interbreed(specs1=[s1], specs2=[s2], num=9, scale=(0,1), seed=1, validation_function=check_max)

    assert len(specs) == 9
    for s in specs:
        m1 = np.max(s1.image)
        m2 = np.max(s2.image)
        m = np.max(s.image)
        assert m > m1 + 0.5 * m2

@pytest.mark.test_interbreed
def test_interbreed_spectrograms_with_min_peak_diff():
    s1 = Spectrogram(image=np.ones((100,100)))
    s2 = s1.copy()
    specs = interbreed(specs1=[s1], specs2=[s2], num=9, scale=(2,3), seed=1, min_peak_diff=0.5)
    assert len(specs) == 9

@pytest.mark.test_interbreed
def test_interbreed_save_to_file():
    s1 = Spectrogram(image=np.ones((100,100)))
    s2 = s1.copy()
    outf = path_to_tmp + 'interbreed.h5'
    interbreed(specs1=[s1], specs2=[s2], num=9, output_file=outf)
    # check that spectrograms were saved to file
    fil = tables.open_file(outf, 'r')
    assert '/spec' in fil
    specs = di.load_specs(fil.root.spec)
    assert len(specs) == 9   

@pytest.mark.test_ensure_same_length
def test_ensure_same_length():
    s1 = Spectrogram(image=np.ones((99,100)))
    s2 = Spectrogram(image=np.ones((100,100)))
    s3 = Spectrogram(image=np.ones((103,100)))
    specs = ensure_same_length([s1, s2, s3], pad=True)
    for s in specs:
        assert s.tbins() == specs[2].tbins()
        assert s.fbins() == 100

@pytest.mark.test_get_label_vector
def test_get_label_vector():
    labels = [1, 1]
    box1 = [1.1, 2.3]
    box2 = [11.5, 17.3]
    spec = Spectrogram(image=np.ones(shape=(100,100)))
    spec.annotate(labels=labels, boxes=[box1,box2])
    y = spec.get_label_vector(label=1)
    assert y[0] == 0
    assert y[1] == 1 
    assert np.all(y[3:11] == 0)
    assert np.all(y[11:18] == 1)
    assert np.all(y[18:] == 0)

@pytest.mark.test_scale_freq_axis
def test_stretch_freq_axis():
    spec = Spectrogram(image=np.ones(shape=(10,20)))
    spec.image[:,5] = 0.5
    spec._scale_freq_axis(scale=2)
    assert spec.image.shape[1] == 20
    assert spec.image[0,5] == pytest.approx(1)
    assert spec.image[0,10] == pytest.approx(0.625, abs=0.001)

@pytest.mark.test_scale_freq_axis
def test_compress_freq_axis():
    spec = Spectrogram(image=np.ones(shape=(10,20)))
    spec.image[:,5] = 0.5
    spec._scale_freq_axis(scale=0.5)
    assert spec.image.shape[1] == 20
    assert spec.image[0,5] == pytest.approx(1)
    assert spec.image[0,2] == pytest.approx(0.78, abs=0.1)

@pytest.mark.test_create_tracking_data
def test_create_tracking_data_with_two_files():
    spec1 = Spectrogram(tag='file1.wav', tres=0.6) 
    spec2 = Spectrogram(tag='file2.wav', tres=0.6) 
    spec1.append(spec2)
    d = spec1.file_dict
    assert d[0] == 'file1.wav'
    assert d[1] == 'file2.wav'
    f = spec1.file_vector
    assert f[0] == 0
    assert f[1] == 0
    assert f[2] == 1
    assert f[3] == 1
    t = spec1.time_vector
    assert t[0] == 0.
    assert t[1] == 0.6
    assert t[2] == 0.
    assert t[3] == 0.6

@pytest.mark.test_crop_tracking_data
def test_crop_tracking_data_with_two_files():
    spec1 = Spectrogram(image=np.ones(shape=(100,10)), tag='file1.wav', tres=0.6) 
    spec2 = Spectrogram(image=np.ones(shape=(50,10)), tag='file2.wav', tres=0.6) 
    spec1.append(spec2)
    tvec, fvec, fdict = spec1._crop_tracking_data(tlow=0.6*80, thigh=0.6*130)
    assert fdict[0] == 'file1.wav'
    assert fdict[1] == 'file2.wav'
    assert len(tvec) == 50
    assert len(fvec) == 50
    for i in range(20):
        assert tvec[i] == (80 + i) * 0.6
        assert fvec[i] == 0
    for i in range(20,50):
        assert tvec[i] == (i - 20) * 0.6
        assert fvec[i] == 1

@pytest.mark.test_tonal_noise_reduction
def test_tonal_noise_reduction():
    img = np.array([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
    spec = Spectrogram(image=img, tres=0.5) 
    spec.tonal_noise_reduction(method='MEDIAN')
    assert spec.image[0,0] == -3
    assert spec.image[0,1] == -3
    assert spec.image[1,0] == 0
    spec.tonal_noise_reduction(method='bla')
    assert spec.image[0,0] == -3
    assert spec.image[0,1] == -3
    assert spec.image[1,0] == 0
    spec = Spectrogram(image=img, tres=0.5) 
    with pytest.raises(AssertionError):
        spec.tonal_noise_reduction(method='RUNNING_MEAN')
    spec.tonal_noise_reduction(method='RUNNING_MEAN', time_constant=10)
    assert spec.image[0,0] == -3
    assert spec.image[0,1] == -3
    assert spec.image[1,0] == pytest.approx(0.27, abs=0.01)


@pytest.mark.test_normalize
def test_normalized_spectrum_has_values_between_0_and_1(sine_audio):
    spec = MagSpectrogram(audio_signal=sine_audio, winlen=0.2, winstep=0.05, NFFT=256)
    spec.normalize()
    for i in range(spec.image.shape[0]):
        val = spec.image[0,i]
        assert 0 <= val <= 1
