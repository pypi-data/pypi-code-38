#!/usr/bin/env python

"""qalign.py

    Functions to align a reciprocal lattice to CCD data for ALS BL402
    *) Import CCD .fits files produced by BCS InstrumentScans or snapshots
    *) BCS data file format, motor & data headers used by ALS beamline 4.0.2
    *) BCS = Beamline Control Systems; ALS = Advanced Light Source
"""

__author__ = "Padraic Shafer"
__copyright__ = "Copyright (c) 2018-2019, Padraic Shafer"
__credits__ = [__author__, ]
__license__ = ""
__maintainer__ = "Padraic Shafer"
__email__ = "PShafer@lbl.gov"
__status__ = "Development"

from als.milo import __version__, __date__

import logging
import sys
import os
from collections import namedtuple

import numpy as np
import pandas as pd
from numpy import pi, cos, sin, deg2rad, cross, array, empty, matrix, dot
from numpy import newaxis, isfinite
from numpy import linspace, outer, sum, product, zeros, roots, square, sqrt
from numpy.linalg import norm, solve, lstsq, tensorsolve
from astropy.io import fits
from sys import exit
import matplotlib.pyplot as plt
import matplotlib.cm as cmx

from qimage import Diffractometer402, Polarization, print_diffractometer
from qimage import QSpacePath, ResonanceProfile
from qscan import AngleOffsets, OrthoLatticeABC, HKL
from qscan import OrthoReciprocalLatticeQabc, OrthoReciprocalVector

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    DATA STRUCTURES    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# class Defaults:
#   *) Default values used internally by functions in this script
Defaults = namedtuple("Defaults", ["output_dir"])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    GLOBALS    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# __defaults__ = Defaults(
#     output_dir=os.getcwd(),
#     )

__default_output_dir = os.getcwd()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_default_chamber_params():
    """Get dict() of suitable default_chamber_params that can be customized.

        RETURNS: Copy of Diffractometer402.default_chamber_params
    """

    return(Diffractometer402.default_chamber_params.copy())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def set_output_dir(format, **kwargs):
    """Sets default output directory using supplied format and keyword params.

        format: Format string for output directory using keywords;
            *) {base}/... is implied
        kwargs: (keyword = value) pairs for keywords used in 'format'

        RETURNS: Generated output directory as string

        !!! Side Effects !!!
            *) generated directory is created if it does not already exist
            *) generated directory is set as global __defaults__.output_dir
    """

    global __default_output_dir

    if not format.startswith("{base}"):
       format = "{base}/" + format

    output_dir = format.format(**kwargs)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    __default_output_dir = output_dir

    return(output_dir)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_output_dir():
    """Gets default output path.

        RETURNS: global __defaults__.output_dir
    """

    global __default_output_dir

    return(__default_output_dir)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def show_motor_params(primary_hdu):
    """Dumps motor values from CCD .fits header to the console standard output.

        primary_hdu: Metadata from primary Header Data Unit of FITS file

        RETURNS: None

        !!! Side Effects !!!
            *) Prints selected metadata from HDU to console standard output.
    """

    print 'Beamline Energy   : ' + str(primary_hdu['Beamline Energy']) + ' eV'
    print 'Bottom Rotary Seal: ' + str(primary_hdu['Bottom Rotary Seal']) + ' deg'
    print 'Top Rotary Seal   : ' + str(primary_hdu['Top Rotary Seal']) + ' deg'
    print 'Flip              : ' + str(primary_hdu['Flip']) + ' deg'
    print 'Twice Top Offset  : ' + str(primary_hdu['Twice Top Offset']) + ' deg'

    energy = primary_hdu['Beamline Energy']
    bottom = primary_hdu['Bottom Rotary Seal']
    top = primary_hdu['Top Rotary Seal']
    flip = primary_hdu['Flip']
    offset_top = primary_hdu['Twice Top Offset'] / 2
    offset_flip = 0
    offset_ccd = -18.68

    if ('Top Offset' in primary_hdu):
        offset_top = primary_hdu['Top Offset']
        print 'Top Offset        : ' + str(offset_top) + ' deg'
    if ('Flip Offset' in primary_hdu):
        offset_flip = primary_hdu['Flip Offset']
        print 'Flip Offset       : ' + str(offset_flip) + ' deg'
    if ('CCD Offset' in primary_hdu):
        offset_ccd = primary_hdu['CCD Offset']
        print 'CCD Offset        : ' + str(offset_ccd) + ' deg'

    wavelength = 1239.842 / energy
    twotheta = bottom - offset_ccd
    truetop = top - offset_top
    incidence = bottom - truetop
    chi = flip - offset_flip

    print ''
    print 'Wavelength : ' + str(wavelength) + ' nm'
    print 'Detector   : ' + str(twotheta) + ' deg'
    print 'Incidence  : ' + str(incidence) + ' deg'
    print 'Chi        : ' + str(chi) + ' deg'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def load_image(filename):
    """Reads BL402 CCD header data from FITS file (.fits).

        fits_file_path: Fully qualified file name for FITS file.

        RETURNS: (CCD_image_metadata, CCD_image_HDU)
            *) CCD_image_metadata: Metadata from primary Header Data Unit
            *) CCD_image_HDU: Header Data Unit for CCD image data

        !!! Side Effects !!!
            *) Prints selected metadata from HDU to console standard output.
    """

    hdulist = fits.open(fits_file_path)
    logging.info("Opening FITS data file: {}".format(fits_file_path))
    logging.info("...data structure: {}".format(hdulist.info()))

    show_motor_params(hdulist[0].header)

    # let's assume, the last entry is the image.
    return (hdulist[0].header, hdulist[-1])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_image_model(image_array, ccd_pairs=None, max_I=None, min_I=None):
    """Display the CCD image data, overlaid with supplied RLU (h,k,L) points.

        image_array: 2D array of intensity data to plot.
            *) Row order is automatically reversed to accommodate FITS format.
        ccd_pairs: 2D coordinates, in units of image pixels.
            *) Pixels at these coordinates are indicated by colored markers.
            *) Supplied values typically correspond to (h,k,L) points in model.
        max_I: Upper limit of color scale is mapped to this intensity value.
        min_I: Lower limit of color scale is mapped to this intensity value.

        RETURNS: None

        !!! Side Effects !!!
            *) Displays plotted data on screen.
            *) Left panel shows color scale mapped linearly to intensity
            *) Right panel shows color scale mapped to log(intensity)
    """

    if ccd_pairs is None:
        ccd_pairs = array([
                            [ [0, 0] ]
                        ])
    logging.info(
        "plot_image_model (ccd_pairs) [{}]: {}".format(
            ccd_pairs.shape,
            ccd_pairs,
            )
        )
    ccd_pairs_shape = array(ccd_pairs.shape)
    ccd_pairs_flat_shape = ccd_pairs_shape[-2:].copy()
    ccd_pairs_flat_shape[0] *= product(ccd_pairs_shape[:-2])
    ccd_pairs = ccd_pairs.reshape(*ccd_pairs_flat_shape)
    logging.debug(
        "plot_image_model (reshaped ccd_pairs) [{}]: {}".format(
            ccd_pairs.shape,
            ccd_pairs,
            )
        )

    img_display_array = image_array[::-1]

    if max_I is None:
        max_I = img_display_array.max()
    if min_I is None:
        min_I = img_display_array.min()

    ax1 = plt.subplot(1,2,1)
    im1 = ax1.imshow(img_display_array)
    im1.set_clim(min_I, max_I)
    plt.colorbar(im1)

    ax2 = plt.subplot(1,2,2)
    im2 = ax2.imshow(np.log10(abs(img_display_array)))
    plt.colorbar(im2)

    ax1.scatter(x=ccd_pairs[:,0], y=(1024-ccd_pairs[:,-1]), s=40, facecolors='none', edgecolors='m')
    ax1.set_xlim([0,1024])
    ax1.set_ylim([1024,0])

    ax2.scatter(x=ccd_pairs[:,0], y=(1024-ccd_pairs[:,-1]), s=40, facecolors='none', edgecolors='m')
    ax2.set_xlim([0,1024])
    ax2.set_ylim([1024,0])

#	plt.show()
    plt.show(block=True)

    return

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ccd_rlu_points(primary_hdu, image_array, hk_pairs=None, lattice=None):
    """Return an array of CCD coordinates, corresponding to RLU (h,k) points.

        primary_hdu: Metadata from primary Header Data Unit of FITS file.
            *) Used to construct reciprocal space model for this CCD image.
        image_array: 2D array of intensity data, used for coordinate mapping.
            *) Array shape defines CCD image pixel coordinates for hk_pairs.
        hk_pairs: Array of 2D coordinates, (h, k), in reciprocal lattice units.
            *) Array can have any shape, with innermost indices being 2D.
            *) e.g., [M x N x 2]
            *) DEFAULT value: [[ [0, 0] ]]; shape = [1 x 1 x 2]
        lattice: OrthoLatticeABC object.
            *) DEFAULT: a=b=c=(2*pi) ; all angles = 0. (qa,qb,qc)==(h,k,L)

        RETURNS: Array of 2D coordinates, in units of image pixels.
            *) Array has same shape as input array, hk_pairs

        !!! Side Effects !!!
            *) None
    """

    if hk_pairs is None:
        hk_pairs = array([
                            [ [0, 0] ]
                        ])
    hk_pairs_shape = array(hk_pairs.shape)
# 	print "hk_pairs_shape (#1)",
# 	print hk_pairs_shape
    # .copy() necessary to not overwrite original
    hk_pairs_flat_shape = hk_pairs_shape[-2:].copy()
# 	print "hk_pairs_shape (#2)",
# 	print hk_pairs_shape
    hk_pairs_flat_shape[0] *= product(hk_pairs_shape[:-2])
# 	print "hk_pairs_shape (#3)",
# 	print hk_pairs_shape
    hk_pairs = hk_pairs.reshape(*hk_pairs_flat_shape)
# 	print "hk_pairs_shape",
# 	print hk_pairs_shape
# 	print "hk_pairs_flat_shape",
# 	print hk_pairs_flat_shape
# 	print "hk_pairs_flat",
# 	print hk_pairs.shape,
# 	print hk_pairs
# 	exit()

    if lattice is None:
        lattice = qscan.OrthoLatticeABC(
            a=2*pi,  # nm
            b=2*pi,  # nm
            c=2*pi,  # nm

            offsets=qscan.AngleOffsets(
                incidence = 0,    # degrees
                transverse = 0,    # degrees
                azimuth = 0,    # degrees
            )
        )

    # TODO: Replace header extraction with CcdImageFromFITS object
    # TODO: Replace print() commands with logging commands

    energy = primary_hdu['Beamline Energy']
    bottom = primary_hdu['Bottom Rotary Seal']
    top = primary_hdu['Top Rotary Seal']
    flip = primary_hdu['Flip']
    offset_top = primary_hdu['Twice Top Offset'] / 2
    offset_flip = 90
    offset_ccd = -18.68		# For data captured after June 2014
#	offset_ccd = -18.63

    if ('Top Offset' in primary_hdu):
        offset_top = primary_hdu['Top Offset']
        print 'Top Offset        : ' + str(offset_top) + ' deg'
    if ('Flip Offset' in primary_hdu):
        offset_flip = primary_hdu['Flip Offset']
        print 'Flip Offset       : ' + str(offset_flip) + ' deg'
    if ('CCD Offset' in primary_hdu):
        offset_ccd = primary_hdu['CCD Offset']
        print 'CCD Offset        : ' + str(offset_ccd) + ' deg'

    wavelength = 1239.842 / energy
    twotheta = bottom - offset_ccd
    truetop = top - offset_top
    incidence = bottom - truetop
    chi = flip - offset_flip     # transverse
    phi = 0     # azimuth

    # Adjustments to alignment
    incidence += lattice.offsets.incidence
    chi += lattice.offsets.transverse
    phi += lattice.offsets.azimuth

    q_xray = 2 * pi * energy / 1239.842		# 2*pi / d   [1 / nm]

    incidence_rad = deg2rad(incidence)
    chi_rad = deg2rad(chi)
    phi_rad = deg2rad(phi)

    incidence_rotation = array([
        [ cos(incidence_rad),	0,	-sin(incidence_rad)	],
        [ 0,					1,	 0					],
        [ sin(incidence_rad),	0,	 cos(incidence_rad)				] ])

    chi_rotation = array([
        [ 1,	0,	 			 0				],
        [ 0,	cos(chi_rad),	-sin(chi_rad)	],
        [ 0,	sin(chi_rad),	 cos(chi_rad)	] ])

# need to verify sign of sin() components
# this version (mathematica, not IGOR) appears correct
    phi_rotation = array([
        [ cos(phi_rad),	 -sin(phi_rad),  0	],
        [ sin(phi_rad),	  cos(phi_rad),	0	],
        [ 0,			  0,				1	] ])

    qxyz_unit = array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1] ])

#	print dot(array([[1,2],[3,4]]), array([[1,3],[5,7]]))
#	print array([[1,2],[3,4]]).dot(array([[1,3],[5,7]]))
#	print array([[1,3],[5,7]]).dot(array([[1,2],[3,4]]))
#	a.dot(b) == dot(a, b) == a.b

#	print array([[1,2],[3,4]]).dot(array([[1,3],[5,7]])).dot(array([[10,20],[30,40]]))
#	print dot(array([[1,2],[3,4]]), dot(array([[1,3],[5,7]]), array([[10,20],[30,40]])))
#	a.dot(b).dot(c) == dot(a, dot(b, c)) == a.b.c

    lattice_a = lattice.a	# nm
    lattice_b = lattice.b	# nm
    lattice_spacing = array([lattice_a, lattice_b, 1])
    q_lattice_spacing = 2 * pi / lattice_spacing
    qxyz_rotated = incidence_rotation.dot(chi_rotation).dot(phi_rotation).dot(qxyz_unit)
    # Rotation leaves new unit vectors as columns
# 	qxyz_rotated = incidence_rotation.dot(qxyz_unit)
# 	print "qxyz_rotated (incid): ",
# 	print incidence,
# 	print qxyz_rotated.shape
# 	print qxyz_rotated
# 	qxyz_rotated = chi_rotation.dot(qxyz_unit)
# 	print "qxyz_rotated (chi): ",
# 	print chi,
# 	print qxyz_rotated.shape
# 	print qxyz_rotated
# 	qxyz_rotated = phi_rotation.dot(qxyz_unit)
# 	print "qxyz_rotated (phi): ",
# 	print phi,
# 	print qxyz_rotated.shape
# 	print qxyz_rotated
    # Divide 1st COLUMN by 2*pi/a
    # Divide 2nd COLUMN by 2*pi/b
    # Divide 3rd COLUMN by 2*pi/c
    hkl_rotated = qxyz_rotated / q_lattice_spacing[newaxis, :]
# 	print "qxyz_rotated: ",
# 	print qxyz_rotated.shape
# 	print qxyz_rotated
# 	print "q_lattice_spacing: ",
# 	print q_lattice_spacing
# 	print "hkl_rotated: ",
# 	print hkl_rotated.shape
# 	print hkl_rotated

    h_unit = hkl_rotated[:, 0]
    k_unit = hkl_rotated[:, 1]
    L_unit = hkl_rotated[:, 2]

    h_unit /= norm(h_unit)
    k_unit /= norm(k_unit)
    L_unit /= norm(L_unit)
# 	print "h_unit",
# 	print h_unit.shape,
# 	print h_unit
# 	print "k_unit",
# 	print k_unit.shape,
# 	print k_unit
# 	print "L_unit",
# 	print L_unit.shape,
# 	print L_unit

    sphere_center_q = array([-q_xray, 0, 0])
    sphere_center_q_proj_hk = array([
        sphere_center_q.dot(h_unit),
        sphere_center_q.dot(k_unit) ])
    # sphere_center_q_proj_h = sphere_center_q.dot(h_unit)
    # sphere_center_q_proj_k = sphere_center_q.dot(k_unit)
# 	print "hk_pairs",
# 	print hk_pairs.shape,
# 	print hk_pairs
# 	print "q_lattice_spacing[newaxis,:-1]",
# 	print q_lattice_spacing[newaxis,:-1].shape,
# 	print q_lattice_spacing[newaxis,:-1]
# 	print "hk_pairs * q_lattice_spacing[newaxis,:-1]",
# 	print (hk_pairs * q_lattice_spacing[newaxis,:-1]).shape,
# 	print hk_pairs * q_lattice_spacing[newaxis,:-1]
# 	exit()
    # Next command has same effect with(out) using 'newaxis'
    # hk_offset_from_sphere_center_q = hk_pairs * q_lattice_spacing[newaxis,:-1]
    hk_offset_from_sphere_center_q = hk_pairs * q_lattice_spacing[:-1]
#   	print "hk_offset_from_sphere_center_q (#1)",
#   	print hk_offset_from_sphere_center_q.shape,
#   	print hk_offset_from_sphere_center_q
    hk_offset_from_sphere_center_q -= sphere_center_q_proj_hk
    print "hk_offset_from_sphere_center_q (#2)",
    print hk_offset_from_sphere_center_q.shape,
    print hk_offset_from_sphere_center_q
    hk_circle_center_q =								\
        hk_offset_from_sphere_center_q[:, :, newaxis]	\
        * array([h_unit, k_unit])[newaxis, :, :]
#   	print "hk_circle_center_q (#1)",
#   	print hk_circle_center_q.shape,
#   	print hk_circle_center_q
    hk_circle_center_q += array([sphere_center_q, sphere_center_q])
    print "hk_circle_center_q (#2)",
    print hk_circle_center_q.shape,
    print hk_circle_center_q
#  	print "array([h_unit, k_unit]) * hk_circle_center_q",
#  	print (array([h_unit, k_unit]) * hk_circle_center_q).shape,
#  	print array([h_unit, k_unit]) * hk_circle_center_q
#  	print "array([h_unit, k_unit])[newaxis, :, :] * hk_circle_center_q",
#  	print (array([h_unit, k_unit])[newaxis, :, :] * hk_circle_center_q).shape,
#  	print array([h_unit, k_unit])[newaxis, :, :] * hk_circle_center_q
    # Next command has same effect with(out) using 'newaxis'
    # hk_linsolve_vector = array([h_unit, k_unit])[newaxis, :, :] * hk_circle_center_q
    hk_linsolve_vector = array([h_unit, k_unit]) * hk_circle_center_q
    hk_linsolve_vector = sum(hk_linsolve_vector, axis=-1)
#  	print "hk_linsolve_vector",
#  	print hk_linsolve_vector.shape,
#  	print hk_linsolve_vector
    linsolve_vector = 	\
        zeros( (hk_linsolve_vector.shape[0], hk_linsolve_vector.shape[1] + 1) )
    linsolve_vector[:, :-1] = hk_linsolve_vector
    print "linsolve_vector",
    print linsolve_vector.shape,
    print linsolve_vector
# 	exit()

    linsolve_matrix = hkl_rotated.transpose()
    hk_plane_intersection_vector = cross(h_unit, k_unit)
#  	print "hk_plane_intersection_vector",
#  	print hk_plane_intersection_vector.shape,
#  	print norm(hk_plane_intersection_vector),
#  	print hk_plane_intersection_vector
    hk_plane_intersection_vector /= norm(hk_plane_intersection_vector)
    print "hk_plane_intersection_vector",
    print hk_plane_intersection_vector.shape,
    print hk_plane_intersection_vector
#  	print "hk_plane_intersection_vector vs. L_unit",
#  	print (hk_plane_intersection_vector - L_unit).shape,
#  	print (hk_plane_intersection_vector - L_unit)
#  	print "hk_plane_intersection_vector vs. qxyz_rotated[:,2]",
#  	print (hk_plane_intersection_vector - qxyz_rotated[:,2]).shape,
#  	print (hk_plane_intersection_vector - qxyz_rotated[:,2])
#  	exit()

    # Only works if h, k, L are orthogonal
# 	if   L_unit[0] != 0 :		# L has component along room-X
# 		linsolve_matrix[-1] = array([1, 0, 0])
# 		solve(linsolve_matrix, linsolve_vector)
# 	elif L_unit[1] != 0 :		# L has component along room-Y
# 		Pass
# 	elif L_unit[2] != 0 :		# L has component along room-Z
# 		Pass
# 	else:
# 		return()	# Return array of complex-valued pairs [INVALID]

    if   hk_plane_intersection_vector[0] != 0 :		# vector has component along room-X
        linsolve_matrix[-1] = array([1, 0, 0])
        hk_plane_intersection_origin = solve(
            linsolve_matrix[newaxis, :, :], linsolve_vector)
        print "hk_plane_intersection_origin",
        print hk_plane_intersection_origin.shape,
        print hk_plane_intersection_origin
        # exit()
    elif hk_plane_intersection_vector[1] != 0 :		# vector has component along room-Y
        linsolve_matrix[-1] = array([0, 1, 0])
        hk_plane_intersection_origin = solve(
            linsolve_matrix[newaxis, :, :], linsolve_vector)
        print "hk_plane_intersection_origin",
        print hk_plane_intersection_origin.shape,
        print hk_plane_intersection_origin
        # exit()
    elif hk_plane_intersection_vector[2] != 0 :		# vector has component along room-Z
        linsolve_matrix[-1] = array([0, 0, 1])
        hk_plane_intersection_origin = solve(
            linsolve_matrix[newaxis, :, :], linsolve_vector)
        print "hk_plane_intersection_origin",
        print hk_plane_intersection_origin.shape,
        print hk_plane_intersection_origin
        # exit()
    else:
        # Return array of  INVALID pairs
        # ccd_hk_pairs_pixels = array([float('NaN'), float('NaN'), float('NaN')])
        ccd_coords_pairs_shape = empty(hk_pairs_shape.shape[0] + 1)
        ccd_coords_pairs_shape[:-2] = hk_pairs_shape[:-1]
        ccd_coords_pairs_shape[-2] = 2
        ccd_coords_pairs_shape[-1] = 2
        # ccd_hk_pairs_pixels = ccd_hk_pairs_pixels.reshape(*ccd_coords_pairs_shape)
        ccd_hk_pairs_pixels = empty( tuple(ccd_coords_pairs_shape) )
        ccd_hk_pairs_pixels.fill( float('NaN') )
        print "ccd_hk_pairs_pixels",
        print ccd_hk_pairs_pixels.shape,
        print ccd_hk_pairs_pixels
        return (ccd_hk_pairs_pixels)

    # a = hk_plane_intersection_vector[newaxis, :]
    a = hk_plane_intersection_vector
    b = hk_plane_intersection_origin - sphere_center_q
    print "a",
    print a.shape,
    print a
    print "b",
    print b.shape,
    print b
    print "a.dot(a)",
    print (a.dot(a)).shape,
    print a.dot(a)
    print "a.dot(b)",
    # print (a.dot(b)).shape,
    # print a.dot(b)
    print sum(a * b, axis=-1).shape,
    print sum(a * b, axis=-1)
    print "b.dot(b)",
    # print (b.dot(b)).shape,
    # print b.dot(b)
    print sum(b * b, axis=-1).shape,
    print sum(b * b, axis=-1)
    print "-B / 2A",
    print (-2*sum(a * b, axis=-1) / (2 * a.dot(a))).shape,
    print -2*sum(a * b, axis=-1) / (2 * a.dot(a))
    print "SQRT(B^2 - 4AC) / 2A",
    print (sqrt(4*square(sum(a * b, axis=-1)) 	\
        - 4 * a.dot(a) * (sum(b * b, axis=-1) - q_xray * q_xray)) 	\
        / (2 * a.dot(a))).shape,
    print sqrt(4*square(sum(a * b, axis=-1)) 	\
        - 4 * a.dot(a) * (sum(b * b, axis=-1) - q_xray * q_xray)) 	\
        / (2 * a.dot(a))
    t0 = -2*sum(a * b, axis=-1) / (2 * a.dot(a))
    t_delta = sqrt( 4*square(sum(a * b, axis=-1)) 	\
                  - 4 * a.dot(a) * (sum(b * b, axis=-1) - q_xray * q_xray) ) 	\
                  / (2 * a.dot(a))
    t_12 = empty((t0.shape[0], 2))
    t_12[:, 0] = t0 - t_delta
    t_12[:, 1] = t0 + t_delta
    print "t_12",
    print t_12.shape,
    print t_12
    # print hk_plane_intersection_vector[newaxis, :, newaxis] * t_12[:, newaxis, :]
    # intersections = hk_plane_intersection_origin[:, :, newaxis]		\
    # 	+ hk_plane_intersection_vector[newaxis, :, newaxis] * t_12[:, newaxis, :]
    intersections = hk_plane_intersection_origin[:, newaxis, :]		\
        + hk_plane_intersection_vector[newaxis, newaxis, :] * t_12[:, :, newaxis]
    print "intersections",
    print intersections.shape,
    print intersections
    exit_vectors = intersections - sphere_center_q[newaxis, newaxis, :]
    print "exit_vectors",
    print exit_vectors.shape,
    print exit_vectors
    # circle_intersections = roots([a.dot(a), 2*a.dot(b), b.dot(b) - q_xray*q_xray])
    # print "circle_intersections",
    # print circle_intersections.shape,
    # print circle_intersections
#	exit()

    distance_ccd = 1.120 * 142.265
    twotheta_rad = deg2rad(twotheta)
    ccd_center_room = [cos(twotheta_rad), 0 , sin(twotheta_rad)]
    ccd_center_room = array(ccd_center_room)
# 	print "Two-Theta: ",
# 	print twotheta,
# 	print " deg, ",
# 	print deg2rad(twotheta),
# 	print " rad"
# 	print "ccd_center_room unit: ",
# 	print ccd_center_room
# 	print "ccd_center_room length: ",
# 	print distance_ccd
    ccd_center_room *= distance_ccd

    ccd_tilt_axisY = 0
    ccd_unit_normal = array(
                        [cos(twotheta_rad) - ccd_tilt_axisY,
                        0 ,
                        sin(twotheta_rad) - ccd_tilt_axisY]	)
    ccd_unit_Y = array( [0, 1, 0] )
    ccd_unit_X = cross(ccd_unit_normal, ccd_unit_Y)

    raw_pixel_size = 0.0135		# size in mm
    raw_pixel_num  = 2048		# pixels / side
    num_cols, num_rows = image_array.shape
    ccd_pixel_size_X = raw_pixel_size * raw_pixel_num / num_cols
    ccd_pixel_size_Y = raw_pixel_size * raw_pixel_num / num_rows
    ccd_center_pixel_X = float(num_cols - 1) / 2					# Assumes 0...numCols-1
    ccd_center_pixel_Y = num_rows * (float(1024 - 460) / 1024) - 1;	# Assumes 0...numRows-1

# 	print "ccd_center_pixel: ",
# 	print ccd_center_pixel_X,
# 	print ", ",
# 	print ccd_center_pixel_Y
# 	print "ccd_pixel_size: ",
# 	print ccd_pixel_size_X,
# 	print ", ",
# 	print ccd_pixel_size_Y
# 	print "ccd_center_room: ",
# 	print ccd_center_room

    # Solve for intersections of exit_vectors (lines) and CCD (plane)
    # Build linear equations matrices, using permutation of exit vector components
    # Matrices intentionally over-determined
    linsolve_matrix_row1 = array([	[ 0,  0,  0],
                                    [ 0,  0,  1],
                                    [ 0, -1 , 0] ])
    linsolve_matrix_row2 = array([	[ 0,  0, -1],
                                    [ 0,  0,  0],
                                    [ 1,  0 , 0] ])
    linsolve_matrix_row3 = array([	[ 0,  1,  0],
                                    [-1,  0,  0],
                                    [ 0,  0 , 0] ])
    linsolve_matrix_rows = array([	linsolve_matrix_row1,
                                    linsolve_matrix_row2,
                                    linsolve_matrix_row3 ])
    print "linsolve_matrix_rows",
    print linsolve_matrix_rows.shape,
    print linsolve_matrix_rows
    linsolve_matrix_3x3 = linsolve_matrix_rows[newaxis, newaxis, :, :, :] 	\
        * exit_vectors[:, :, newaxis, newaxis, :]
    print "linsolve_matrix_3x3 (#1)",
    print linsolve_matrix_3x3.shape,
    print linsolve_matrix_3x3
    linsolve_matrix_3x3 = sum(linsolve_matrix_3x3, axis=-1)
    print "linsolve_matrix_3x3 (#2)",
    print linsolve_matrix_3x3.shape,
    print linsolve_matrix_3x3
    linsolve_matrix = empty((	linsolve_matrix_3x3.shape[0],
                                linsolve_matrix_3x3.shape[1],
                                linsolve_matrix_3x3.shape[2] + 1,
                                linsolve_matrix_3x3.shape[3]	))
    linsolve_matrix[:, :, 1:, :] = linsolve_matrix_3x3
    linsolve_matrix[:, :, 0, :] = ccd_unit_normal
    print "linsolve_matrix (#3)",
    print linsolve_matrix.shape,
    print linsolve_matrix
    # exit()

    linsolve_vector = zeros(4)
    linsolve_vector[0] = ccd_unit_normal.dot(ccd_center_room)
    print "linsolve_vector",
    print linsolve_vector.shape,
    print linsolve_vector

    # ccd_hk_pairs_room = tensorsolve(
    # 		linsolve_matrix, linsolve_vector[newaxis, newaxis, :])
    # Must use lstsq() for over-determined system
    # ...solution is contained in first index of returned array
    ccd_hk_pairs_room = array([
        [
            lstsq(exit_matrix, linsolve_vector)[0]
                if isfinite(exit_matrix).all() else
                # inaccessible (h,k) pair, return INVALID coordinate
                array([float('NaN'), float('NaN'), float('NaN')])
            for exit_matrix in hk_pair ]
        for hk_pair in linsolve_matrix
        ])
    print "ccd_hk_pairs_room",
    print ccd_hk_pairs_room.shape,
    print ccd_hk_pairs_room
    exit_vectors_proj_ccd = sum(ccd_hk_pairs_room * exit_vectors, axis=-1)
# 	ccd_hk_pairs_room = array([
# 		[
# 			if exit_proj < 0:
# 				array([1j, 1j])			# INVALID pair; projected AWAY from CCD
# 			else:
#
# 			for exit_proj in hk_pair ]
# 		for hk_pair in exit_vectors_proj_ccd
# 		])
# 	ccd_hk_pairs_room = array([
# 		[
# 			if exit_proj < 0:
# 				array([1j, 1j])			# INVALID pair; projected AWAY from CCD
# 			else:
# 				hk_proj_room
# 			for exit_proj, hk_proj_room in zip(exit_pair, hk_pair) ]
# 		for exit_pair, hk_pair in zip(exit_vectors_proj_ccd, ccd_hk_pairs_room)
# 		])
    ccd_hk_pairs_room = array([
        [
            # array([1j, 1j, 1j])			# INVALID pair; projected AWAY from CCD
            # INVALID pair; projected AWAY from CCD
            array([float('NaN'), float('NaN'), float('NaN')])
                if exit_proj < 0 else
                hk_proj_room
            for exit_proj, hk_proj_room in zip(exit_pair, hk_pair) ]
        for exit_pair, hk_pair in zip(exit_vectors_proj_ccd, ccd_hk_pairs_room)
        ])
    print "ccd_hk_pairs_room (#2)",
    print ccd_hk_pairs_room.shape,
    print ccd_hk_pairs_room
    # exit()
    ccd_hk_pairs_room -= ccd_center_room
    print "ccd_hk_pairs_room (#3)",
    print ccd_hk_pairs_room.shape,
    print ccd_hk_pairs_room
    ccd_hk_pairs_pixels = ccd_hk_pairs_room[:, :, :, newaxis] 	\
        * array([ccd_unit_X, ccd_unit_Y]).transpose()[newaxis, newaxis, :, :]
    ccd_hk_pairs_pixels = sum(ccd_hk_pairs_pixels, axis=-2)
    print "ccd_hk_pairs_pixels (#1)",
    print ccd_hk_pairs_pixels.shape,
    print ccd_hk_pairs_pixels
    ccd_hk_pairs_pixels /= 	\
        array([ccd_pixel_size_X, ccd_pixel_size_Y])[newaxis, newaxis, :]
    print "ccd_hk_pairs_pixels (#2)",
    print ccd_hk_pairs_pixels.shape,
    print ccd_hk_pairs_pixels
    ccd_hk_pairs_pixels += 	\
        array([ccd_center_pixel_X, ccd_center_pixel_Y])[newaxis, newaxis, :]
    print "ccd_hk_pairs_pixels (#3)",
    print ccd_hk_pairs_pixels.shape,
    print ccd_hk_pairs_pixels
    # exit()

    ccd_coords_pairs_shape = empty(hk_pairs_shape.shape[0] + 1)
    ccd_coords_pairs_shape[:-2] = hk_pairs_shape[:-1]
    ccd_coords_pairs_shape[-2] = 2
    ccd_coords_pairs_shape[-1] = 2
    ccd_hk_pairs_pixels = ccd_hk_pairs_pixels.reshape(*ccd_coords_pairs_shape)
    print "ccd_hk_pairs_pixels (#4)",
    print ccd_hk_pairs_pixels.shape,
    print ccd_hk_pairs_pixels

    return (ccd_hk_pairs_pixels)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main(args=None):
    """The main routine."""

    if args is None:
        args = sys.argv[1:]

    for arg in args:
        # if arg.lower() == "--version":
        #     print __version__
        pass

    print "Usage details"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    main()
