# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
from astropy.coordinates.matrix_utilities import rotation_matrix


def calculate_sky_offset(xoff, yoff, sky_pa):
    """
    Convert pixel offset to sky offset in arcseconds

    Arguments
    ---------
    xoff, yoff : float
        desired pixel offsets
    sky_pa : float
        current instrument PA
    """
    px_scale = 0.081  # arcseconds per pixel
    flipEW = True  # is E to the right in the image?
    EofN = True  # does increasing rotator PA move us to E?
    paOff = 69.3  # pa when rotator = 0

    if EofN:
        theta = sky_pa - paOff
    else:
        theta = -sky_pa - paOff
    # only take 3d of 3d rotation matrix
    rmat = rotation_matrix(theta)[:2, :2]

    # +ve shifts should move stars right and up
    # offset for skyPA = 0 are:
    ra_shift_arcsecs = -xoff*px_scale if flipEW else xoff*px_scale
    dec_shift_arcsecs = -yoff*px_scale
    pix_shift = np.array([ra_shift_arcsecs, dec_shift_arcsecs])
    return rmat.dot(pix_shift)
