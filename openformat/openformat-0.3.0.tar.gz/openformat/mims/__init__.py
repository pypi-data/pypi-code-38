import logging
import os
import struct

import numpy as np
from scipy import ndimage

from ..util import from_buffer
from .structures import *
from .structures import _ANALYSIS_TYPES


def load_mims(filename, byte_order='<', roll_data=True):
    """
    Load a multi-isotope imaging mass spectrometry (MIMS) file.

    .. note::
        This function returns a dictionary with keys listed in the **Returns** section.

    Parameters
    ----------
    filename : str
        path to the MIMS file with .im extension
    byte_order : str
        byte order of the encoded binary data
    roll_data : bool
        whether to roll image data along the last two dimenions. Rolling the image fixes an issue
        with Cameca's encoding of pixel positions.

    Returns
    -------
    def_analysis : Def_analysis
        information about the analysis performed. See [fmt]_ for details.
    def_analysis_bis : Def_analysis_bis
        additional information about the analysis peformed. See [fmt]_ for details.
    mask_im : Mask_im
        image acquisition information. See [fmt]_ for details.
    tab_mass : list[Tab_mass]
        information about the detectors and masses. See [fmt]_ for details.
    cal_cond : Cal_cond
        information about the conditions for data acquisition. See [fmt]_ for details.
    poly_list : Poly_list
        header for element information. See [fmt]_ for details.
    polyatomique : list[Polyatomique]
        sequence of element information containers. See [fmt]_ for details.
    mask_nano : Mask_nano
        data acquisition information. See [fmt]_ for details.
    tab_Bfield_nano : tab_Bfield_nano
        information about the magnetic field. See [fmt]_ for details.
    anal_param_nano : Anal_param_nano
        parameters for the analysis. See [fmt]_ for details.
    anal_param_nano_bis : Anal_param_nano_bis
        additional parameters for the analysis. See [fmt]_ for details.
    _anal_param : bytes
        unparsed value
    _setup_soft : bytes
        unparsed value
    header_image : Header_image
        information regarding images. See [fmt]_ for details.
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames, `p` is the number
        of detectors, `w` is the width, and `h` is the height

    References
    ----------
    .. [fmt] Alain Morgand. "Format File N50 V7",
       https://www.dropbox.com/sh/gyss2uvv5ggu2vl/AACkLTMRfKjZj3PEt3H_PxY_a/manual?preview=Format+File+N50+V7.doc
    """
    mims = Structure()
    stat = os.stat(filename)

    with open(filename, 'rb') as fp:
        # Load the header
        mims['def_analysis'] = Def_analysis.from_buffer(fp, byte_order)
        try:
            analysis_type = _ANALYSIS_TYPES[mims.def_analysis.analysis_type]
        except KeyError:  # pragma: no cover
            raise ValueError(f"Found unrecognised analysis type {mims.def_analysis.analysis_type} "
                             f"(expected one of {list(_ANALYSIS_TYPES)}). Did you use the correct "
                             "byte order?")

        if analysis_type == 'IMAGE':
            mims['mask_im'] = Mask_im.from_buffer(fp, byte_order)
            mims['tab_mass'] = [Tab_mass.from_buffer(fp, byte_order) for _ in range(mims.mask_im.nb_mass)]
            mims['cal_cond'] = [Cal_cond.from_buffer(fp, byte_order) for _ in range(mims.mask_im.nb_mass)]
            mims['poly_list'] = Poly_list.from_buffer(fp, byte_order)
            mims['polyatomique'] = [Polyatomique.from_buffer(fp, byte_order) for _ in range(mims.poly_list.nb_poly)]
            mims['mask_nano'] = Mask_nano.from_buffer(fp, byte_order)
            mims['tab_Bfield_nano'] = [Tab_BField_nano.from_buffer(fp, byte_order) for _ in range(mims.mask_nano.m_nNbBField)]

            # Consume 288 dummy bytes (no idea where they come from)
            _ = fp.read(288)

            mims['anal_param_nano'] = Anal_param_nano.from_buffer(fp, byte_order)
            mims['def_analysis_bis'] = Def_analysis_bis.from_buffer(fp, byte_order)

            # Read dummy content
            mims['_anal_param'] = fp.read(416)
            mims['_setup_soft'] = fp.read(376)

            mims['anal_param_nano_bis'] = Anal_param_nano_bis.from_buffer(fp, byte_order)
            mims['header_image'] = Header_image.from_buffer(fp, byte_order)

            assert fp.tell() == mims.def_analysis.hdr_usr, \
                f"read {fp.tell()} bytes (expected {mims.def_analysis.hdr_usr})"

            fmt = f'int[{mims.mask_im.cycle_number}, {mims.header_image.n}, ' \
                f'{mims.header_image.w}, {mims.header_image.h}]'

            mims['data'] = from_buffer(fmt, fp, byte_order)
            if roll_data:
                mims['data'] = np.roll(mims['data'], 1, axis=(2, 3))
        else:  # pragma: no cover
            raise NotImplementedError(f"{analysis_type} is not implemented")

        assert fp.tell() == stat.st_size, f"consumed {fp.tell()} bytes (expected {stat.st_size})"
        return mims


def infer_hot_pixels(data, num_outliers, kernel_size=3, outlier_factor=3, min_count=1,
                     max_repeat_fraction=0.1, num_nonzero=None, return_filtered=False):
    """
    Identify hot pixels due to correlated noise.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    num_outliers : int
        number of times a pixel needs to be labelled as an outlier in different
        detectors to be considered correlated noise
    kernel_size : int
        size of the kernel used for median filtering
    outlier_factor : float
        factor multiplying the median-filtered image to define the threshold that
        serves to flag a pixel as an outlier
    min_count : float
        minimum count used to determine the threshold if the median-filtered image
        is smaller
    max_repeat_fraction : float
        maximum fraction of frames in which a pixel is allowed to be a hot pixel.
        If a pixel is a hot pixel candidate in more than `max_repeat_fraction` of
        all frames, it is not considered a hot pixel.
    num_nonzeros : int
        number of detectors in which a hot pixel candidate must be non-zero. Default
        is all detectors.
    return_filtered : bool
        whether to return the median-filtered image

    Returns
    -------
    mask : np.ndarray
        binary mask of hot pixels with shape `(n, w, h)`
    """
    data = np.asarray(data)
    assert data.ndim == 4, f"expected `data` to have 4 dimensions; got {data.ndim}"
    assert 1 <= num_outliers <= data.shape[1], "number of ouliers must be positive " \
        "and <= the number of detectors"
    num_nonzero = num_nonzero or data.shape[1]

    # Apply a median filter to identify "typical" counts for this area
    filtered = ndimage.median_filter(data, (1, 1, kernel_size, kernel_size))
    # Flag any pixels as hot-pixel candidates if they exceed a given threshold
    candidates = data >= outlier_factor * np.maximum(filtered, min_count)
    # Flag as a hot pixel if a pixel is a candidate in at least num_outliers detectors
    mask = np.sum(candidates, axis=1) >= num_outliers
    # Remove any hot pixels that have zero count in any detector
    mask &= np.sum(data > 0, axis=1) >= num_nonzero
    # Remove any hot pixels that occur in more than max_repeat_fraction of all frames
    mask &= (np.mean(mask, axis=0) < max_repeat_fraction)[None]
    return (mask, filtered) if return_filtered else mask


def apply_mask(data, mask, replacement_values):
    """
    Replace all values in `data` by `replacement_values` where `mask` is `True`.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    mask : np.ndarray
        binary mask of hot pixels with shape `(n, w, h)`
    replacement_values : np.ndarray
        tensor of replacement values with the same shape as `data`, a list of the
        same length as non-zero elements in `mask`, or a scalar
    """
    data = np.asarray(data)
    replacement_values = np.asarray(replacement_values)
    # Repeat the mask along the detector dimension so we can index
    mask = np.repeat(mask[:, None], data.shape[1], 1)

    cleaned = data.copy()
    if cleaned.shape == replacement_values.shape:
        cleaned[mask] = replacement_values[mask]
    else:
        cleaned[mask] = replacement_values
    return cleaned


def remove_hot_pixels(data, num_outliers=3, kernel_size=3, outlier_factor=1.999, min_count=.5,
                      max_repeat_fraction=0.1, num_nonzero=None):
    """
    Remove hot pixels due to correlated noise.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    num_outliers : int
        number of times a pixel needs to be labelled as an outlier in different
        detectors to be considered correlated noise
    kernel_size : int
        size of the kernel used for median filtering
    outlier_factor : float
        factor multiplying the median-filtered image to define the threshold that
        serves to flag a pixel as an outlier
    min_count : float
        minimum count used to determine the threshold if the median-filtered image
        is smaller
    max_repeat_fraction : float
        maximum fraction of frames in which a pixel is allowed to be a hot pixel.
        If a pixel is a hot pixel candidate in more than `max_repeat_fraction` of
        all frames, it is not considered a hot pixel.
    num_nonzeros : int
        number of detectors in which a hot pixel candidate must be non-zero. Default
        is all detectors.

    Returns
    -------
    cleaned : np.ndarray
        cleaned data tensor with the same shape as `data` with hot pixels replaced
        by median-filtered pixels
    """
    mask, filtered = infer_hot_pixels(data, num_outliers, kernel_size, outlier_factor,
                                      min_count, max_repeat_fraction, num_nonzero, True)
    return apply_mask(data, mask, filtered)


def infer_translations(data, padding=8, method='sequential'):
    """
    Infer translations between successive frames to increase sharpness of aggregated
    nanoSIMS images.

    Parameters
    ----------
    data : np.ndarray
        data tensor for a single detector with shape `(n, w, h)`, where `n` is the
        number of frames, `w` is the width, and `h` is the height
    padding : int
        padding applied to the data tensor before computing correlations
    method : str
        method used to align different frames. 'sequential' aggregates frames in
        order and aligns successive frames with the current best aggregate.

    Returns
    -------
    translations : np.ndarray
        sequence of translations that should be applied to align the images
    """
    assert data.ndim == 3, f"expected `data` to have 3 dimensions; got {data.ndim}"
    data = np.pad(data, [(0, 0), (padding, padding), (padding, padding)], 'constant')

    if method == 'sequential':
        translations = [(0, 0)]
        aggregate = data[0]
        for frame in data[1:]:
            transformed = np.fft.fft2(frame[::-1, ::-1])
            convolution = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(aggregate) * transformed))
            dx, dy = np.unravel_index(np.argmax(convolution), convolution.shape)
            dx -= convolution.shape[0] // 2 - 1
            dy -= convolution.shape[1] // 2 - 1
            translations.append((dx, dy))
            aggregate += np.roll(frame, (dx, dy), (0, 1))
    else:
        raise NotImplementedError

    # Center the translations
    translations = np.asarray(translations)
    translations -= np.median(translations, axis=0).astype(int)
    return translations


def apply_translations(data, translations, padding=8):
    """
    Apply the sequence of translations to the data.

    Parameters
    ----------
    data : np.ndarray
        data tensor with shape `(n, p, w, h)`, where `n` is the number of frames,
        `p` is the number of detectors, `w` is the width, and `h` is the height
    translations : np.ndarray
        sequence of translations that should be applied to align the images

    Returns
    -------
    translated : np.ndarray
        translated data tensor with shape `(n, p, w + 2 * padding, h + 2 * padding)`
    """
    data = np.asarray(data).copy()
    translations = np.asarray(translations)
    assert data.ndim == 4, f"expected `data` to have 4 dimensions; got {data.ndim}"
    expected_shape = (data.shape[0], 2)
    assert translations.shape == expected_shape, "expected `translations` to have shape " \
        f"{expected_shape}; got {translations.shape}"

    # Apply the translations by rolling the image
    translated = []
    for frame, translation in zip(data, translations):
        frame = np.pad(frame, [(0, 0), (padding, padding), (padding, padding)], 'constant')
        translated.append(np.roll(frame, translation, (1, 2)))

    return np.asarray(translated)


def process_image_data(filename, alignment_detector, padding=8, load_mims_kwargs=None,
                       remove_hot_pixels_kwargs=None, infer_translations_kwargs=None):
    """
    Process a raw .im file, remove hot pixels, and align the frames of each image. Returns a
    dictionary of cleaned aligned data and relevent information.

    .. note::
        This function returns a dictionary with keys listed in the **Returns** section.

    Parameters
    ----------
    filename : str
        path to the MIMS file with .im extension
    alignment_detector : str
        the element or element combination to use for frame alignment e.g. '12C 14N' or '32Se'
    padding : int
        number of border pixels to allow image shifts without data loss
    load_mims_kwargs : dict, optional
        dictionary with keywords passed to the :func:`~mims.load_mims` call used to load the raw
        data
    remove_hot_pixel_kwargs : dict, optional
        dictionary with keywords passed to the :func:`~mims.remove_hot_pixels` call used to remove
        hot pixels from the dataset
    infer_translations_kwargs : dict, optional
        dictionary with keywords passed to the :func:`~mims.infer_translations` call used to
        calculate image alignment shifts

    Returns
    -------
    total_lookup : dict
        cleaned, aligned detector data keyed by detector name
    detector_names : list
        sequence of detector names
    cleaned : list
        sequence of detector data with hot pixels replaced by median-filtered pixels
    translations : np.array
        sequence of horizontal and vertical translations to align different scans
    aligned : list
        sequence of aligned detector data
    image_shape : tuple
        width and height of the image in pixels
    image_size : tuple
        width and height of the image in micrometers
    pixel_size : float
        size of each pixel in micrometers
    alignment_detector_index : int
        index of detector used for aligning different scans
    se_detector_index : int
        index of the detector collecting secondary electron data
    """
    # function kwargs
    load_mims_kwargs = load_mims_kwargs or {}
    remove_hot_pixels_kwargs = remove_hot_pixels_kwargs or {}
    infer_translations_kwargs = infer_translations_kwargs or {}


    # processing the image data to return a dictionary containing the various results
    mims = load_mims(filename, **load_mims_kwargs)

    w, h = mims.data.shape[2:]
    # Find the index of the secondary electron detector which has exactly zero "mass"
    se_index = [mass.mass_amu for mass in mims.tab_mass].index(0)
    mims.tab_mass[se_index]['mass']['string'] = 'SE'

    detector_names = [mass.mass.string.strip() for mass in mims.tab_mass]
    alignment_index = detector_names.index(alignment_detector)
    pixel_size = mims.header_image.raster / w * 1e-3

    # Remove hot pixels after dropping the secondary electron detector
    data_without_se = np.delete(mims.data, se_index, axis=1)
    cleaned = remove_hot_pixels(data_without_se, **remove_hot_pixels_kwargs)

    # Re-insert the secondary electron detector
    cleaned = np.insert(cleaned, se_index, mims.data[:, se_index], axis=1)

    # Infer translations (drift) from one of the detectors
    translations = infer_translations(cleaned[:, alignment_index], padding=padding,
                                      **infer_translations_kwargs)

    # Apply the translations
    aligned = apply_translations(cleaned, translations, padding=padding)

    # Chop off the padding
    aligned = aligned[:, :, padding:-padding, padding:-padding]

    total_lookup = dict(zip(detector_names, aligned.sum(axis=0)))

    image_data = {
        "total_lookup": total_lookup,
        "detector_names": detector_names,
        "cleaned": cleaned,
        "translations": translations,
        "aligned": aligned,
        "image_shape": (w, h),
        "image_size": (w * pixel_size, h * pixel_size),
        "pixel_size": pixel_size,
        "alignment_detector_index:": alignment_index,
        "se_detector_index:": se_index,
    }

    return image_data
