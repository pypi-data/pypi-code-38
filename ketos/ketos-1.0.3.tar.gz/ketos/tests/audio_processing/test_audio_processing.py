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

""" Unit tests for the 'audio_processing' module within the ketos library
"""
import pytest
import os
import numpy as np
import scipy.signal as sg
import ketos.audio_processing.audio_processing as ap
from ketos.audio_processing.audio import AudioSignal
from ketos.audio_processing.spectrogram import Spectrogram, MagSpectrogram

current_dir = os.path.dirname(os.path.realpath(__file__))
path_to_assets = os.path.join(os.path.dirname(current_dir),"assets")
path_to_tmp = os.path.join(path_to_assets,'tmp')



@pytest.mark.test_to_decibel
def test_to_decibel_returns_decibels():
    x = 7
    y = ap.to_decibel(x)
    assert y == 20 * np.log10(x) 

@pytest.mark.test_to_decibel
def test_to_decibel_can_handle_arrays():
    x = np.array([7,8])
    y = ap.to_decibel(x)
    assert np.all(y == 20 * np.log10(x))

@pytest.mark.test_to_decibel
def test_to_decibel_returns_inf_if_input_is_negative():
    x = -7
    y = ap.to_decibel(x)
    assert np.ma.getmask(y) == True

@pytest.mark.test_blur_img
def test_uniform_image_is_unchanged_by_blurring():
    img = np.ones(shape=(10,10), dtype=np.float32)
    img_median = ap.blur_image(img,5,gaussian=False)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            assert img_median[i,j] == img[i,j]
    img_gaussian = ap.blur_image(img,9,gaussian=True)
    np.testing.assert_array_equal(img, img_gaussian)
            
@pytest.mark.test_blur_img
def test_median_filter_can_work_with_kernel_size_greater_than_five():
    img = np.ones(shape=(10,10), dtype=np.float32)
    ap.blur_image(img,13,gaussian=False)

@pytest.mark.test_apply_median_filter
def test_median_filter_works_as_expected():
    img = np.array([[1,1,1],[1,1,1],[1,1,10]], dtype=np.float32)
    img_fil = ap.apply_median_filter(img,row_factor=1,col_factor=1)
    img_res = np.array([[0,0,0],[0,0,0],[0,0,1]], dtype=np.float32)
    np.testing.assert_array_equal(img_fil,img_res)
    img = np.array([[1,1,1],[1,1,1],[1,1,10]], dtype=np.float32)
    img_fil = ap.apply_median_filter(img,row_factor=15,col_factor=1)
    assert img_fil[2,2] == 0
    img = np.array([[1,1,1],[1,1,1],[1,1,10]], dtype=np.float32)
    img_fil = ap.apply_median_filter(img,row_factor=1,col_factor=15)
    assert img_fil[2,2] == 0
    
@pytest.mark.test_apply_preemphasis
def test_preemphasis_has_no_effect_if_coefficient_is_zero():
    sig = np.array([1,2,3,4,5], np.float32)
    sig_new = ap.apply_preemphasis(sig,coeff=0)
    for i in range(len(sig)):
        assert sig[i] == sig_new[i]

def test_prepare_for_binary_cnn():
    n = 1
    l = 2
    specs = list()
    for i in range(n):
        t1 = (i+1) * 2
        t2 = t1 + l + 1
        img = np.ones(shape=(20,30))
        img[t1:t2,:] = 2.5
        s = Spectrogram(image=img)       
        s.annotate(labels=7,boxes=[t1, t2])
        specs.append(s)

    img_wid = 4
    framer = ap.FrameMakerForBinaryCNN(specs=specs, label=7, frame_width=img_wid, step_size=1, signal_width=2)
    x, y, _ = framer.make_frames()
    m = 1 + 20 - 4
    q = 4
    assert y.shape == (m*n,)
    assert x.shape == (m*n, img_wid, specs[0].image.shape[1])
    assert np.all(y[0:q] == 1)
    assert y[4] == 0
    assert np.all(x[0,2,:] == 2.5)
    assert np.all(x[1,1,:] == 2.5)

    framer = ap.FrameMakerForBinaryCNN(specs=specs, label=7, frame_width=img_wid, step_size=1, signal_width=2, equal_rep=True)
    x, y, _ = framer.make_frames()
    assert y.shape == (2*q,)
    assert np.sum(y) == q

@pytest.mark.test_append_specs
def test_append_specs():
    img = np.ones(shape=(20,30))
    s = Spectrogram(image=img)       
    merged = ap.append_specs([s,s,s])
    assert merged.image.shape[0] == 3 * s.image.shape[0]

@pytest.mark.test_filter_isolated_cells
def test_filter_isolated_spots_removes_single_pixels():
    img = np.array([[0,0,1,1,0,0],
                    [0,0,0,1,0,0],
                    [0,1,0,0,0,0],
                    [0,0,0,0,0,0],
                    [0,0,0,1,0,0]])
    
    expected = np.array([[0,0,1,1,0,0],
                        [0,0,0,1,0,0],
                        [0,0,0,0,0,0],
                        [0,0,0,0,0,0],
                        [0,0,0,0,0,0]])
    

    #Struct defines the relationship between a pixel and its neighbors.
    #If a pixel complies with this relationship, it is not removed
    #in this case, if the pixel has any neighbors, it will not be removed.
    struct=np.array([[1,1,1],
                    [1,1,1],
                    [1,1,1]])

    filtered_img = ap.filter_isolated_spots(img,struct)

    assert np.array_equal(filtered_img, expected)

