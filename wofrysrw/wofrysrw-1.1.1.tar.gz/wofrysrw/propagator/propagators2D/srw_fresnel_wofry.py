import scipy.constants as codata
angstroms_to_eV = codata.h*codata.c/codata.e*1e10

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofry.propagator.propagator import Propagator2D

from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontPropagationParameters, WavefrontPropagationOptionalParameters
from wofrysrw.propagator.wavefront2D.srw_wavefront import SRWWavefront

from oasys_srw.srwlib import *

class FresnelSRWWofry(Propagator2D):

    HANDLER_NAME = "FRESNEL_SRW_WOFRY"

    def get_handler_name(self):
        return self.HANDLER_NAME

    """
    2D Fresnel propagator using convolution via Fourier transform
    :param wavefront:
    :param propagation_distance:
    :param srw_autosetting:set to 1 for automatic SRW redimensionate wavefront
    :return:
    """


    def do_specific_progation_before(self, wavefront, propagation_distance, parameters, element_index=None):
        return self.do_specific_progation(wavefront, propagation_distance, parameters, prefix="before")

    def do_specific_progation_after(self, wavefront, propagation_distance, parameters, element_index=None):
        return self.do_specific_progation(wavefront, propagation_distance, parameters, prefix="after")

    def do_specific_progation(self, wavefront, propagation_distance, parameters, prefix="after"):
        is_generic_wavefront = isinstance(wavefront, GenericWavefront2D)

        if is_generic_wavefront:
            wavefront = SRWWavefront.fromGenericWavefront(wavefront)
        else:
            if not isinstance(wavefront, SRWWavefront): raise ValueError("wavefront cannot be managed by this propagator")

        #
        # propagation (simple wavefront drift
        #

        optBL = SRWLOptC([SRWLOptD(propagation_distance)], # drift space
                         [self.__get_drift_wavefront_propagation_parameters(parameters, prefix)])

        srwl.PropagElecField(wavefront, optBL)

        if is_generic_wavefront:
            return wavefront.toGenericWavefront()
        else:
            return wavefront

    def __get_drift_wavefront_propagation_parameters(self, parameters, where="before"):
        if not parameters.has_additional_parameter("srw_drift_" + where + "_wavefront_propagation_parameters"):
            wavefront_propagation_parameters = WavefrontPropagationParameters()
        else:
            wavefront_propagation_parameters = parameters.get_additional_parameter("srw_drift_" + where + "_wavefront_propagation_parameters")

            if not isinstance(wavefront_propagation_parameters, WavefrontPropagationParameters):
                raise ValueError("SRW Wavefront Propagation Parameters not present")

        srw_parameters_array = wavefront_propagation_parameters.to_SRW_array()

        if parameters.has_additional_parameter("srw_drift_" + where + "_wavefront_propagation_optional_parameters"):
            wavefront_propagation_optional_parameters = parameters.get_additional_parameter("srw_drift_" + where + "_wavefront_propagation_optional_parameters")

            if not isinstance(wavefront_propagation_optional_parameters, WavefrontPropagationOptionalParameters):
                raise ValueError("SRW Wavefront Propagation Optional Parameters are inconsistent")

            wavefront_propagation_optional_parameters.append_to_srw_array(srw_parameters_array)

        return srw_parameters_array
