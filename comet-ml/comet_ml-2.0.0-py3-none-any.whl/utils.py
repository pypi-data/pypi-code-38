# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import calendar
import io
import json
import logging
import math
import os
import os.path
import tempfile
import time
from datetime import datetime

import six

from ._logging import UPLOAD_FILE_OS_ERROR
from .exceptions import FileIsTooBig

LOGGER = logging.getLogger(__name__)


def is_iterable(value):
    try:
        iter(value)
        return True

    except TypeError:
        return False


def is_list_like(value):
    """ Check if the value is a list-like
    """
    if is_iterable(value) and not isinstance(value, six.string_types):
        return True

    else:
        return False


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def local_timestamp():
    """ Return a timestamp in a format expected by the backend (milliseconds)
    """
    now = datetime.utcnow()
    timestamp_in_seconds = calendar.timegm(now.timetuple()) + (now.microsecond / 1e6)
    timestamp_in_milliseconds = int(timestamp_in_seconds * 1000)
    return timestamp_in_milliseconds


def wait_for_empty(check_function, timeout, verbose=False, sleep_time=1):
    """ Wait up to TIMEOUT seconds for the messages queue to be empty
    """
    end_time = time.time() + timeout

    while check_function() is False and time.time() < end_time:
        if verbose is True:
            LOGGER.info("Still uploading")
        time.sleep(sleep_time)


def read_unix_packages():
    package_status_file = "/var/lib/dpkg/status"
    if os.path.isfile(package_status_file):
        with open(package_status_file, "r") as f:
            status = f.read()
        package = None
        os_packages = []
        for line in status.split("\n"):
            if line.startswith("Package: "):
                package = line[9:]
            if line.startswith("Version: "):
                version = line[9:]
                if package is not None:
                    os_packages.append((package, version))
                package = None
        os_packages_list = sorted(
            [("%s=%s" % (package, version)) for (package, version) in os_packages]
        )
        return os_packages_list
    else:
        return None


def image_data_to_file_like_object(
    image_data,
    file_name,
    image_format,
    image_scale,
    image_shape,
    image_colormap,
    image_minmax,
    image_channels,
):
    """
    Ensure that the given image_data is converted to a file_like_object ready
    to be uploaded
    """
    try:
        import PIL.Image
    except ImportError:
        PIL = None

    ## Conversion from standard objects to image
    ## Allow file-like objects, numpy arrays, etc.
    if hasattr(image_data, "numpy"):  # pytorch tensor
        array = image_data.numpy()
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif hasattr(image_data, "eval"):  # tensorflow tensor
        array = image_data.eval()
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif PIL is not None and isinstance(image_data, PIL.Image.Image):  # PIL.Image
        ## filename tells us what format to use:
        if file_name is not None and "." in file_name:
            _, image_format = file_name.rsplit(".", 1)
        fp = image_to_fp(image_data, image_format)

        return fp
    elif image_data.__class__.__name__ == "ndarray":  # numpy array
        fp = array_to_image_fp(
            image_data,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif hasattr(image_data, "read"):  # file-like object
        return image_data
    elif isinstance(image_data, (tuple, list)):  # list or tuples
        try:
            import numpy
        except ImportError:
            LOGGER.error("The Python library numpy is required for this operation")
            return None
        array = numpy.array(image_data)
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )
        return fp
    else:
        LOGGER.error("invalid image file_type: %s", type(image_data))
        if PIL is None:
            LOGGER.error("Consider installing the Python Image Library, PIL")
        return None


def array_to_image_fp(
    array,
    image_format,
    image_scale,
    image_shape,
    image_colormap,
    image_minmax,
    image_channels,
):
    """
    Convert a numpy array to an in-memory image
    file pointer.
    """
    try:
        import PIL.Image
        import numpy as np
        from matplotlib import cm
    except ImportError:
        LOGGER.error(
            "The Python libraries PIL, numpy, and matplotlib are required for this operation"
        )
        return

    ## Handle image transformations here
    ## End up with a 0-255 PIL Image
    if image_minmax is not None:
        minmax = image_minmax
    else:  # auto minmax
        minmax = [array.min(), array.max()]
        if minmax[0] == minmax[1]:
            minmax[0] = minmax[0] - 0.5
            minmax[1] = minmax[1] + 0.5
        minmax[0] = math.floor(minmax[0])
        minmax[1] = math.ceil(minmax[1])
    ## if a shape is given, try to reshape it:
    if image_shape is not None:
        try:
            ## array shape is opposite of image size(width, height)
            array = array.reshape(image_shape[1], image_shape[0])
        except Exception:
            LOGGER.info("WARNING: invalid image_shape; ignored", exc_info=True)
    ## If 3D, but last array is flat, make it 2D:
    if len(array.shape) == 3 and array.shape[-1] == 1:
        array = array.reshape((array.shape[0], array.shape[1]))
    elif len(array.shape) == 1:
        ## if 1D, make it 2D:
        array = np.array([array])
    if image_channels == "first" and len(array.shape) == 3:
        array = np.moveaxis(array, 0, -1)
    ### Ok, now let's colorize and scale
    if image_colormap is not None:
        ## Need to be in range (0,1) for colormapping:
        array = rescale_array(array, minmax, (0, 1), "float")
        try:
            cm_hot = cm.get_cmap(image_colormap)
            array = cm_hot(array)
        except Exception:
            LOGGER.info("WARNING: invalid image_colormap; ignored", exc_info=True)
        ## rescale again:
        array = rescale_array(array, (0, 1), (0, 255), "uint8")
        ## Convert to RGBA:
        image = PIL.Image.fromarray(array, "RGBA")
    else:
        ## Rescale (0, 255)
        array = rescale_array(array, minmax, (0, 255), "uint8")
        image = PIL.Image.fromarray(array)
    if image_scale != 1.0:
        image = image.resize(
            (int(image.size[0] * image_scale), int(image.size[1] * image_scale))
        )
    ## Put in a standard mode:
    if image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGB")
    return image_to_fp(image, image_format)


def image_to_fp(image, image_format):
    """
    Convert a PIL.Image into an in-memory file
    pointer.
    """
    fp = io.BytesIO()
    image.save(fp, format=image_format)  # save the content to fp
    fp.seek(0)
    return fp


def rescale_array(array, old_range, new_range, dtype):
    """
    Given a numpy array in an old_range, rescale it
    into new_range, and make it an array of dtype.
    """
    try:
        import numpy as np
    except ImportError:
        LOGGER.error("The Python library numpy is required for this operation")
        return

    old_min, old_max = old_range
    if array.min() < old_min or array.max() > old_max:
        ## truncate:
        array = np.clip(array, old_min, old_max)
    new_min, new_max = new_range
    old_delta = float(old_max - old_min)
    new_delta = float(new_max - new_min)
    if old_delta == 0:
        return ((array - old_min) + (new_min + new_max) / 2).astype(dtype)
    else:
        return (new_min + (array - old_min) * new_delta / old_delta).astype(dtype)


def write_file_like_to_tmp_file(file_like_object):
    # Copy of `shutil.copyfileobj` with binary / text detection

    buf = file_like_object.read(1)

    # Detect binary/text
    if isinstance(buf, six.binary_type):
        tmp_file_mode = "w+b"
    else:
        tmp_file_mode = "w+"

    tmp_file = tempfile.NamedTemporaryFile(mode=tmp_file_mode, delete=False)

    tmp_file.write(buf)

    # Main copy loop
    while True:
        buf = file_like_object.read(16 * 1024)

        if not buf:
            break

        tmp_file.write(buf)

    return tmp_file.name


def data_to_fp(data):
    fp = io.StringIO()
    if isinstance(data, str):
        if six.PY2:
            data = unicode(data)  # noqa
        fp.write(data)
    else:
        try:
            json.dump(data, fp)
        except Exception:
            LOGGER.error("Failed to log asset data as JSON or str", exc_info=True)
            return None
    fp.seek(0)
    return fp


def check_max_file_size(file_path, max_upload_size):
    """ Check if a file identified by its file path is bigger than the maximum
    allowed upload size. Raises FileIsTooBig if the file is greater than the
    upload limit.
    """

    # Check the file size before reading it
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_upload_size:
            raise FileIsTooBig(file_path, file_size, max_upload_size)

    except OSError:
        LOGGER.error(UPLOAD_FILE_OS_ERROR, file_path, exc_info=True)
        raise


def is_valid_file_path(file_path):
    """ Check if the given argument is corresponding to a valid file path,
    ready for reading
    """
    try:
        if os.path.isfile(file_path):
            return True
        else:
            return False
    # We can receive lots of things as arguments
    except (TypeError, ValueError):
        return False
