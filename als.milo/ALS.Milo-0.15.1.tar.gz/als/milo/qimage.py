#!/usr/bin/env python

"""qimage.py

   Reads CCD images from diffractometer, converts to Q-space data
"""

__author__ = "Padraic Shafer"
__copyright__ = "Copyright (c) 2014-2019, Padraic Shafer"
__credits__ = [__author__, ]
__license__ = ""
__maintainer__ = "Padraic Shafer"
__email__ = "PShafer@lbl.gov"
__status__ = "Development"

# Allow import of package siblings when module is run as script
import pkgscript
if (__name__ == "__main__") and (__package__ is None):
    pkgscript.import_parent_packages("als.milo", globals())

from als.milo import __version__, __date__

from numbers import Real
from datetime import datetime, date

from astropy.io import fits

from numpy import pi, cos, sin, deg2rad, rad2deg, arctan2, arcsin
from numpy import array, empty, full, newaxis
from numpy import linspace, arange, tile, hstack, vstack
from numpy import matrix, dot, cross, outer, sum, product, zeros, roots
from numpy import square, sqrt, around, isfinite, nan, isnan
from numpy.linalg import norm, solve, lstsq, tensorsolve
from scipy.optimize import brentq

import argparse
import pandas as pd


class Photon( object ):

    """Photon: set or access (energy / wavelength / q) of the photon

        energy (eV) / wavelength (nm) / q (1 / nm) are always synchronized
        according to relationship:
        q == 2*pi / wavelength;
        wavelength == 1239.842 eV*nm / energy
    """

    energy_at_1nm = 1239.842	# eV

    def __init__(self, *arguments, **keywords):
        """Initial value can be supplied in one of several formats
            Due to the multi-faceted nature of this class,
                keyword arguments are preferred

            ***Highest priority***
            energy = value, hv = value
            wavelength = value, wl = value, lambda_ = value
            q = value, momentum = value
            ***Lowest priority***

            If no keywords are given, then value of first arbitrary argument
                is used as the value for energy
                (as if input were energy = value)
        """
        if keywords:
            value = keywords.get('energy', None)
            if value is not None:
                self.energy = value
                return
            value = keywords.get('hv', None)
            if value is not None:
                self.energy = value
                return
            value = keywords.get('wavelength', None)
            if value is not None:
                self.wavelength = value
                return
            value = keywords.get('wl', None)
            if value is not None:
                self.wavelength = value
                return
            value = keywords.get('lambda_', None)
            if value is not None:
                self.wavelength = value
                return
            value = keywords.get('q', None)
            if value is not None:
                self.q = value
                return
            value = keywords.get('momentum', None)
            if value is not None:
                self.q = value
                return
        elif arguments:
            value = arguments[0]
            if isinstance(value, Real):
                self.energy = value
                return
        # handle undefined input
        pass

    @property
    def energy(self):
        """Access the energy (in eV) of the Photon"""
        return self._energy

    @energy.setter
    def energy(self, value):
        # Does not check for valid value
        self._energy = value
        return value

    @property
    def wavelength(self):
        """Access the wavelength (in nm) of the Photon"""
        return Photon.energy_at_1nm / self._energy

    @wavelength.setter
    def wavelength(self, value):
        # Does not check for valid value
        self._energy = Photon.energy_at_1nm / value
        return value

    @property
    def q(self):
        """Access the momentum (in 1/nm) of the Photon"""
        return 2*pi * self._energy / Photon.energy_at_1nm

    @q.setter
    def q(self, value):
        # Does not check for valid value
        self._energy = value * Photon.energy_at_1nm / (2*pi)
        return value


class Polarization( object ):

    """Polarization: set or access polarization of the x-ray beamline

        State can be circular, linear, or undefined
        Degree of circular polarization is given as ratio, -1 <= ratio <= 1
        Angle of linear polarization axis is given in degrees from horizontal
    """

    # Allowed polarization states
    UNDEFINED = -1
    CIRCULAR = 0
    LINEAR = 1

    # Offsets for internal calculations of state / value
    _OFFSET_CIRCULAR = 0
    _OFFSET_LINEAR = 100

    def __init__(self, init_value=0., *arguments, **keywords):
        """init_value should be supplied in the following range(s):
            0   --  Horizontal linear polarization
            -1 <= init_value <= 1   --  Degree of circular polarization
            2   --  Vertical linear polarization
            100 <= init_value <= 190   --  100 + angle of linear polarization

            State is set to circular, linear, or undefined based on init_value
        """
        self.value = float(init_value)

    @property
    def value(self):
        """Access the raw value of the x-ray polarization"""
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        # might need to adjust comparisons for floating point rounding
        if (0 < abs(new_value) <= 1):
            self._state = Polarization.CIRCULAR
            self._offset_circular = Polarization._OFFSET_CIRCULAR
            self._offset_linear = float('NaN')
        elif (100 <= new_value <= 190):
            self._state = Polarization.LINEAR
            self._offset_circular = float('NaN')
            self._offset_linear = Polarization._OFFSET_LINEAR
        elif (0 <= new_value <= 0):
            self._value = 100
            self._state = Polarization.LINEAR
            self._offset_circular = float('NaN')
            self._offset_linear = Polarization._OFFSET_LINEAR
        elif (2 <= new_value <= 2):
            self._value = 190
            self._state = Polarization.LINEAR
            self._offset_circular = float('NaN')
            self._offset_linear = Polarization._OFFSET_LINEAR
        else:
            self._state = Polarization.UNDEFINED
            self._offset_circular = float('NaN')
            self._offset_linear = float('NaN')
        return new_value

    @property
    def circular_degree(self):
        """Access the degree of circular polarization for the x-ray
            Given as ratio, -1 <= degree_of_polarization <= 1
        """
        return (self._value - self._offset_circular)

    @circular_degree.setter
    def circular_degree(self, degree_of_polarization):
        # Error checking performed by @value.setter
        self.value = degree_of_polarization
        return self.value

    @property
    def linear_angle(self):
        """Access the angle of linear polarization for the x-ray
            Angle is in degrees from horizontal
        """
        return (self._value - self._offset_linear)

    @linear_angle.setter
    def linear_angle(self, angle):
        # Error checking performed by @value.setter
        self.value = angle + Polarization._OFFSET_LINEAR
        return self.value

    @property
    def state(self):
        """Access the polarization state of the x-ray"""
        return self._state


class SampleLattice( object ):

    """SampleLattice: set or access lattice parameters of sample

        x_unit (x = a,b,c) = unit vector of fundamental lattice translation
        x (x = a,b,c) = distance of fundamental lattice translation
        x_vect (x = a,b,c) = x * x_unit

        reset_axes: Sets a_unit // x, b_unit // y, c_unit // z
        permute_axes: Cycles lattice fundamental directions so that (x,y,z) //
            (a,b,c)_unit -> (a,b,c)_unit -> (a,b,c)_unit // (x,y,z)
        rotate_by: Rotate sample by XX degrees about given axis
        normal: lattice vector normal to sample stage (z)
        longitudinal: lattice vector longitudinal to sample stage (y)
        transverse: lattice vector transverse to sample stage (x)
    """

    # set parameter modes
    CCD, DIODE_WIDE, DIODE_HIRES = range(3)
    energy_at_1nm = 1239.842	# eV


    def __init__(self, *arguments, **keywords):
        """Initial value can be supplied in one of several formats
            Due to the multi-faceted nature of this class,
                keyword arguments are preferred

            ***Highest priority***
            energy = value, hv = value
            wavelength = value, wl = value, lambda_ = value
            q = value, momentum = value
            ***Lowest priority***

            If no keywords are given, then value of first arbitrary argument
                is used as the value for energy
                (as if input were energy = value)
        """
        if keywords:
            value = keywords.get('energy', None)
            if value is not None:
                self.energy = value
                return
            value = keywords.get('hv', None)
            if value is not None:
                self.energy = value
                return
            value = keywords.get('wavelength', None)
            if value is not None:
                self.wavelength = value
                return
            value = keywords.get('wl', None)
            if value is not None:
                self.wavelength = value
                return
            value = keywords.get('lambda_', None)
            if value is not None:
                self.wavelength = value
                return
            value = keywords.get('q', None)
            if value is not None:
                self.q = value
                return
            value = keywords.get('momentum', None)
            if value is not None:
                self.q = value
                return
        elif arguments:
            value = arguments[0]
            if isinstance(value, Real):
                self.energy = value
                return
        # handle undefined input
        pass

    @property
    def energy(self):
        """Access the energy (in eV) of the Photon"""
        return self._energy

    @energy.setter
    def energy(self, value):
        # Does not check for valid value
        self._energy = value
        return value

    @property
    def wavelength(self):
        """Access the wavelength (in nm) of the Photon"""
        return Photon.energy_at_1nm / self._energy

    @wavelength.setter
    def wavelength(self, value):
        # Does not check for valid value
        self._energy = Photon.energy_at_1nm / value
        return value

    @property
    def q(self):
        """Access the momentum (in 1/nm) of the Photon"""
        return 2*pi * self._energy / Photon.energy_at_1nm

    @q.setter
    def q(self, value):
        # Does not check for valid value
        self._energy = value * Photon.energy_at_1nm / (2*pi)
        return value


class Diffractometer( object ):

    """Diffractometer: diffractometer settings and readings"""

    def __init__(self, twotheta=0., incidence=0., transverse=0., azimuth=0.,
                 energy=700., polarization=0., intensity0=1.,
                 temperature=298, distance=1.,
                 *arguments, **keywords):
        self.twotheta = twotheta
        self.incidence = incidence
        self.transverse = transverse
        self.azimuth = azimuth
        self.photon = Photon(energy)
        self.polarization = polarization
        self.intensity0 = intensity0
        self.temperature = temperature

    @property
    def twotheta(self):
        """Access the detector position, 2-Theta (in degrees)"""
        return self._twotheta

    @twotheta.setter
    def twotheta(self, value):
        # Does not check for valid value
        self._twotheta = value
        return value

    @property
    def incidence(self):
        """Access the 2D incidence angle (in degrees) within Th-2Th plane"""
        return self._incidence

    @incidence.setter
    def incidence(self, value):
        # Does not check for valid value
        self._incidence = value
        return value

    @property
    def exit_angle(self):
        """Access the 2D exit angle (in degrees) within Th-2Th plane"""
        return (self._twotheta - self._incidence)

    @exit_angle.setter
    def exit_angle(self, value):
        # Does not check for valid value
        # self._twotheta = self._incidence + value
        self._incidence = self._twotheta - value
        return value

    @property
    def transverse(self):
        """Access the chi angle (in degrees), transverse to Th-2Th plane"""
        return self._transverse

    @transverse.setter
    def transverse(self, value):
        # Does not check for valid value
        self._transverse = value
        return value

    @property
    def azimuth(self):
        """Access the sample stage's azimuth angle (in degrees), phi"""
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        # Does not check for valid value
        self._azimuth = value
        return value

    @property
    def energy(self):
        """Access the energy (in eV) of the Photon"""
        return self.photon.energy

    @energy.setter
    def energy(self, value):
        # Does not check for valid value
        self.photon.energy = value
        return value

    @property
    def wavelength(self):
        """Access the wavelength (in nm) of the Photon"""
        return self.photon.wavelength

    @wavelength.setter
    def wavelength(self, value):
        # Does not check for valid value
        self.photon.wavelength = value
        return value

    @property
    def q_xray(self):
        """Access the momentum (in 1/nm) of the Photon"""
        return self.photon.q

    @q_xray.setter
    def q_xray(self, value):
        # Does not check for valid value
        self.photon.q = value
        return value

    @property
    def polarization(self):
        """Access the Polarization object for the x-ray polarization"""
        return self._polarization

    @polarization.setter
    def polarization(self, new_polarization):
        # Does not check for valid value
        if not isinstance(new_polarization, Polarization):
            new_polarization = Polarization(new_polarization)
        self._polarization = new_polarization
        return new_polarization

    @property
    def intensity0(self):
        """Access the incoming flux, I0, (in arb. units)"""
        return self._intensity0

    @intensity0.setter
    def intensity0(self, value):
        # Does not check for valid value
        self._intensity0 = value
        return value

    @property
    def temperature(self):
        """Access the temperature of the sample stage (in Kelvin)"""
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        # Does not check for valid value
        self._temperature = value
        return value

    @property
    def exposure_time(self):
        """Access the exposure (acquisition) time (in seconds)"""
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, value):
        # Does not check for valid value
        self._exposure_time = value
        return value

    @property
    def distance(self):
        """Access the distance between sample and detector (in mm)"""
        return self._distance

    @distance.setter
    def distance(self, value):
        # Does not check for valid value
        self._distance = value
        return value


class Diffractometer402( Diffractometer ):

    """Diffractometer402:
        Settings and readings and scattering chamber at ALS beamline 4.0.2
    """

    # Detector modes
    CCD, DIODE_WIDE, DIODE_HIRES = range(3)
    DIODE = DIODE_WIDE

    # Defaults
    _DISTANCE_SAMPLE_TO_CCD = 1.125 * 142.265		# mm
    _DISTANCE_SAMPLE_TO_DIODE = 7.75 * 25.4			# mm
    default_chamber_params = dict({
        'Beamline Energy': 700.,
        'EPU Polarization': 0.,
        'Bottom Rotary Seal': 15.,
        'Top Rotary Seal': 137.5,
        'Flip': -2.,
        'Flip Offset': -1.,
        'Top Offset': 2.,
        # 'Twice Top Offset': 4.,
        # 'CCD Offset': -18.68,
        # 'DATE': "2015-02-12",
        'DATE': date.today().strftime("%Y-%m-%d"),
        # 'Counter 2': 340*1000.,
        'I0 BL': 340*1000.,
        'TempCtrlrA': 296.,
        'TempCtrlrB': 295.,
         })

    def __init__(self, param_dict=None, *arguments, **keywords):
        """Initialize the Diffractometer using dictionary value pairs,
            or provide default values as needed
        """

        # Do NOT call __init__() for base class
        # Diffractometer.__init__(self, **keywords)
        if param_dict is None:
            # Need to provide some default values
            param_dict = self.default_chamber_params
            # return
        value = param_dict.get('DATE', None)
        if value is not None:
            if 'T' in value:
                image_date = datetime.strptime(value,
                    "%Y-%m-%dT%H:%M:%S").date()
            else:
                image_date = datetime.strptime(value, "%Y-%m-%d").date()
        else:
            value = param_dict.get('DATETIME', None)
            if value is not None:
                image_date = datetime.strptime(value,
                    "%Y/%m/%d %H:%M:%S").date()
            else:
                image_date = datetime.strptime("1970-01-01", "%Y-%m-%d").date()
        # print image_date
        value = param_dict.get('EXPOSURE', None)
        if value is not None:
            self.exposure_time = value
        value = param_dict.get('Detector Mode', None)
        if value is not None:
            self.detector = value
        else:
            value = keywords.get('detector', None)
            if value is not None:
                self.detector = value
            else:
                self.detector = Diffractometer402.CCD
        value = param_dict.get('Beamline Energy', None)
        if value is not None:
            energy = value
        value = param_dict.get('EPU Polarization', None)
        if value is not None:
            polarization = value
        value = param_dict.get('Bottom Rotary Seal', None)
        if value is not None:
            # self.bottom_angle = value
            bottom_angle = value
        value = param_dict.get('Top Rotary Seal', None)
        if value is not None:
            # self.top_angle = value
            top_angle = value
        value = param_dict.get('Flip', None)
        if value is not None:
            # self.flip_angle = value
            flip_angle = value
        else:
            value = param_dict.get('Flip Position', None)
            if value is not None:
                # self.flip_angle = value
                flip_angle = value
        value = param_dict.get('Flip Offset', None)
# 		if value is not None:
# 			self.offset_flip = value
# 		else:
# 			self.offset_flip = 0.0
# 			# Potentially a useful default value
# 			# self.offset_flip = -2.0
        if value is not None:
            self._offset_flip = value
        else:
            self._offset_flip = 0.0
            # Potentially a useful default value
            # self._offset_flip = -2.0
        value = param_dict.get('Top Offset', None)
# 		if value is not None:
# 			self.offset_top = value
# 		else:
# 			value = keywords.get('Twice Top Offset', None)
# 			if value is not None:
# 				self.offset_top = (value / 2)
# 			else:
# 				self.offset_top = 0.0
# 				# Potentially a useful default value
# 				# self.offset_top = 2.0
        if value is not None:
            self._offset_top = value
        else:
            value = keywords.get('Twice Top Offset', None)
            if value is not None:
                self._offset_top = (value / 2.0)
            else:
                self._offset_top = 0.0
                # Potentially a useful default value
                # self._offset_top = 2.0
        value = param_dict.get('CCD Offset', None)
        if value is not None:
            self.offset_CCD = value
        else:
            # # value = keywords.get('DATE', None)
            # value = param_dict.get('DATE', None)
            # image_date = datetime.strptime(value, "%Y-%m-%d").date()
            if image_date > date(2014, 06, 01):
                self.offset_CCD = -18.68	# degrees
            else:
                self.offset_CCD = -18.63	# degrees
        value = param_dict.get('Hi-Res Offset', None)
        if value is not None:
            self.offset_diode_hires = value
        else:
            # # value = keywords.get('DATE', None)
            # value = param_dict.get('DATE', None)
            # image_date = datetime.strptime(value, "%Y-%m-%d").date()
            if image_date > date(2014, 06, 01):
                self.offset_diode_hires = 5.976		# degrees
            else:
                self.offset_diode_hires = 0.00		# degrees
        value = param_dict.get('Azimuth', None)
        if value is not None:
            self.azimuth = value
        else:
            value = keywords.get('azimuth', None)
            if value is not None:
                self.azimuth = value
            else:
                self.azimuth = 0.0
        value = param_dict.get('I0 BL', None)
        # print "CCD I0 BL:", value
        if value is not None:
            self.intensity0 = value
        else:
            value = param_dict.get('Counter 2', None)
            # print "CCD Counter 2:", value
            if value is not None:
                self.intensity0 = value
        # print "self.intensity0:", self.intensity0
        for key_entry in ('TempCtrlrA', 'Temperature A',
                          'Lakeshore Temp Controller A',
                          'TempCtrlrB', 'Temperature B',
                          'Lakeshore Temp Controller B', ):
            value = param_dict.get(key_entry, None)
            if value is not None:
                self.temperature = value
                break
        else:
            self.temperature = 298		# Kelvin

        # TO DO: Gracefully handle inconsistent derived motor values
        # value = param_dict.get('CCD 2-Theta (Th-2Th)', None)
        # if value is not None:
        # 	self.twotheta = value

        self.offset_diode_wide = 0.00		# degrees
        self._distance_CCD = Diffractometer402._DISTANCE_SAMPLE_TO_CCD
        self._distance_diode = Diffractometer402._DISTANCE_SAMPLE_TO_DIODE
        # Allow for keyword to change the distance

        if (self.detector == self.CCD):
            self.offset_detector = self.offset_CCD
            distance = self._distance_CCD
        elif (self.detector == self.DIODE_WIDE):
            self.offset_detector = self.offset_diode_wide
            distance = self._distance_diode
        elif (self.detector == self.DIODE_HIRES):
            self.offset_detector = self.offset_diode_hires
            distance = self._distance_diode

# 		twotheta = self.bottom_angle - self.offset_detector
# 		top_true = self.top_angle - self.offset_top
# 		incidence = self.bottom_angle - top_true
# 		transverse = self.flip_angle - self.offset_flip

        twotheta = bottom_angle - self.offset_detector
        top_true = top_angle - self.offset_top
        incidence = bottom_angle - top_true
        transverse = flip_angle - self.offset_flip

        self.twotheta = twotheta
        self.incidence = incidence
        self.transverse = transverse
        # self.azimuth = azimuth
        self.photon = Photon(energy)
        self.polarization = polarization
        # self.intensity0 = intensity0
        # self.temperature = temperature
        self.distance = distance


        # This appears to be resolved as of 2015-02-12 edit
        # -------------------------------------------------
        # NOTE:  default values will always override param_dict values
        #	Need to either provide defaults or overrides
        # NOTE: Base class initialization duplicated with overrides
        #	and also with param_dict values
        # REQUIRES SIMPLIFICATION

    @property
    def twotheta(self):
        """Access the detector position, 2-Theta (in degrees)"""
        return self._twotheta

    @twotheta.setter
    def twotheta(self, value):
        # Does not check for valid value
        self._twotheta = value
        return value

    @property
    def incidence(self):
        """Access the 2D incidence angle (in degrees) within Th-2Th plane"""
        return self._incidence

    @incidence.setter
    def incidence(self, value):
        # Does not check for valid value
        self._incidence = value
        return value

    @property
    def exit_angle(self):
        """Access the 2D exit angle (in degrees) within Th-2Th plane"""
        return (self._twotheta - self._incidence)

    @exit_angle.setter
    def exit_angle(self, value):
        # Does not check for valid value
        # self._twotheta = self._incidence + value
        self._incidence = self._twotheta - value
        return value

    @property
    def transverse(self):
        """Access the chi angle (in degrees), transverse to Th-2Th plane"""
        return self._transverse

    @transverse.setter
    def transverse(self, value):
        # Does not check for valid value
        self._transverse = value
        return value

    @property
    def azimuth(self):
        """Access the sample stage's azimuth angle (in degrees), phi"""
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        # Does not check for valid value
        self._azimuth = value
        return value

    @property
    def bottom_angle(self):
        """Access the stored value of the Bottom Rotary Seal MOTOR"""
        return (self.twotheta + self.offset_detector)

    @property
    def top_angle(self):
        """Access the stored value of the Top Rotary Seal MOTOR"""
        return ( (self.bottom_angle - self.incidence) + self.offset_top)

    @property
    def flip_angle(self):
        """Access the stored value of the Flip MOTOR"""
        return (self.transverse + self.offset_flip)

    @property
    def offset_top(self):
        """Access the stored offset of the Top Rotary Seal MOTOR"""
        return self._offset_top

    @property
    def offset_flip(self):
        """Access the stored offset of the Flip MOTOR"""
        return self._offset_flip

    def offset(self, motor, value = 0, motor_unchanged = True):
        """Update the stored offset of a MOTOR

            motor: name (or short name) of motor to which offset is applied
            value: new value of the motor's offset
            motor_unchanged: True = motor value unchanged, update ideal angle
                             False = ideal angle unchanged, update motor value
        """
        twotheta = self.twotheta
        incidence = self.incidence
        transverse = self.transverse

        bottom_angle = self.bottom_angle
        top_angle = self.top_angle
        flip_angle = self.flip_angle

        motor = motor.lower()
        if (
                (motor == "top") or
                (motor == "top motor") or
                (motor == "top seal") or
                (motor == "top rotary seal")
                ):
            self._offset_top = value
            if (motor_unchanged == False):
                # top_true = self._bottom_angle - self.incidence
                # self._top_angle = top_true + self.offset_top
                pass
            else:
                # top_true = self._top_angle - self.offset_top
                # self.incidence = self._bottom_angle - top_true
                top_true = top_angle - self.offset_top
                self.incidence = bottom_angle - top_true
        elif (
                (motor == "flip") or
                (motor == "flip motor")
                ):
            self._offset_flip = value
            if (motor_unchanged == False):
                # self._flip_angle = self.transverse + self.offset_flip
                pass
            else:
                # self.transverse = self._flip_angle - self.offset_flip
                self.transverse = flip_angle - self.offset_flip
        else:
            # print "Bad motor name supplied to offset() method"
            pass

    def offset_step(self, motor, value_step = 0, motor_unchanged = True):
        """Update the stored offset of a MOTOR, relative to existing offset

            motor: name (or short name) of motor to which offset is applied
            value_step: add to existing value of the motor's offset
            motor_unchanged: True = motor value unchanged, update ideal angle
                             False = ideal angle unchanged, update motor value
        """
        twotheta = self.twotheta
        incidence = self.incidence
        transverse = self.transverse

        bottom_angle = self.bottom_angle
        top_angle = self.top_angle
        flip_angle = self.flip_angle

        offset_top = self.offset_top
        offset_flip = self.offset_flip

        motor = motor.lower()
        if (
                (motor == "top") or
                (motor == "top motor") or
                (motor == "top seal") or
                (motor == "top rotary seal")
                ):
            self._offset_top += value_step
            if (motor_unchanged == False):
                # top_true = self._bottom_angle - self.incidence
                # self._top_angle = top_true + self.offset_top
                pass
            else:
                # top_true = self._top_angle - self.offset_top
                # self.incidence = self._bottom_angle - top_true
                top_true = top_angle - self.offset_top
                self.incidence = bottom_angle - top_true
        elif (
                (motor == "flip") or
                (motor == "flip motor")
                ):
            self._offset_flip += value_step
            if (motor_unchanged == False):
                # self._flip_angle = self.transverse + self.offset_flip
                pass
            else:
                # self.transverse = self._flip_angle - self.offset_flip
                self.transverse = flip_angle - self.offset_flip

        # Hack for allowing ideal angles (not just MOTORs)
        elif (
                (motor == "incidence") 	# Ideal angle, not MOTOR
                ):
            self._offset_top -= value_step	# opposite rotation sense
            if (motor_unchanged == False):
                # top_true = self._bottom_angle - self.incidence
                # self._top_angle = top_true + self.offset_top
                pass
            else:
                # top_true = self._top_angle - self.offset_top
                # self.incidence = self._bottom_angle - top_true
                top_true = top_angle - self.offset_top
                self.incidence = bottom_angle - top_true
        elif (
                (motor == "transverse") 	# Ideal angle, not MOTOR
                ):
            self._offset_flip += value_step	# same rotation sense
            if (motor_unchanged == False):
                # self._flip_angle = self.transverse + self.offset_flip
                pass
            else:
                # self.transverse = self._flip_angle - self.offset_flip
                self.transverse = flip_angle - self.offset_flip
        else:
            # print "Bad motor name supplied to offset() method"
            pass

    def valid_motors(self):
        """Checks whether motor values are valid

            returns: True if motor values are valid; False otherwise
        """
        if ( (self.detector == self.CCD) and (self.bottom_angle < 6.0) ):
            return False

        if (self.bottom_angle > 140.0):
            return False

        if (self.flip_angle < -5.0) or (self.flip_angle > 95.0):
            return False

        return True


class CcdImage:

    """CcdImage: wrapper for 2D data + header info from diffractometer image"""

    def __init__(self):
        pass


class CcdImageFromFITS( CcdImage ):

    """CCDImageFromFITS: CCDImage created from FITS file"""

    def __init__(self, filename_or_hdulist, offset_diffractometer=None):
        """Extract relevant data from FITS file"""
        if isinstance(filename_or_hdulist, fits.HDUList):
            self.hdulist = filename_or_hdulist
        else:
            # check for errors during load
            self.hdulist = fits.open(filename_or_hdulist)
        self._build_diffractometer(offset_diffractometer)

    def _build_diffractometer(self, offset_diffractometer=None):
        """Extract relevant diffractometer data"""
        self._repair_fits_header()
        self._diffractometer = Diffractometer402(
            param_dict = self.hdulist[0].header)
        if offset_diffractometer:
            self._diffractometer.azimuth += offset_diffractometer.azimuth
            self._diffractometer.transverse += offset_diffractometer.transverse
            self._diffractometer.incidence += offset_diffractometer.incidence
        # Assumes last image has intensity map
        self.data = self.hdulist[-1].data

    def _repair_fits_header(self):
        """Repair AI channels in diffractometer data"""
        primary_hdu = self.hdulist[0].header
        # z_motor = primary_hdu['Z']
        z_ai = primary_hdu['Z Position']
        z_motor = primary_hdu.get('Z', z_ai)
        ai_ratio = int(z_ai / z_motor)

        for key in primary_hdu.keys():
            if primary_hdu.comments[key] == "Analog Input":
                # print key, ":", primary_hdu[key]
                primary_hdu[key] /= ai_ratio
                # print key, ":", primary_hdu[key]

    @property
    def intensity0(self):
        """Access the incoming flux, I0, (in arb. units)"""
        return self._diffractometer.intensity0

    @property
    def exposure_time(self):
        """Access the exposure (acquisition) time (in seconds)"""
        return self._diffractometer.exposure_time

    def qimage(self, output_filename=None):
        """Convert pixel map of intensities into reciprocal space map"""

        diffr = self._diffractometer
        image_array = self.data

        # wavelength = diffr.photon.wavelength
        twotheta = diffr.twotheta
        incidence = diffr.incidence
        chi = diffr.transverse
        phi = diffr.azimuth

        distance_ccd = diffr.distance
        ccd_center_room = [cos(deg2rad(twotheta)), 0 , sin(deg2rad(twotheta))]
        ccd_center_room = array(ccd_center_room)
        ccd_center_room *= distance_ccd

        ccd_tilt_axisY = 0
        ccd_unit_normal = [cos(deg2rad(twotheta)) - ccd_tilt_axisY,
                            0 ,
                            sin(deg2rad(twotheta)) - ccd_tilt_axisY]
        ccd_unit_Y = [0, 1, 0]
        ccd_unit_X = cross(ccd_unit_normal, ccd_unit_Y)

        raw_pixel_size = 0.0135		# size in mm
        raw_pixel_num  = 2048		# pixels / side
        num_cols, num_rows = image_array.shape
        ccd_pixel_size_X = raw_pixel_size * raw_pixel_num / num_cols
        ccd_pixel_size_Y = raw_pixel_size * raw_pixel_num / num_rows
        ccd_center_pixel_X = float(num_cols - 1) / 2					# Assumes 0...numCols-1
        ccd_center_pixel_Y = num_rows * (float(1024 - 460) / 1024) - 1;	# Assumes 0...numRows-1

        ccd_pixel_Y = linspace(
            (0        - ccd_center_pixel_Y) * ccd_pixel_size_Y,
            (num_rows - ccd_center_pixel_Y) * ccd_pixel_size_Y,
            num=num_rows,
            endpoint=False
            )
        ccd_pixel_X = linspace(
            (0        - ccd_center_pixel_X) * ccd_pixel_size_X,
            (num_cols - ccd_center_pixel_X) * ccd_pixel_size_X,
            num=num_cols,
            endpoint=False
            )
        # print ccd_pixel_Y, ccd_pixel_X
        ccd_pixel_room_rows = outer(ccd_pixel_Y, ccd_unit_Y)
        ccd_pixel_room_cols = outer(ccd_pixel_X, ccd_unit_X)
        ccd_pixel_room = (ccd_pixel_room_rows[:, None] + ccd_pixel_room_cols +
            ccd_center_room)
        # print "ccd_pixel_room.shape", ccd_pixel_room.shape
        ccd_pixel_room = ccd_pixel_room.reshape(num_rows * num_cols, 3)
        # print "ccd_pixel_room.shape (flattened)", ccd_pixel_room.shape

        ccd_pixel_intensities = array(image_array)
        ccd_pixel_intensities = ccd_pixel_intensities.reshape(
            num_rows * num_cols)

        ccd_pixel_room_norms = norm(ccd_pixel_room, axis=-1)
        ccd_pixel_room_norm = ccd_pixel_room / ccd_pixel_room_norms[:, newaxis]
        # print "ccd_pixel_room_norm.shape", ccd_pixel_room_norm.shape

        q_xray = diffr.photon.q		# 2*pi / d   [1 / nm]
        qxyz_sphere = ccd_pixel_room_norm * q_xray + array([-q_xray, 0, 0])

        incidence_rad = deg2rad(incidence)
        chi_rad = deg2rad(chi)
        phi_rad = deg2rad(phi)

        incidence_rotation = array([
            [ cos(incidence_rad),	0,	-sin(incidence_rad)	],
            [ 0,					1,	 0					],
            [ sin(incidence_rad),	0,	 cos(incidence_rad)	] ])

        chi_rotation = array([
            [ 1,	0,	 			 0				],
            [ 0,	cos(chi_rad),	-sin(chi_rad)	],
            [ 0,	sin(chi_rad),	 cos(chi_rad)	] ])

        # need to verify sign of sin() components
        # this version (mathematica, not IGOR) appears correct
        phi_rotation = array([
            [ cos(phi_rad),	 -sin(phi_rad),  	0	],
            [ sin(phi_rad),	  cos(phi_rad),		0	],
            [ 0,			  0,				1	] ])

        qxyz_normal = array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1] ])

        # lattice_a = 42	#nm
        # lattice_spacing = array([lattice_a, lattice_a, 1])
        # q_lattice_spacing = 2 * pi / lattice_spacing
        q_lattice_spacing = array([1, 1, 1])
        qxyz_rotated = incidence_rotation.dot(
            chi_rotation).dot(phi_rotation).dot(qxyz_normal)
        # print "qxyz_rotated.shape", qxyz_rotated.shape
        # Rotation leaves new unit vectors as columns
        # Divide 1st COLUMN by 2*pi/a
        # Divide 2nd COLUMN by 2*pi/b
        # Divide 3rd COLUMN by 2*pi/c
        hkl_rotated = qxyz_rotated / q_lattice_spacing[newaxis, :]
        # print "hkl_rotated.shape", hkl_rotated.shape
        hkl_map = qxyz_sphere.dot(hkl_rotated)
        # print "hkl_map.shape", hkl_map.shape
        ccd_int_qxqy = array([
            hkl_map[:, 0],
            hkl_map[:,1],
            ccd_pixel_intensities])
        # print "ccd_int_qxqy.shape", ccd_int_qxqy.shape
        ccd_int_qxqy = ccd_int_qxqy.transpose()
        # print "ccd_int_qxqy.shape (transposed)", ccd_int_qxqy.shape

        return( ccd_int_qxqy )

    def qvalues_df(self, output_filename=None):
        """Convert pixel map of intensities into reciprocal space map

            *) output_filename: optional storage location of calculated data
            *) Returns PANDAS dataframe containing:
                row, col, Qx, Qy, Qz, intensity (in "Counts")
        """

        diffr = self._diffractometer
        image_array = self.data

        # wavelength = diffr.photon.wavelength
        twotheta = diffr.twotheta
        incidence = diffr.incidence
        chi = diffr.transverse
        phi = diffr.azimuth

        distance_ccd = diffr.distance
        ccd_center_room = [cos(deg2rad(twotheta)), 0 , sin(deg2rad(twotheta))]
        ccd_center_room = array(ccd_center_room)
        ccd_center_room *= distance_ccd

        ccd_tilt_axisY = 0
        ccd_unit_normal = [cos(deg2rad(twotheta)) - ccd_tilt_axisY,
                            0 ,
                            sin(deg2rad(twotheta)) - ccd_tilt_axisY]
        ccd_unit_Y = [0, 1, 0]
        ccd_unit_X = cross(ccd_unit_normal, ccd_unit_Y)

        raw_pixel_size = 0.0135		# size in mm
        raw_pixel_num  = 2048		# pixels / side
        num_cols, num_rows = image_array.shape
        ccd_pixel_size_X = raw_pixel_size * raw_pixel_num / num_cols
        ccd_pixel_size_Y = raw_pixel_size * raw_pixel_num / num_rows
        ccd_center_pixel_X = float(num_cols - 1) / 2					# Assumes 0...numCols-1
        ccd_center_pixel_Y = num_rows * (float(1024 - 460) / 1024) - 1;	# Assumes 0...numRows-1

        ccd_pixel_Y = linspace(
            (0        - ccd_center_pixel_Y) * ccd_pixel_size_Y,
            (num_rows - ccd_center_pixel_Y) * ccd_pixel_size_Y,
            num=num_rows,
            endpoint=False
            )
        ccd_pixel_X = linspace(
            (0        - ccd_center_pixel_X) * ccd_pixel_size_X,
            (num_cols - ccd_center_pixel_X) * ccd_pixel_size_X,
            num=num_cols,
            endpoint=False
            )
        # print ccd_pixel_Y, ccd_pixel_X
        ccd_pixel_room_rows = outer(ccd_pixel_Y, ccd_unit_Y)
        ccd_pixel_room_cols = outer(ccd_pixel_X, ccd_unit_X)
        ccd_pixel_room = (ccd_pixel_room_rows[:, None] + ccd_pixel_room_cols +
            ccd_center_room)
        # print "ccd_pixel_room.shape", ccd_pixel_room.shape
        ccd_pixel_room = ccd_pixel_room.reshape(num_rows * num_cols, 3)
        # print "ccd_pixel_room.shape (flattened)", ccd_pixel_room.shape

        ccd_pixel_intensities = array(image_array)
        ccd_pixel_intensities = ccd_pixel_intensities.reshape(
            num_rows * num_cols)

        ccd_pixel_room_norms = norm(ccd_pixel_room, axis=-1)
        ccd_pixel_room_norm = ccd_pixel_room / ccd_pixel_room_norms[:, newaxis]
        # print "ccd_pixel_room_norm.shape", ccd_pixel_room_norm.shape

        q_xray = diffr.photon.q		# 2*pi / d   [1 / nm]
        qxyz_sphere = ccd_pixel_room_norm * q_xray + array([-q_xray, 0, 0])

        incidence_rad = deg2rad(incidence)
        chi_rad = deg2rad(chi)
        phi_rad = deg2rad(phi)

        incidence_rotation = array([
            [ cos(incidence_rad),	0,	-sin(incidence_rad)	],
            [ 0,					1,	 0					],
            [ sin(incidence_rad),	0,	 cos(incidence_rad)	] ])

        chi_rotation = array([
            [ 1,	0,	 			 0				],
            [ 0,	cos(chi_rad),	-sin(chi_rad)	],
            [ 0,	sin(chi_rad),	 cos(chi_rad)	] ])

        # need to verify sign of sin() components
        # this version (mathematica, not IGOR) appears correct
        phi_rotation = array([
            [ cos(phi_rad),	 -sin(phi_rad),  	0	],
            [ sin(phi_rad),	  cos(phi_rad),		0	],
            [ 0,			  0,				1	] ])

        qxyz_normal = array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1] ])

        # lattice_a = 42	#nm
        # lattice_spacing = array([lattice_a, lattice_a, 1])
        # q_lattice_spacing = 2 * pi / lattice_spacing
        q_lattice_spacing = array([1, 1, 1])
        qxyz_rotated = incidence_rotation.dot(
            chi_rotation).dot(phi_rotation).dot(qxyz_normal)
        # print "qxyz_rotated.shape", qxyz_rotated.shape
        # Rotation leaves new unit vectors as columns
        # Divide 1st COLUMN by 2*pi/a
        # Divide 2nd COLUMN by 2*pi/b
        # Divide 3rd COLUMN by 2*pi/c
        hkl_rotated = qxyz_rotated / q_lattice_spacing[newaxis, :]
        # print "hkl_rotated.shape", hkl_rotated.shape
        hkl_map = qxyz_sphere.dot(hkl_rotated)
        # print "hkl_map.shape", hkl_map.shape
        ccd_int_qxqy = array([
            hkl_map[:, 0],
            hkl_map[:,1],
            ccd_pixel_intensities])
        # print "ccd_int_qxqy.shape", ccd_int_qxqy.shape
        ccd_int_qxqy = ccd_int_qxqy.transpose()
        # print "ccd_int_qxqy.shape (transposed)", ccd_int_qxqy.shape

        row_values = tile(arange(num_rows), (num_cols, 1)).transpose()
        row_values = row_values.reshape(num_rows * num_cols)
        col_values = tile(arange(num_cols), (num_rows, 1))
        col_values = col_values.reshape(num_rows * num_cols)
        df_qxyz = pd.DataFrame({
            "row": row_values,
            "col": col_values,
            "Qx": hkl_map[:, 0],
            "Qy": hkl_map[:, 1],
            "Qz": hkl_map[:, 2],
            "Counts": ccd_pixel_intensities,
            })

        return( df_qxyz )


class QSpacePath():

    """QSpacePath: Build a path through reciprocal (Q) space

        *) Export scan files for use at ALS BL 4.0.2 Diffractometer

        *) Qx is along relative azimuth = 0 deg (uses offset)
        *) Qy is along relative azimuth = 90 deg (uses offset)
        *) Qz is along azimuthal axis

        *) Q1 is along absolute azimuth = 0 deg (offset = 0)
        *) Q2 is along absolute azimuth = 90 deg (offset = 0)
        *) Q3 is along azimuthal axis
    """

    def __init__(self,
            diffractometer=None,
            offset_diffractometer=None):
        """Attach a diffractometer for generating QSpacePath angles

            diffractometer: diffractometer object to generate angles, motions
            offset_diffractometer: Extract relevant angle offsets
                for calibrating exported scans
        """
        self._build_diffractometer(diffractometer, offset_diffractometer)
        self.angles = None

    def _build_diffractometer(self,
            diffractometer=None,
            offset_diffractometer=None):
        """Attach a diffractometer for generating QSpacePath angles

            diffractometer: diffractometer object to generate angles, motions
            offset_diffractometer: Extract relevant angle offsets
                for calibrating exported scans
        """
        if diffractometer:
            self._diffractometer = diffractometer
        else:
            self._diffractometer = Diffractometer402()

        if offset_diffractometer:
            self._diffractometer.azimuth += offset_diffractometer.azimuth
            # Move sample, rather than move model...opposite offsets
            self._diffractometer.offset_step(
                "transverse", -offset_diffractometer.transverse)
            self._diffractometer.offset_step(
                "incidence", -offset_diffractometer.incidence)

    def lin_path(self,
        q_start = array([0, 0, 0]),
        q_stop = array([0, 0, 1]),
        num_samples = 31 ):
        """Define a linear path through reciprocal (Q) space

            q_start: starting point, array([Qx, Qy, Qz]) in 1/nm
            q_stop: ending point, array([Qx, Qy, Qz]) in 1/nm
            num_samples: number of points (M) to generate

            set(self.angles):
                M x 3 array([2theta, incidence, transverse (chi)])
        """

        qx_values = linspace(q_start[0], q_stop[0], num_samples, endpoint=True)
        qy_values = linspace(q_start[1], q_stop[1], num_samples, endpoint=True)
        qz_values = linspace(q_start[2], q_stop[2], num_samples, endpoint=True)

        q_values = array([qx_values, qy_values, qz_values]).transpose()

        self.angles = self.q2angles(q_values)

    def q2angles(self, q_points = None):
        """Convert an array of reciprocal (Q) space points into ideal angles

            *** Assumes that ideal angles are calculated at fixed azimuth
            q_points: M x 3 array([Qx, Qy, Qz]) in 1/nm

            returns: M x 3 array([2theta, incidence, transverse (chi)])
        """

        if q_points is None:
            q_points = array([
                [0, 0, 0],
                ])

        diffr = self._diffractometer

# 		incidence_rad = deg2rad(incidence)
# 		transverse_rad = deg2rad(transverse)
# 		azimuth_rad = deg2rad(azimuth)
        azimuth_rad = deg2rad(diffr.azimuth)

# 		incidence_rotation = array([
# 			[ cos(incidence_rad),	0,	-sin(incidence_rad)	],
# 			[ 0,					1,	 0					],
# 			[ sin(incidence_rad),	0,	 cos(incidence_rad)	] ])
# 	
# 		transverse_rotation = array([
# 			[ 1,	0,	 			 		 0				],
# 			[ 0,	cos(transverse_rad),	-sin(transverse_rad)	],
# 			[ 0,	sin(transverse_rad),	 cos(transverse_rad)	] ])

        azimuth_rotation = array([
            [ cos(azimuth_rad),	-sin(azimuth_rad),  0	],
            [ sin(azimuth_rad),	 cos(azimuth_rad),	0	],
            [ 0,			  	 0,					1	] ])

        # Convert q_points (relative to sample azimuth = 0)
        #   into q123_points (has no azimuthal motion)
        q123_points = [azimuth_rotation.dot(q_point) for q_point in q_points]

# 		transverse_solutions = [
# 			brentq(f, -pi, pi, args=(q123_point) 
# 				) for q123_point in q123_points]

        # transverse, chi = arctan(Q2 / Q3)
        transverse_angles = rad2deg([(
            arctan2(q123_point[1], q123_point[2])
            ) for q123_point in q123_points])

        # incidence_offset = arctan(Q1 / norm(Q2,Q3) )
        incidence_angles = rad2deg([(
            arctan2(q123_point[0], norm(q123_point[1:]) )
            ) for q123_point in q123_points])

        # theta = arcsin(Q / 2*Q_xray)
        theta_angles = rad2deg([(
            arcsin(norm(q123_point) / (2 * diffr.photon.q) )
            ) for q123_point in q123_points])

        twoTheta_angles = 2 * theta_angles

        incidence_angles += theta_angles

        angles = array([
            twoTheta_angles,
            incidence_angles,
            transverse_angles,
            ]).transpose()

        return angles

    def is_accessible(self, twotheta, incidence, transverse, tolerance=2.0):
        """True if reciprocal space is accessible at angles requested

            tolerance = tolerable incidence (in deg.) beyond accessible limits
        """

        if ( isnan(twotheta) or isnan(incidence) or isnan(transverse) ):
            return False

        if (-tolerance < incidence) and (incidence < (twotheta + tolerance) ):
            return True
        else:
            return False

    def angles2motors(self, twotheta, incidence, transverse,
            validate_motors = True):
        """Convert ideal angles into ALS BL 4.0.2 motor values"""

        if ( isnan(twotheta) or isnan(incidence) or isnan(transverse) ):
            return (nan, nan, nan)

        diffr = self._diffractometer

        diffr.twotheta = twotheta
        diffr.incidence = incidence
        diffr.transverse = transverse

        if (validate_motors == True) and not diffr.valid_motors():
            return (nan, nan, nan)

        return (diffr.bottom_angle, diffr.top_angle, diffr.flip_angle)

    def export_scanfile(self,
            output_filename="test.scn",
            export_energy = True,
            export_polarization = True):
        """Convert reciprocal space path into a scan file (ALS BL 4.0.2)"""

        diffr = self._diffractometer

        accessible_angles = self.angles[
            array([
                array(self.is_accessible(*tuple(angle_values) )
                    ) for angle_values in self.angles])
            ]

        motors = array([
            array(self.angles2motors(*tuple(angle_values) )
                ) for angle_values in accessible_angles])
        # Remove 'nan' rows
        motors = motors[isfinite(motors).all(axis=1)]

        col_names = []
        col_values = []
        if (export_energy == True):
            energies = full(len(motors), diffr.energy)
            col_names += ["Mono Energy", "EPU Energy"]
            col_values += [energies, energies]
        if (export_polarization == True):
            polarizations = full(len(motors), diffr.polarization.value)
            col_names += ["EPU Polarization"]
            col_values += [polarizations]
        col_names += ["Bottom Rotary Seal", "Top Rotary Seal", "Flip"]

        if len(col_values) > 0:
            motor_values = hstack((
                array(col_values).transpose(),
                around(motors, 3),
                ))
        else:
            motor_values = around(motors, 3)

        scan_motors = pd.DataFrame(motor_values, columns=col_names)
        scan_motors.to_csv(
            output_filename,
            sep = '\t',
            index = False,
            line_terminator = "\r\n",
            )


class ResonanceProfile():

    """ResonanceProfile: Photon energy changes at constant reciprocal point, Q

        *) Export scan files for use at ALS BL 4.0.2 Diffractometer

        *) Qx is along relative azimuth = 0 deg (uses offset)
        *) Qy is along relative azimuth = 90 deg (uses offset)
        *) Qz is along azimuthal axis

        *) Q1 is along absolute azimuth = 0 deg (offset = 0)
        *) Q2 is along absolute azimuth = 90 deg (offset = 0)
        *) Q3 is along azimuthal axis
    """

    def __init__(self,
            q_value,
            diffractometer=None,
            offset_diffractometer=None):
        """Constant reciprocal point, Q = (Qx, Qy, Qz)
            Attach a diffractometer for generating ResonanceProfile angles

            q_value: reciprocal point, array([Qx, Qy, Qz]) in 1/nm
            diffractometer: diffractometer object to generate angles, motions
            offset_diffractometer: Extract relevant angle offsets
                for calibrating exported scans
        """
        if len(q_value) == 3:
            self.q = array([ q_value ])
        else:
            self.q = array([ [0, 0, 1] ])	# Better default available?

        self._build_diffractometer(diffractometer, offset_diffractometer)
        self.angles = None

    def _build_diffractometer(self,
            diffractometer=None,
            offset_diffractometer=None):
        """Attach a diffractometer for generating QSpacePath angles

            diffractometer: diffractometer object to generate angles, motions
            offset_diffractometer: Extract relevant angle offsets
                for calibrating exported scans
        """
        if diffractometer:
            self._diffractometer = diffractometer
        else:
            self._diffractometer = Diffractometer402()

        if offset_diffractometer:
            self._diffractometer.azimuth += offset_diffractometer.azimuth
            # Move sample, rather than move model...opposite offsets
            self._diffractometer.offset_step(
                "transverse", -offset_diffractometer.transverse)
            self._diffractometer.offset_step(
                "incidence", -offset_diffractometer.incidence)

    def new_spectrum(self,
        energies):
        """Define a resonance profile for the energies

            energies: array() of energy values defining the resonance profile

            set(self.angles):
                M x 3 array([2theta, incidence, transverse (chi)])
                Adjusted for each energy to maintain constant Q
        """

        self.energies = energies

        diffr = self._diffractometer
        q_value = self.q
        angles = []
        for energy in energies:

            diffr.energy = energy
            angles.append( self.q2angles(q_value)[0] )

        self.angles = array(angles)

    def q2angles(self, q_points = None):
        """Convert an array of reciprocal (Q) space points into ideal angles

            *** Assumes that ideal angles are calculated at fixed azimuth
            q_points: M x 3 array([Qx, Qy, Qz]) in 1/nm

            returns: M x 3 array([2theta, incidence, transverse (chi)])
        """

        if q_points is None:
            q_points = array([
                [0, 0, 0],
                ])

        diffr = self._diffractometer

# 		incidence_rad = deg2rad(incidence)
# 		transverse_rad = deg2rad(transverse)
# 		azimuth_rad = deg2rad(azimuth)
        azimuth_rad = deg2rad(diffr.azimuth)

# 		incidence_rotation = array([
# 			[ cos(incidence_rad),	0,	-sin(incidence_rad)	],
# 			[ 0,					1,	 0					],
# 			[ sin(incidence_rad),	0,	 cos(incidence_rad)	] ])
# 	
# 		transverse_rotation = array([
# 			[ 1,	0,	 			 		 0				],
# 			[ 0,	cos(transverse_rad),	-sin(transverse_rad)	],
# 			[ 0,	sin(transverse_rad),	 cos(transverse_rad)	] ])

        azimuth_rotation = array([
            [ cos(azimuth_rad),	-sin(azimuth_rad),  0	],
            [ sin(azimuth_rad),	 cos(azimuth_rad),	0	],
            [ 0,			  	 0,					1	] ])

        # Convert q_points (relative to sample azimuth = 0)
        #   into q123_points (has no azimuthal motion)
        q123_points = [azimuth_rotation.dot(q_point) for q_point in q_points]

# 		transverse_solutions = [
# 			brentq(f, -pi, pi, args=(q123_point) 
# 				) for q123_point in q123_points]

        # transverse, chi = arctan(Q2 / Q3)
        transverse_angles = rad2deg([(
            arctan2(q123_point[1], q123_point[2])
            ) for q123_point in q123_points])

        # incidence_offset = arctan(Q1 / norm(Q2,Q3) )
        incidence_angles = rad2deg([(
            arctan2(q123_point[0], norm(q123_point[1:]) )
            ) for q123_point in q123_points])

        # theta = arcsin(Q / 2*Q_xray)
        theta_angles = rad2deg([(
            arcsin(norm(q123_point) / (2 * diffr.photon.q) )
            ) for q123_point in q123_points])

        twoTheta_angles = 2 * theta_angles

        incidence_angles += theta_angles

        angles = array([
            twoTheta_angles,
            incidence_angles,
            transverse_angles,
            ]).transpose()

        return angles

    def is_accessible(self, twotheta, incidence, transverse, tolerance=2.0):
        """True if reciprocal space is accessible at angles requested

            tolerance = tolerable incidence (in deg.) beyond accessible limits
        """

        if ( isnan(twotheta) or isnan(incidence) or isnan(transverse) ):
            return False

        if (-tolerance < incidence) and (incidence < (twotheta + tolerance) ):
            return True
        else:
            return False

    def angles2motors(self, twotheta, incidence, transverse,
            validate_motors = True):
        """Convert ideal angles into ALS BL 4.0.2 motor values"""

        if ( isnan(twotheta) or isnan(incidence) or isnan(transverse) ):
            return (nan, nan, nan)

        diffr = self._diffractometer

        diffr.twotheta = twotheta
        diffr.incidence = incidence
        diffr.transverse = transverse

        if (validate_motors == True) and not diffr.valid_motors():
            return (nan, nan, nan)

        return (diffr.bottom_angle, diffr.top_angle, diffr.flip_angle)

    def export_scanfile(self,
            output_filename="test.scn",
            polarizations = None,
            alternate_polarization = False,
            export_polarization = True):
        """Convert resonance profile into a scan file (ALS BL 4.0.2)"""

        diffr = self._diffractometer

        accessible_angles = self.angles[
            array([
                array(self.is_accessible(*tuple(angle_values) )
                    ) for angle_values in self.angles])
            ]

        motors = array([
            array(self.angles2motors(*tuple(angle_values) )
                ) for angle_values in accessible_angles])
        # Remove 'nan' rows
        motors = motors[isfinite(motors).all(axis=1)]

        polarization_values = None
        energy_list = []
        pol_list = []
        motor_list = []

        if (export_polarization == True) and (polarizations is None):
            polarization_values = full(len(motors), diffr.polarization.value)

        if (polarizations is not None) and (alternate_polarization == False):
            for polarization in polarizations:
                energy_list.append(self.energies)
                pol_list.append( full(len(motors), polarization) )
                motor_list.append(motors)
            energy_values = hstack(( tuple(energy_list) ))
            polarization_values = hstack(( tuple(pol_list) ))
            # motor_values = hstack(( tuple(motor_list) ))
            motor_values = vstack(( tuple(motor_list) ))

        if (polarizations is not None) and (alternate_polarization == True):
            for (energy, motor_positions) in zip(self.energies, motors):
                energy_list.append( full(len(polarizations), energy) )
                pol_list.append(polarizations)
                motor_list.append(
                    full(
                        (len(polarizations), len(motor_positions)),
                        motor_positions)
                    )
            energy_values = hstack(( tuple(energy_list) ))
            polarization_values = hstack(( tuple(pol_list) ))
            # motor_values = hstack(( tuple(motor_list) ))
            motor_values = vstack(( tuple(motor_list) ))


        col_names = ["Mono Energy", "EPU Energy"]
        col_values = [energy_values, energy_values]
        if (polarization_values is not None):
            col_names += ["EPU Polarization"]
            col_values += [polarization_values]
        col_names += ["Bottom Rotary Seal", "Top Rotary Seal", "Flip"]

        motor_entries = hstack((
            array(col_values).transpose(),
            around(motor_values, 3),
            ))

        scan_motors = pd.DataFrame(motor_entries, columns=col_names)
        scan_motors.to_csv(
            output_filename,
            sep = '\t',
            index = False,
            line_terminator = "\r\n",
            )


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN:  Testing of module
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def print_photon(photon):
    """Print properties of the photon"""

    print "****************************"
    print "   energy (eV) = " + str(photon.energy)
    print "   lambda (nm) = " + str(photon.wavelength)
    print "   q (1/nm)    = " + str(photon.q)


def test_photon():
    """Basic tests of the class<Photon>"""

    print "\nTesting class<Photon>"
    xray = Photon(energy=700)
    print_photon(xray)
    xray.energy = 642
    print_photon(xray)
    xray.wavelength = 2
    print_photon(xray)
    xray.q = 2
    print_photon(xray)


def print_polarization(pol):
    """Print properties of the polarization"""

    state_text = dict({
        -1: "UNDEFINED",
        0:	"CIRCULAR",
        1:	"LINEAR" })
    print "****************************"
    print "   value             = " + str(pol.value)
    print "   state             = " + (state_text[pol.state] +
                                        " (" + str(pol.state) + ")")
    print "   deg. circ.        = " + str(pol.circular_degree)
    print "   lin. angle. (deg) = " + str(pol.linear_angle)


def test_polarization():
    """Basic tests of the class<Polarization>"""

    print "\nTesting class<Polarization>"
    pol = Polarization(0)
    print_polarization(pol)
    pol.value = 100
    print_polarization(pol)
    pol.value = 190
    print_polarization(pol)
    pol.value = 200
    print_polarization(pol)
    pol.value = 0.9
    print_polarization(pol)
    pol.value = 1
    print_polarization(pol)
    pol.value = -1
    print_polarization(pol)
    pol.value = 1.
    print_polarization(pol)
    pol.value = -1.
    print_polarization(pol)


def print_diffractometer(diffr):
    """Print properties of the diffractometer"""

    print "****************************"
    print "   twotheta (deg)      = " + str(diffr.twotheta)
    print "   incidence (deg)     = " + str(diffr.incidence)
    print "   transverse (deg)    = " + str(diffr.transverse)
    print "   azimuth (deg)       = " + str(diffr.azimuth)
    print "   photon..."
    print_photon(diffr.photon)
    print "   polarization..."
    print_polarization(diffr.polarization)
    print "   intensity0 (counts) = " + str(diffr.intensity0)
    print "   temperature (K)     = " + str(diffr.temperature)
    print "   distance (mm)       = " + str(diffr.distance)


def test_diff402():
    """Basic tests of the class<Diffractometer402>"""

    print "\nTesting class<Diffractometer402>"
    chamber_params = dict({
        'Beamline Energy': 700,
        'EPU Polarization': 0,
        'Bottom Rotary Seal': 15,
        'Top Rotary Seal': 137,
        'Flip': -2,
        'Flip Offset': -1,
        'Top Offset': 2,
        'Twice Top Offset': 4,
        'CCD Offset': -18.68,
        'DATE': "2015-02-12",
        'Counter 2': 340*1000,
        'TempCtrlrA': 296,
        'TempCtrlrB': 295 })
    chamber = Diffractometer402(param_dict=chamber_params)
    print_diffractometer(chamber)


class SmartFormatter(argparse.HelpFormatter):
    """Copied from 'Anthon' (https://stackoverflow.com/a/22157136)"""

    def _split_lines(self, text, width):
        """Allows '\n' in help strings that start with 'R|'"""

        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def main():
    parser = argparse.ArgumentParser(
        usage=__doc__,

        description="Command line usage: Basic tests of module functionality",
        formatter_class=SmartFormatter,
        )
    # parser.add_argument(
    #     "--version",
    #     action="store_true",
    #     help="Display PEP440 version identifier",
    #     )
    parser.add_argument(
        "--version",
        action="version",
        version="{} {}".format(__package__, __version__),
        help="Display PEP440 version identifier",
        )
    parser.add_argument(
        '--test',
        action='append',
        default=[],
        help="R|Name of test to run; "
             "Multiple tests allowed by repeating this option."
             "\ne.g., --test diffractometer --test photon --test pol"
             "{}{}{}".format(
                "\nd[iff[r[actometer]]]: {}".format(test_diff402.__doc__),
                "\nph[oton]: {}".format(test_photon.__doc__),
                "\npol[arization]: {}".format(test_polarization.__doc__),
                ),
        )
    args = parser.parse_args()

    # Tests of module functionality
    for module_test in args.test:
        if module_test in ["diffractometer", "diffract", "diffr", "diff", "d"]:
            test_diff402()
        elif module_test in ["photon", "ph"]:
            test_photon()
        elif module_test in ["polarization", "pol"]:
            test_polarization()
        else:
            pass


if __name__ == "__main__":
    main()
