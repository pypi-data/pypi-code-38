# **************************************************************************
# *
# * Authors:     Josue Gomez BLanco (josue.gomez-blanco@mcgill.ca)
# *              J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [2]
# *
# * [2] SciLifeLab, Stockholm University
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

import pyworkflow.em as pwem
import pyworkflow.protocol.params as params

from grigoriefflab import Plugin
from grigoriefflab.constants import (V4_0_15, V4_1_10, CTFFIND, CTFFIND4)
import grigoriefflab.convert as convert


class ProgramCtffind:
    """
    Wrapper of Ctffind programs (3 and 4) that will handle parameters definition
    and also execution of the program with the proper arguments.
    This class is not a Protocol, but it is related, since it can be used from
    protocols that perform CTF estimation.
    """
    def __init__(self, protocol):
        self._program = self._getProgram()  # Load program to use
        self._findPhaseShift = protocol.findPhaseShift.get()
        self._args, self._params = self._getArgs(protocol)  # Load general arguments

    @classmethod
    def defineFormParams(cls, form):
        """ Define some parameters from this program into the given form. """
        form.addParam('useCtffind4', params.BooleanParam, default=True,
                      label="Use ctffind4 to estimate the CTF?",
                      help='If is true, the protocol will use ctffind4 instead of ctffind3')
        form.addParam('astigmatism', params.FloatParam, default=100.0,
                      label='Expected (tolerated) astigmatism (A)',
                      expertLevel=params.LEVEL_ADVANCED,
                      help='Astigmatism values much larger than this will be penalised '
                           '(Angstroms; set negative to remove this restraint)',
                      condition='useCtffind4')
        form.addParam('findPhaseShift', params.BooleanParam, default=False,
                      label="Find additional phase shift?", condition='useCtffind4',
                      help='If the data was collected with phase plate, this will find '
                           'additional phase shift due to phase plate',
                      expertLevel=params.LEVEL_ADVANCED)

        group = form.addGroup('Phase shift parameters')
        group.addParam('minPhaseShift', params.FloatParam, default=0.0,
                       label="Minimum phase shift (rad)", condition='findPhaseShift',
                       help='Lower bound of the search for additional phase shift. '
                            'Phase shift is of scattered electrons relative to '
                            'unscattered electrons. In radians.',
                       expertLevel=params.LEVEL_ADVANCED)
        group.addParam('maxPhaseShift', params.FloatParam, default=3.15,
                       label="Maximum phase shift (rad)", condition='findPhaseShift',
                       help='Upper bound of the search for additional phase shift. '
                            'Phase shift is of scattered electrons relative to '
                            'unscattered electrons. In radians. '
                            'Please use value between 0.10 and 3.15',
                       expertLevel=params.LEVEL_ADVANCED)
        group.addParam('stepPhaseShift', params.FloatParam, default=0.2,
                       label="Phase shift search step (rad)", condition='findPhaseShift',
                       help='Step size for phase shift search (radians)',
                       expertLevel=params.LEVEL_ADVANCED)

        form.addParam('resamplePix', params.BooleanParam, default=True,
                      label="Resample micrograph if pixel size too small?",
                      condition='isNewCtffind4',
                      help='When the pixel is too small, Thon rings appear very thin '
                           'and near the origin of the spectrum, which can lead to '
                           'suboptimal fitting. This options resamples micrographs to '
                           'a more reasonable pixel size if needed',
                      expertLevel=params.LEVEL_ADVANCED)

        form.addParam('slowSearch', params.BooleanParam, default=True,
                      expertLevel=params.LEVEL_ADVANCED,
                      label="Slower, more exhaustive search?",
                      condition='isNewCtffind4',
                      help="From version 4.1.5 to 4.1.8 the slow (more precise) "
                           "search was activated by default because of reports the "
                           "faster 1D search was significantly less accurate "
                           "(thanks Rado Danev & Tim Grant). "
                           "Set this parameters to *No* to get faster fits.")

    @staticmethod
    def getVersion():
        return Plugin.getActiveVersion(CTFFIND4)

    @staticmethod
    def isNewCtffind4():
        return ProgramCtffind.getVersion() != V4_0_15

    @staticmethod
    def _getProgram():
        """ Return the program to be used. """
        # FIXME: number of threads are used for steps, not for OpenMP, what should we do?
        # useThreads = self._protocol.numberOfThreads > 1
        useThreads = False
        program = 'export OMP_NUM_THREADS=1; '  # FIXME: consider using OpenMPI threads
        program += Plugin.getProgram(CTFFIND4, useMP=useThreads)

        return program

    def getCommand(self, **kwargs):
        """ Return the program and arguments to be run.
        The input keywords argument should contain key-values for
        one micrograph or group of micrographs.
        """
        params = dict(self._params)
        params.update(kwargs)
        return self._program, self._args % params

    def parseOutput(self, filename):
        """ Retrieve defocus U, V and angle from the
        output file of the program execution.
        """
        return convert.parseCtffind4Output(filename)

    def parseOutputAsCtf(self, filename, psdFile=None):
        """ Parse the output file and build the CTFModel object
        with the values.
        """
        ctf = pwem.CTFModel()
        convert.readCtfModel(ctf, filename, ctf4=True)
        if psdFile:
            ctf.setPsdFile(psdFile)

        return ctf

    def _getArgs(self, protocol):
        # Update first the _params dict
        params = protocol.getCtfParamsDict()
        # Convert digital frequencies to spatial frequencies
        sampling = params['samplingRate']
        params['lowRes'] = sampling / params['lowRes']
        if params['lowRes'] > 50:
            params['lowRes'] = 50
        params['highRes'] = sampling / params['highRes']
        params['step_focus'] = 500.0

        params['astigmatism'] = protocol.astigmatism.get()
        if self._findPhaseShift:
            params['phaseShift'] = "yes"
            params['minPhaseShift'] = protocol.minPhaseShift.get()
            params['maxPhaseShift'] = protocol.maxPhaseShift.get()
            params['stepPhaseShift'] = protocol.stepPhaseShift.get()
        else:
            params['phaseShift'] = "no"
        # ctffind >= v4.1.5
        params['resamplePix'] = "yes" if protocol.resamplePix else "no"
        params['slowSearch'] = "yes" if protocol.slowSearch else "no"

        downFactor = protocol.ctfDownFactor.get()
        if downFactor != 1:
            params['scannedPixelSize'] *= downFactor

        args = """   << eof > %(ctffindOut)s
%(micFn)s
%(ctffindPSD)s"""
        args += self._getExtraArgs()
        return args, params

    def _getExtraArgs(self):
        args = """
%(samplingRate)f
%(voltage)f
%(sphericalAberration)f
%(ampContrast)f
%(windowSize)d
%(lowRes)f
%(highRes)f
%(minDefocus)f
%(maxDefocus)f
%(step_focus)f"""
        v = self.getVersion()
        if v in ['4.1.5', '4.1.8', V4_1_10]:
            if self._findPhaseShift:
                args += """
no
%(slowSearch)s
yes
%(astigmatism)f
%(phaseShift)s
%(minPhaseShift)f
%(maxPhaseShift)f
%(stepPhaseShift)f
yes
%(resamplePix)s
eof
"""
            else:
                args += """
no
%(slowSearch)s
yes
%(astigmatism)f
%(phaseShift)s
yes
%(resamplePix)s
eof
"""
        elif v == V4_0_15:
            if self._findPhaseShift:
                args += """
%(astigmatism)f
%(phaseShift)s
%(minPhaseShift)f
%(maxPhaseShift)f
%(stepPhaseShift)f
eof
"""
            else:
                args += """
%(astigmatism)f
%(phaseShift)s
eof
"""

        return args

