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

import os
import sys

import pyworkflow as pw
import grigoriefflab.convert as convert
from grigoriefflab.constants import *
from .program_ctffind import ProgramCtffind
from grigoriefflab import Plugin


class ProtCTFFind(pw.em.ProtCTFMicrographs):
    """
    Estimates CTF on a set of micrographs
    using either ctffind3 or ctffind4 program.
    
    To find more information about ctffind4 go to:
    http://grigoriefflab.janelia.org/ctffind4
    """
    _label = 'ctffind4'

    @classmethod
    def validateInstallation(cls):
        """ Check if the installation of this protocol is correct.
        Can't rely on package function since this is a "multi package" package
        Returning an empty list means that the installation is correct
        and there are not errors. If some errors are found, a list with
        the error messages will be returned.
        """
        missingPaths = []

        # FIXME
        if (not os.path.exists(Plugin.getHome(CTFFIND4)) and
                not os.path.exists(Plugin.getHome(CTFFIND))):
            missingPaths.append("%s, %s : ctffind installation not found"
                                % (CTFFIND4_HOME, CTFFIND_HOME))
        return missingPaths

    def _defineParams(self, form):
        pw.em.ProtCTFMicrographs._defineParams(self, form)
        self._defineStreamingParams(form)

    def _defineProcessParams(self, form):
        ProgramCtffind.defineFormParams(form)

    def _defineCtfParamsDict(self):
        pw.em.ProtCTFMicrographs._defineCtfParamsDict(self)
        self._ctfProgram = ProgramCtffind(self)

    # -------------------------- STEPS functions ------------------------------
    def _doCtfEstimation(self, mic, **kwargs):
        """ Run ctffind, 3 or 4, with required parameters """
        try:
            micFn = mic.getFileName()
            micDir = self._getTmpPath('mic_%04d' % mic.getObjId())
            # Create micrograph dir
            pw.utils.makePath(micDir)
            downFactor = self.ctfDownFactor.get()
            micFnMrc = os.path.join(micDir, pw.utils.replaceBaseExt(micFn, 'mrc'))

            ih = pw.em.ImageHandler()

            if not ih.existsLocation(micFn):
                raise Exception("Missing input micrograph %s" % micFn)

            if downFactor != 1:
                # Replace extension by 'mrc' because there are some formats
                # that cannot be written (such as dm3)
                ih.scaleFourier(micFn, micFnMrc, downFactor)
            else:
                ih.convert(micFn, micFnMrc, pw.em.DT_FLOAT)

        except Exception as ex:
            print >> sys.stderr, "Some error happened: %s" % ex
            import traceback
            traceback.print_exc()
        try:
            program, args = self._ctfProgram.getCommand(
                micFn=micFnMrc,
                ctffindOut=self._getCtfOutPath(mic),
                ctffindPSD=self._getPsdPath(mic),
                **kwargs
            )
            self.runJob(program, args)
        except Exception as ex:
            print >> sys.stderr, "ctffind has failed with micrograph %s" % micFnMrc

    def _estimateCTF(self, mic, *args):
        self._doCtfEstimation(mic)

    def _reEstimateCTF(self, mic, ctf):
        """ Run ctffind3 with required parameters """
        self._doCtfEstimation(mic, **self._getRecalCtfParamsDict(ctf))

    def _createCtfModel(self, mic, updateSampling=True):
        #  When downsample option is used, we need to update the
        # sampling rate of the micrograph associated with the CTF
        # since it could be downsampled
        if updateSampling:
            newSampling = mic.getSamplingRate() * self.ctfDownFactor.get()
            mic.setSamplingRate(newSampling)

        psd = self._getPsdPath(mic)
        ctfModel = self._ctfProgram.parseOutputAsCtf(self._getCtfOutPath(mic),
                                                     psdFile=psd)
        ctfModel.setMicrograph(mic)

        return ctfModel

    def _createOutputStep(self):
        pass

    # -------------------------- INFO functions -------------------------------
    def _validate(self):
        errors = []

        valueStep = round(self.stepPhaseShift.get(), 2)
        valueMin = round(self.minPhaseShift.get(), 2)
        valueMax = round(self.maxPhaseShift.get(), 2)

        if not (self.minPhaseShift < self.maxPhaseShift and
                valueStep <= (valueMax-valueMin) and
                0.10 <= valueMax <= 3.15):
            errors.append('Wrong values for phase shift search.')

        return errors

    def _citations(self):
        return ['Rohou2015'] if self.useCtffind4 else ['Mindell2003']

    def _methods(self):
        if self.inputMicrographs.get() is None:
            return ['Input micrographs not available yet.']
        methods = ("We calculated the CTF of %s using CTFFind. "
                   % self.getObjectTag('inputMicrographs'))
        methods += self.methodsVar.get('')
        methods += 'Output CTFs: %s' % self.getObjectTag('outputCTF')

        return [methods]

    # -------------------------- UTILS functions ------------------------------
    def isNewCtffind4(self):
        # This function is needed because it is used in Form params condition
        return ProgramCtffind.isNewCtffind4()

    def _getRecalCtfParamsDict(self, ctfModel):
        values = map(float, ctfModel.getObjComment().split())
        sampling = ctfModel.getMicrograph().getSamplingRate()
        return {
            'step_focus': 500.0,
            'lowRes': sampling / values[3],
            'highRes': sampling / values[4],
            'minDefocus': min([values[0], values[1]]),
            'maxDefocus': max([values[0], values[1]])
        }

    def _getMicExtra(self, mic, suffix):
        """ Return a file in extra direction with root of micFn. """
        return self._getExtraPath(pw.utils.removeBaseExt(os.path.basename(
            mic.getFileName())) + '_' + suffix)

    def _getPsdPath(self, mic):
        return self._getMicExtra(mic, 'ctfEstimation.mrc')

    def _getCtfOutPath(self, mic):
        return self._getMicExtra(mic, 'ctfEstimation.txt')

    def _parseOutput(self, filename):
        """ Try to find the output estimation parameters
        from filename. It search for a line containing: Final Values.
        """
        return self._ctfProgram.parseOutput(filename)

    def _getCTFModel(self, defocusU, defocusV, defocusAngle, psdFile):
        ctf = pw.em.CTFModel()
        ctf.setStandardDefocus(defocusU, defocusV, defocusAngle)
        ctf.setPsdFile(psdFile)

        return ctf

    def _summary(self):
        summary = pw.em.ProtCTFMicrographs._summary(self)
        if self.useCtffind4 and ProgramCtffind.getVersion() == '4.1.5':
            summary.append("NOTE: ctffind4.1.5 finishes correctly (all output "
                           "is generated properly), but returns an error code. "
                           "Disregard error messages until this is fixed."
                           "http://grigoriefflab.janelia.org/node/5421")
        return summary

