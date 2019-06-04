# **************************************************************************
# *
# * Authors:     Josue Gomez Blanco (josue.gomez-blanco@mcgill.ca)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
"""
This module contains converter functions that will serve to:
1. Write from base classes to Grigorieff packages specific files
2. Read from Grigorieff packages files to base classes
"""

import os
import re
from itertools import izip
from collections import OrderedDict
import numpy as np

#from numpy import rad2deg, deg2rad
#from np.linalg import inv

from pyworkflow.object import Float
import pyworkflow.em as em
import pyworkflow.em.convert.transformations as transformations


HEADER_COLUMNS = ['INDEX', 'PSI', 'THETA', 'PHI', 'SHX', 'SHY', 'MAG',
                  'FILM', 'DF1', 'DF2', 'ANGAST', 'OCC',
                  '-LogP', 'SIGMA', 'SCORE', 'CHANGE']


class FrealignParFile(object):
    """ Handler class to read/write frealign metadata."""
    def __init__(self, filename, mode='r'):
        self._file = open(filename, mode)
        self._count = 0

    def __iter__(self):
        """PSI   THETA     PHI       SHX       SHY     MAG  FILM      DF1      DF2  ANGAST     OCC     -LogP      SIGMA   SCORE  CHANGE
        """
        for line in self._file:
            line = line.strip()
            if not line.startswith('C'):
                row = OrderedDict(zip(HEADER_COLUMNS, line.split()))
                yield row

    def close(self):
        self._file.close()


def readSetOfParticles(inputSet, outputSet, parFileName):
    """
     Iterate through the inputSet and the parFile lines
     and populate the outputSet with the same particles
     of inputSet, but with the angles and shift (3d alignment)
     updated from the parFile info.
     It is assumed that the order of iteration of the particles
     and the lines match and have the same number.
    """
    #create dictionary that matches input particles with param file
    samplingRate = inputSet.getSamplingRate()
    parFile = FrealignParFile(parFileName)
    partIter = iter(inputSet.iterItems(orderBy=['_micId', 'id'], direction='ASC'))
     
    for particle, row in izip(partIter, parFile):        
        particle.setTransform(rowToAlignment(row, samplingRate))
        # We assume that each particle have ctfModel
        # in order to be processed in Frealign
        # JMRT: Since the CTF will be set, we can setup
        # an empty CTFModel object
        if not particle.hasCTF():
            particle.setCTF(em.CTFModel())
        rowToCtfModel(row, particle.getCTF())
        outputSet.append(particle)
    outputSet.setAlignment(em.ALIGN_PROJ)


def rowToAlignment(alignmentRow, samplingRate):
    """
    Return an Transform object representing the Alignment
    from a given parFile row.
    """
    angles = np.zeros(3)
    shifts = np.zeros(3)
    alignment = em.Transform()
    # PSI   THETA     PHI       SHX       SHY
    angles[0] = float(alignmentRow.get('PSI'))
    angles[1] = float(alignmentRow.get('THETA'))
    angles[2] = float(alignmentRow.get('PHI'))
    shifts[0] = float(alignmentRow.get('SHX'))/samplingRate
    shifts[1] = float(alignmentRow.get('SHY'))/samplingRate

    M = matrixFromGeometry(shifts, angles)
    alignment.setMatrix(M)

    return alignment


def matrixFromGeometry(shifts, angles):
    """ Create the transformation matrix from a given
    2D shifts in X and Y...and the 3 euler angles.
    """
    inverseTransform = True
    radAngles = -np.deg2rad(angles)

    M = transformations.euler_matrix(
        radAngles[0], radAngles[1], radAngles[2], 'szyz')
    if inverseTransform:
        M[:3, 3] = -shifts[:3]
        M = np.linalg.inv(M)
    else:
        M[:3, 3] = shifts[:3]

    return M


def rowToCtfModel(ctfRow, ctfModel):
    defocusU = float(ctfRow.get('DF1'))
    defocusV = float(ctfRow.get('DF2'))
    defocusAngle = float(ctfRow.get('ANGAST'))
    ctfModel.setStandardDefocus(defocusU, defocusV, defocusAngle)


# ------------- Old functions (before using EMX matrix for alignment) ------
def parseCtffindOutput(filename):
    """ Retrieve defocus U, V and angle from the
    output file of the ctffind3 execution.
    """
    result = None
    if os.path.exists(filename):
        f = open(filename)
        for line in f:
            if 'Final Values' in line:
                # Take DefocusU, DefocusV and Angle as a tuple
                # that are the first three values in the line
                result = tuple(map(float, line.split()[:3]))
                break
        f.close()
    return result


def parseCtffind4Output(filename):
    """ Retrieve defocus U, V and angle from the
    output file of the ctffind4 execution.
    """
    result = None
    if os.path.exists(filename):
        f = open(filename)
        for line in f:
            if not line.startswith("#"):
                result = tuple(map(float, line.split()[1:]))
                # Stop reading. In ctffind4-4.0.15 output file has additional lines.
                break
        f.close()
    return result


def parseCtftiltOutput(filename):
    """ Retrieve defocus U,V,angle,tilt axis,tilt angle,CC from the
    output file of the ctftilt execution.
    """
    result = None
    if os.path.exists(filename):
        f = open(filename)
        for line in f:
            if 'Final Values' in line:
                result = tuple(map(float, line.split()[:6]))
                break
        f.close()
    return result


def ctffindOutputVersion(filename):
    """ Detect the ctffind version (3 or 4) that produced
    the given filename.
    """
    f = open(filename)
    for line in f:
        if 'Output from CTFFind version 4.' in line:
            return 4
    return 3


def setWrongDefocus(ctfModel):
    ctfModel.setDefocusU(-999)
    ctfModel.setDefocusV(-1)
    ctfModel.setDefocusAngle(-999)
    
    
def readCtfModel(ctfModel, filename, ctf4=False, ctfTilt=False):
    if ctfTilt:
        result = parseCtftiltOutput(filename)
        if result is None:
            setWrongDefocus(ctfModel)
            tiltAxis, tiltAngle, ctfFit = -999, -999, -999
        else:
            defocusU, defocusV, defocusAngle, tiltAxis, tiltAngle, ctfFit = result
            ctfModel.setStandardDefocus(defocusU, defocusV, defocusAngle)
        ctfModel.setFitQuality(ctfFit)
        ctfModel._ctftilt_tiltAxis = Float(tiltAxis)
        ctfModel._ctftilt_tiltAngle = Float(tiltAngle)

    if not ctf4:
        result = parseCtffindOutput(filename)
        if result is None:
            setWrongDefocus(ctfModel)
        else:
            defocusU, defocusV, defocusAngle = result
            ctfModel.setStandardDefocus(defocusU, defocusV, defocusAngle)
    else:
        result = parseCtffind4Output(filename)
        if result is None:
            setWrongDefocus(ctfModel)
            ctfFit, ctfResolution, ctfPhaseShift = -999, -999, -999
        else:
            defocusU, defocusV, defocusAngle, ctfPhaseShift, ctfFit, ctfResolution = result
            ctfModel.setStandardDefocus(defocusU, defocusV, defocusAngle)
        ctfModel.setFitQuality(ctfFit)
        ctfModel.setResolution(ctfResolution)

        # Avoid creation of phaseShift
        ctfPhaseShiftDeg = np.rad2deg(ctfPhaseShift)
        if ctfPhaseShiftDeg != 0:
            ctfModel.setPhaseShift(ctfPhaseShiftDeg)


def geometryFromMatrix(matrix, inverseTransform=True):
    if inverseTransform:
        matrix = np.linalg.inv(matrix)
        shifts = -transformations.translation_from_matrix(matrix)
    else:
        shifts = transformations.translation_from_matrix(matrix)
    angles = -np.rad2deg(transformations.euler_from_matrix(matrix, axes='szyz'))

    return shifts, angles


def geometryFromAligment(alignment):
    shifts, angles = geometryFromMatrix(alignment.getMatrix(), True)

    return shifts, angles


def _createErrorCtf4Fn(self, filename):
            f = open(filename, 'w+')
            lines = """# Error report file 
  -999       -999       -999       -999       -999      -999       -999     
"""
            f.write(lines)
            f.close()


def _createErrorCtf3Fn(self, filename):
    f = open(filename, 'w+')
    lines = """-999    -999       -999     -999  Final Values"""
    f.write(lines)
    f.close()


def readShiftsMovieAlignment(shiftFn):
    f = open(shiftFn)
    xshifts = []
    yshifts = []

    for line in f:
        l = line.strip()
        if not l.startswith('#'):
            parts = l.split()
            if len(xshifts) == 0:
                xshifts = [float(i) for i in parts]
            else:
                yshifts = [float(i) for i in parts]
    f.close()
    return xshifts, yshifts


def writeShiftsMovieAlignment(movie, shiftsFn, s0, sN):
    movieAlignment=movie.getAlignment()
    shiftListX, shiftListY = movieAlignment.getShifts()
    
    # Generating metadata for global shifts
    a0, aN = movieAlignment.getRange()
    alFrame = a0
    
    if s0 < a0:
        diff = a0 - s0
        initShifts = "0.0000 " * diff
    else:
        initShifts = ""
    
    if sN > aN:
        diff = sN - aN
        finalShifts = "0.0000 " * diff
    else:
        finalShifts = ""
    
    shiftsX = ""
    shiftsY = ""
    for shiftX, shiftY in izip(shiftListX, shiftListY):
        if alFrame >= s0 and alFrame <= sN:
            shiftsX = shiftsX + "%0.4f " % shiftX
            shiftsY = shiftsY + "%0.4f " % shiftY
        alFrame += 1
    
    f=open(shiftsFn,'w')
    shifts = (initShifts + shiftsX + " " + finalShifts + "\n" 
              + initShifts + shiftsY + " " + finalShifts)
    f.write(shifts)
    f.close()


def parseMagEstOutput(filename):
    result = []
    ansi_escape = re.compile(r'\x1b[^m]*m')
    if os.path.exists(filename):
        f = open(filename)
        parsing = False
        for line in f:
            l = ansi_escape.sub('', line)
            line = re.sub('[%]', '', l).strip()
            if line.startswith("The following distortion parameters were found"):
                parsing = True
            if parsing:
                if 'Distortion Angle' in line:
                    result.append(float(line.split()[3]))
                if 'Major Scale' in line:
                    result.append(float(line.split()[3]))
                if 'Minor Scale' in line:
                    result.append(float(line.split()[3]))
            if line.startswith("Stretch only parameters would be as follows"):
                parsing = False
            if 'Corrected Pixel Size' in line:
                result.append(float(line.split()[4]))
            if 'The Total Distortion =' in line:
                result.append(float(line.split()[4]))
        f.close()

    return result


def parseMagCorrInput(filename):
    result = []
    ansi_escape = re.compile(r'\x1b[^m]*m')
    if os.path.exists(filename):
        f = open(filename)
        parsing = False
        for line in f:
            l = ansi_escape.sub('', line)
            line = re.sub('[%]', '', l).strip()
            if line.startswith("Stretch only parameters would be as follows"):
                parsing = True
            if parsing:
                if 'Distortion Angle' in line:
                    result.append(float(line.split()[3]))
                if 'Major Scale' in line:
                    result.append(float(line.split()[3]))
                if 'Minor Scale' in line:
                    result.append(float(line.split()[3]))
            if 'Corrected Pixel Size' in line:
                result.append(float(line.split()[4]))
        f.close()

    return result


def unDistortCoord(params):
    # http://grigoriefflab.janelia.org/node/5140#comment-1238
    # no need to invert Y-axis since we calculate relative to
    # the center of mic

    if len(params) != 7:
        raise Exception("Not enough params for undistorting!")
    x_original, y_original, mic_x, mic_y, ang, major_scale, minor_scale = params
    angle_rad = np.rad2deg(ang)

    # pixel location relative to center of micrograph
    x = float(x_original) - float(mic_x) / 2.0
    y = float(y_original) - float(mic_y) / 2.0

    # rotate
    r = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x) + angle_rad

    # scale
    x = r * np.cos(phi) * major_scale
    y = r * np.sin(phi) * minor_scale

    # rotate back
    r = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x) - angle_rad

    # pixel location relative to edge of micrograph
    x_correct = r * np.cos(phi) + float(mic_x) / 2.0
    y_correct = r * np.sin(phi) + float(mic_y) / 2.0

    return x_correct, y_correct
