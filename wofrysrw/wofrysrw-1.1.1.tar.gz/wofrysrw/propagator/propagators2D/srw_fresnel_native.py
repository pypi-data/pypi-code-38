import scipy.constants as codata
angstroms_to_eV = codata.h*codata.c/codata.e*1e10

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofry.propagator.propagator import PropagationManager, PropagationParameters, Propagator2D

from wofrysrw.beamline.srw_beamline import Where
from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontPropagationParameters, WavefrontPropagationOptionalParameters
from wofrysrw.propagator.wavefront2D.srw_wavefront import SRWWavefront
from wofrysrw.propagator.propagators2D.srw_propagation_mode import SRWPropagationMode

from oasys_srw.srwlib import *

SRW_APPLICATION = "SRW"

class FresnelSRWNative(Propagator2D):

    HANDLER_NAME = "FRESNEL_SRW_NATIVE"

    def get_handler_name(self):
        return self.HANDLER_NAME

    """
    2D Fresnel propagator using convolution via Fourier transform
    :param wavefront:
    :param propagation_distance:
    :param srw_autosetting:set to 1 for automatic SRW redimensionate wavefront
    :return:
    """

    def do_propagation(self, parameters=PropagationParameters()):
        wavefront = parameters.get_wavefront()

        is_generic_wavefront = isinstance(wavefront, GenericWavefront2D)

        if is_generic_wavefront:
            wavefront = SRWWavefront.fromGenericWavefront(wavefront)
        else:
            if not isinstance(wavefront, SRWWavefront): raise ValueError("wavefront cannot be managed by this propagator")

        srw_oe_array = []
        srw_pp_array = []

        propagation_mode = PropagationManager.Instance().get_propagation_mode(SRW_APPLICATION)

        if propagation_mode == SRWPropagationMode.STEP_BY_STEP:
            self.add_optical_element(parameters, 0, srw_oe_array, srw_pp_array, wavefront)
        elif propagation_mode == SRWPropagationMode.WHOLE_BEAMLINE:
            srw_beamline = parameters.get_additional_parameter("working_beamline")

            for index in range(srw_beamline.get_beamline_elements_number()):
                self.add_optical_element_from_beamline(srw_beamline, index, srw_oe_array, srw_pp_array, wavefront)
        else:
            raise ValueError("Propagation Mode not supported by this Propagator")

        if len(srw_oe_array) > 0:
            optBL = SRWLOptC(srw_oe_array, srw_pp_array)
            srwl.PropagElecField(wavefront, optBL)

        if is_generic_wavefront:
            return wavefront.toGenericWavefront()
        else:
            return wavefront

    ########################################################
    # WHOLE BEAMLINE

    def add_optical_element_from_beamline(self, srw_beamline, index, srw_oe_array, srw_pp_array, wavefront):
        optical_element = srw_beamline.get_beamline_element_at(index).get_optical_element()
        coordinates = srw_beamline.get_beamline_element_at(index).get_coordinates()

        if coordinates.p() != 0.0:
            srw_oe_array.append(SRWLOptD(coordinates.p()))
            srw_pp_array.append(self.__get_drift_wavefront_propagation_parameters_from_beamline(srw_beamline, index, Where.DRIFT_BEFORE))

        optical_element.add_to_srw_native_array(srw_oe_array, srw_pp_array, srw_beamline.get_wavefront_propagation_parameters_at(index, Where.OE), wavefront)

        if coordinates.q() != 0.0:
            srw_oe_array.append(SRWLOptD(coordinates.q()))
            srw_pp_array.append(self.__get_drift_wavefront_propagation_parameters_from_beamline(srw_beamline, index, Where.DRIFT_AFTER))

    ########################################################
    # ELEMENT BY ELEMENT

    def __get_drift_wavefront_propagation_parameters_from_beamline(self, srw_beamline, index, where=Where.DRIFT_BEFORE):
        wavefront_propagation_parameters, wavefront_propagation_optional_parameters = srw_beamline.get_wavefront_propagation_parameters_at(index, where)

        srw_parameters_array = wavefront_propagation_parameters.to_SRW_array()
        if not wavefront_propagation_optional_parameters is None: wavefront_propagation_optional_parameters.append_to_srw_array(srw_parameters_array)

        return srw_parameters_array

    def __get_drift_wavefront_propagation_parameters(self, parameters, where=Where.DRIFT_BEFORE):
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

    def add_optical_element(self, parameters, index, srw_oe_array, srw_pp_array, wavefront):
        optical_element = parameters.get_PropagationElements().get_propagation_element(index).get_optical_element()
        coordinates = parameters.get_PropagationElements().get_propagation_element(index).get_coordinates()

        if coordinates.p() != 0.0:
            srw_oe_array.append(SRWLOptD(coordinates.p()))
            srw_pp_array.append(self.__get_drift_wavefront_propagation_parameters(parameters, Where.DRIFT_BEFORE))

        optical_element.add_to_srw_native_array(srw_oe_array, srw_pp_array, parameters, wavefront)

        if coordinates.q() != 0.0:
            srw_oe_array.append(SRWLOptD(coordinates.q()))
            srw_pp_array.append(self.__get_drift_wavefront_propagation_parameters(parameters, Where.DRIFT_AFTER))
