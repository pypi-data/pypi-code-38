import numpy as np


def cart2pol(x, y, units='deg', ref=(0, 0)):
    """Convert cartesian coordinates to polar coordinates.

    Args:
        x
        y
    Kwargs:
        units (string): 'deg' for degrees, 'rad' for radians.
        ref (list or tuple): The reference point (x, y).
    Returns:
        (theta, radius)
    """
    x -= ref[0]
    y -= ref[1]
    radius = np.hypot(x, y)
    theta = np.arctan2(y, x)
    if units in 'deg':
        theta *= 180.0 / np.pi

    return theta, radius


def pol2cart(theta, radius, units='deg', ref=(0, 0)):
    """Convert polar coordinates to cartesian coordinates.

    Args:
        theta
        radius
    Kwargs:
        units (string): 'deg' for degrees, 'rad' for radians.
        ref (list or tuple): The reference point (x, y).
    Returns:
        (x, y)
    """
    if units in 'deg':
        theta *= np.pi / 180.0
    x = radius * np.cos(theta) + ref[0]
    y = radius * np.sin(theta) + ref[1]
    return x, y


def cart2sph(x, y, z, units='deg', ref=(0, 0, 0)):
    """Convert cartesian coordinates to spherical coordinates.

    Args:
        x
        y
        z
    Kwargs:
        units (string): 'deg' for degrees, 'rad' for radians.
        ref (list or tuple): The reference point (x, y, z).
    Returns:
        (elevation, azimuth, radius)
    """
    x -= ref[0]
    y -= ref[1]
    z -= ref[2]
    radius = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    azimuth = np.arctan2(y, x)
    elevation = np.arctan2(z, np.sqrt(x ** 2 + y ** 2))
    if units in 'deg':
        azimuth *= 180.0 / np.pi
        elevation *= 180.0 / np.pi
    return elevation, azimuth, radius


def sph2cart(elevation, azimuth, radius, units='deg', ref=(0, 0, 0)):
    """Convert spherical coordinates to cartesian coordinates.

    Args:
        elevation
        azimuth
        radius
    Kwargs:
        units (string): 'deg' for degrees, 'rad' for radians.
        ref (list or tuple): The reference point (x, y, z).
    Returns:
        (x, y, z)
    """
    if units in 'deg':
        azimuth *= np.pi / 180.0
        elevation *= np.pi / 180.0

    x = radius * np.cos(elevation) * np.cos(azimuth) + ref[0]
    y = radius * np.cos(elevation) * np.sin(azimuth) + ref[1]
    z = radius * np.sin(elevation) + ref[2]

    return x, y, z
