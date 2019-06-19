import numpy as np
import astropy.io.fits as fits
import pytest
import bpm.image_processing as image_processing
import bpm.test.test_utils as test_utils
import bpm.image_utils as image_utils

def test_process_bias_frames():
    bad_pixel_locations = test_utils.generate_bad_pixel_locations(94, 100, 10)
    bias_frames = [test_utils.generate_test_bias_frame(bad_pixel_locations) for index in range(0,10)]

    bias_mask = image_processing.process_bias_frames(bias_frames, mask_threshold=10)
    flagged_pixels = np.where(bias_mask == True)

    assert np.shape(bias_mask) == np.shape(bias_frames[0].data)
    assert set(bad_pixel_locations[0]) == set(flagged_pixels[0])
    assert set(bad_pixel_locations[1]) == set(flagged_pixels[1])


def test_process_dark_frames():
    bad_pixel_locations = test_utils.generate_bad_pixel_locations(94, 100, 10)
    dark_frames = [test_utils.generate_test_dark_frame(bad_pixel_locations) for index in range(0,10)]

    dark_mask = image_processing.process_dark_frames(dark_frames)
    flagged_pixels = np.where(dark_mask==True)

    assert np.shape(dark_mask) == np.shape(dark_frames[0].data)
    assert set(flagged_pixels[0]) == set(bad_pixel_locations[0])
    assert set(flagged_pixels[1]) == set(bad_pixel_locations[1])


def test_process_flat_frames():
    base_image_mean = 22000
    base_image_std = 1000
    bad_pixel_locations = test_utils.generate_bad_pixel_locations(94, 100, 10)

    flat_frames = [test_utils.generate_test_flat_frame(bad_pixel_locations,
                                                       base_image_mean - 2000*index,
                                                       base_image_std - 50*index) for index in range(0,10)]

    flat_mask = image_processing.process_flat_frames(flat_frames, mask_threshold=10)
    flagged_pixels = np.where(flat_mask == True)

    assert np.shape(flat_mask) == np.shape(flat_frames[0].data)
    assert set(bad_pixel_locations[0]) == set(flagged_pixels[0])
    assert set(bad_pixel_locations[1]) == set(flagged_pixels[1])


def test_get_slices_from_header_section():
    test_header_string_1 = '[3100:3135, 1:2048]'
    test_header_string_2 = '[3100:3135,1:2048]'

    assert image_utils.get_slices_from_header_section(test_header_string_1) ==\
           (slice(0, 2048, 1), slice(3099, 3135, 1))

    assert image_utils.get_slices_from_header_section(test_header_string_2) ==\
           (slice(0, 2048, 1), slice(3099, 3135, 1))
