"""
Methods for general processing of geospatial and satellite data
"""

def normalize(x, lower, upper):
    """
    Normalize an array to a given bound interval
    """
    import numpy

    x_max = numpy.max(x)
    x_min = numpy.min(x)

    m = (upper - lower) / (x_max - x_min)
    x_norm = (m * (x - x_min)) + lower

    return x_norm


def true_color(a, factor=2.5):
    """
    Apply "true color" transformation to ndarray
    """
    return factor*a


def stack_bands(bands):
    """
    Stack bands adding a third dimension to the front of the array
    """
    from functools import reduce
    import numpy

    bands = reduce(lambda x, xn: numpy.dstack([x, xn]), bands)
    bands = numpy.moveaxis(bands, -1, 0)

    return bands


def save_jpeg_rgb(bands, src_profile, fp_dst, band_count=3, write_xml=False):
    """
    Save image data as JPEG RGB formatted image

    Example
    =======
    First Reorder and normalize - R, G, B
    >>> bands = stack_bands([normalize(true_color(x, 2.5), 0, 255) for x in bands])

    Save as standard RGB JPEG
    >>>save_jpeg_rgb(bands, src_profile, fp_dst)
    """
    import rasterio

    jpg_profile = {
        "driver": "JPEG",
        "dtype": "uint8",
        "width": src_profile["width"],
        "height": src_profile["height"],
        "count": band_count,
        }

    if write_xml:
        jpg_profile.update({
            "nodata": src_profile["nodata"],
            "crs": src_profile["crs"],
            "transform": src_profile["transform"],
        })


    # Write normalized RGB data to jpeg
    with rasterio.open(fp_dst, "w", **jpg_profile) as dst:
        dst.write(bands.astype("uint8"))
