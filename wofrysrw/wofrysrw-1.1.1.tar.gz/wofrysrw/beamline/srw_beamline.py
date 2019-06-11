
from syned.beamline.beamline import Beamline

from wofrysrw.srw_object import SRWObject
from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElementDisplacement
from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontPropagationParameters, WavefrontPropagationOptionalParameters

from oasys_srw.srwlib import *

class Where:
    DRIFT_BEFORE = "before"
    DRIFT_AFTER = "after"
    OE = "oe"

    @classmethod
    def tuple(cls):
        return cls.DRIFT_BEFORE, cls.OE, cls.DRIFT_AFTER

class SRWBeamline(Beamline, SRWObject):

    def __init__(self,
                 light_source=SRWLightSource(),
                 beamline_elements_list=[]):
        super().__init__(light_source=light_source, beamline_elements_list=beamline_elements_list)

        self._wavefront_propagation_parameters_list = {}
        self._wavefront_propagation_parameters_list[Where.DRIFT_BEFORE] = []
        self._wavefront_propagation_parameters_list[Where.OE]           = []
        self._wavefront_propagation_parameters_list[Where.DRIFT_AFTER]  = []

    # overwrites the SynedObject method for dealing with list
    def to_dictionary(self): # TODO: to be adjusted....
        dict_to_save = super().to_dictionary()
        dict_to_save["srw_wavefront_propagation_parameters"] = [ el[0].to_dictionary() for el in self._wavefront_propagation_parameters_list[Where.OE]]

        return dict_to_save

    def append_wavefront_propagation_parameters(self, wavefront_propagation_parameters=WavefrontPropagationParameters(), wavefront_propagation_optional_parameters=WavefrontPropagationOptionalParameters(), where=Where.OE):
        self._wavefront_propagation_parameters_list[where].append([wavefront_propagation_parameters, wavefront_propagation_optional_parameters])

    def get_wavefront_propagation_parameters(self, where=Where.OE):
        return self._wavefront_propagation_parameters_list[where]

    def get_wavefront_propagation_parameters_at(self, index, where=Where.OE):
        if index >= len(self._wavefront_propagation_parameters_list[where]):
            raise IndexError("Index " + str(index) + " out of bounds")

        return self._wavefront_propagation_parameters_list[where][index]

    def duplicate(self):
        beamline_elements_list = []
        for beamline_element in self._beamline_elements_list:
            beamline_elements_list.append(beamline_element)

        new_beamline = SRWBeamline(light_source=self._light_source, beamline_elements_list = beamline_elements_list)

        for where in Where.tuple():
            for element in self.get_wavefront_propagation_parameters(where):
                new_beamline.append_wavefront_propagation_parameters(element[0], element[1], where)

        return new_beamline

    def to_python_code(self, data=None):
        wavefront = data[0]
        is_multi_electron = data[1] == True

        text_code  = "from oasys_srw.srwlib import *\nfrom oasys_srw.uti_plot import *\nimport numpy\n\n"

        if is_multi_electron: text_code += "#if not srwl_uti_proc_is_master(): exit()\n"
        else: text_code += "if not srwl_uti_proc_is_master(): exit()\n"

        text_code += "\n####################################################\n# LIGHT SOURCE\n\n"
        text_code += self.get_light_source().to_python_code(is_multi_electron)

        if not is_multi_electron:
            text_code += "\n"
            text_code += "mesh0 = deepcopy(wfr.mesh)" + "\n"
            text_code += "arI = array('f', [0]*mesh0.nx*mesh0.ny)" + "\n"
            text_code += "srwl.CalcIntFromElecField(arI, wfr, 6, 0, 3, mesh0.eStart, 0, 0)" + "\n"
            text_code += "arIx = array('f', [0]*mesh0.nx)" + "\n"
            text_code += "srwl.CalcIntFromElecField(arIx, wfr, 6, 0, 1, mesh0.eStart, 0, 0)" + "\n"
            text_code += "arIy = array('f', [0]*mesh0.ny)" + "\n"
            text_code += "srwl.CalcIntFromElecField(arIy, wfr, 6, 0, 2, mesh0.eStart, 0, 0)" + "\n"
            text_code += "#save ascii file with intensity" + "\n"
            text_code += "#srwl_uti_save_intens_ascii(arI, mesh0, <file_path>)" + "\n"
            text_code += "plotMesh0x = [1000*mesh0.xStart, 1000*mesh0.xFin, mesh0.nx]" + "\n"
            text_code += "plotMesh0y = [1000*mesh0.yStart, 1000*mesh0.yFin, mesh0.ny]" + "\n"
            text_code += "uti_plot2d1d (arI, plotMesh0x, plotMesh0y, labels=['Horizontal Position [mm]', 'Vertical Position [mm]', 'Intensity Before Propagation'])" + "\n"

        if self.get_beamline_elements_number() > 0:
            text_code += "\n####################################################\n# BEAMLINE\n\n"
            text_code += "srw_oe_array = []" + "\n"
            text_code += "srw_pp_array = []" + "\n"
            text_code += "\n"

            for index in range(self.get_beamline_elements_number()):
                oe_name = "oe_" + str(index)
                data_oe = [oe_name, wavefront]

                beamline_element = self.get_beamline_element_at(index)

                optical_element = beamline_element.get_optical_element()
                coordinates = beamline_element.get_coordinates()

                # DRIFT BEFORE ----------------

                if coordinates.p() != 0.0:
                    text_code += "drift_before_" + oe_name + " = " + "SRWLOptD(" + str(coordinates.p()) + ")" + "\n"

                    wp, wop = self.get_wavefront_propagation_parameters_at(index, Where.DRIFT_BEFORE)
                    drift_pp_array = wp.to_python_code()
                    if not wop is None: drift_pp_array = wop.append_to_python_code(drift_pp_array)

                    text_code += "pp_drift_before_" + oe_name + " = " + drift_pp_array  + "\n"
                    text_code += "\n"
                    text_code += "srw_oe_array.append(drift_before_" + oe_name + ")" + "\n"
                    text_code += "srw_pp_array.append(pp_drift_before_" + oe_name + ")" + "\n"
                    text_code += "\n"

                wp, wop = self.get_wavefront_propagation_parameters_at(index, Where.OE)

                # OPTICAL ELEMENT ----------------

                if not wp is None: # SCREEN!!!
                    text_code += optical_element.to_python_code(data_oe)

                    oe_pp_array = wp.to_python_code()
                    if not wop is None: oe_pp_array = wop.append_to_python_code(oe_pp_array)

                    text_code += "\n"

                    if not optical_element.displacement is None:
                        data_oe.append(SRWOpticalElementDisplacement.BEFORE)

                        text_code += optical_element.displacement.to_python_code(data_oe)

                        text_code += "\n"

                        if optical_element.displacement.has_shift:
                            text_code += "srw_oe_array.append(shift_before_" + oe_name + ")" + "\n"
                            text_code += "srw_pp_array.append(pp_shift_before_" + oe_name + ")" + "\n"
                            text_code += "\n"

                        if optical_element.displacement.has_rotation:
                            text_code += "srw_oe_array.append(rotation_before_" + oe_name + ")" + "\n"
                            text_code += "srw_pp_array.append(pp_rotation_before_" + oe_name + ")" + "\n"
                            text_code += "\n"

                    if hasattr(optical_element, "add_acceptance_slit") and getattr(optical_element, "add_acceptance_slit") == True: # MIRROR AND GRATINGS

                        text_code += "pp_acceptance_slits_" + oe_name + " = " + oe_pp_array  + "\n"
                        text_code += "pp_" + oe_name + " = " + WavefrontPropagationParameters().to_python_code()  + "\n"
                        text_code += "\n"

                        text_code += "srw_oe_array.append(acceptance_slits_" + oe_name + ")" + "\n"
                        text_code += "srw_pp_array.append(pp_acceptance_slits_" + oe_name + ")" + "\n"

                    else:
                        text_code += "pp_" + oe_name + " = " + oe_pp_array  + "\n"

                    text_code += "\n"
                    text_code += "srw_oe_array.append(" + oe_name + ")" + "\n"
                    text_code += "srw_pp_array.append(pp_" + oe_name + ")" + "\n"

                    if hasattr(optical_element, "height_profile_data_file"): # MIRROR AND GRATINGS
                        if not getattr(optical_element, "height_profile_data_file") is None:
                            text_code += "\n"
                            text_code += "srw_oe_array.append(optTrEr_" + oe_name + ")" + "\n"
                            text_code += "srw_pp_array.append(" + WavefrontPropagationParameters().to_python_code() + ")" + "\n"

                    if not optical_element.displacement is None:
                        data_oe[2] = SRWOpticalElementDisplacement.AFTER

                        text_code += "\n"

                        text_code += optical_element.displacement.to_python_code(data_oe)

                        text_code += "\n"

                        if optical_element.displacement.has_shift:
                            text_code += "srw_oe_array.append(shift_after_" + oe_name + ")" + "\n"
                            text_code += "srw_pp_array.append(pp_shift_after_" + oe_name + ")" + "\n"
                            text_code += "\n"

                        if optical_element.displacement.has_rotation:
                            text_code += "srw_oe_array.append(rotation_after_" + oe_name + ")" + "\n"
                            text_code += "srw_pp_array.append(pp_rotation_after_" + oe_name + ")" + "\n"
                            text_code += "\n"


                # DRIFT AFTER ----------------

                if coordinates.q() != 0.0:
                    text_code += "\n"
                    text_code += "drift_after_" + oe_name + " = " + "SRWLOptD(" + str(coordinates.q()) + ")" + "\n"

                    wp, wop = self.get_wavefront_propagation_parameters_at(index, Where.DRIFT_AFTER)
                    drift_pp_array = wp.to_python_code()
                    if not wop is None: drift_pp_array = wop.append_to_python_code(drift_pp_array)

                    text_code += "pp_drift_after_" + oe_name + " = " + drift_pp_array  + "\n"
                    text_code += "\n"
                    text_code += "srw_oe_array.append(drift_after_" + oe_name + ")" + "\n"
                    text_code += "srw_pp_array.append(pp_drift_after_" + oe_name + ")" + "\n"

                text_code += "\n"

            text_code += "\n####################################################\n# PROPAGATION\n\n"
            text_code += "optBL = SRWLOptC(srw_oe_array, srw_pp_array)" + "\n"
            if not is_multi_electron: text_code += "srwl.PropagElecField(wfr, optBL)" + "\n"
            text_code += "\n"

            if not is_multi_electron:
                text_code += "mesh1 = deepcopy(wfr.mesh)" + "\n"
                text_code += "arI1 = array('f', [0]*mesh1.nx*mesh1.ny)" + "\n"
                text_code += "srwl.CalcIntFromElecField(arI1, wfr, 6, 0, 3, mesh1.eStart, 0, 0)" + "\n"
                text_code += "arI1x = array('f', [0]*mesh1.nx)" + "\n"
                text_code += "srwl.CalcIntFromElecField(arI1x, wfr, 6, 0, 1, mesh1.eStart, 0, 0)" + "\n"
                text_code += "arI1y = array('f', [0]*mesh1.ny)" + "\n"
                text_code += "srwl.CalcIntFromElecField(arI1y, wfr, 6, 0, 2, mesh1.eStart, 0, 0)" + "\n"
                text_code += "#save ascii file with intensity" + "\n"
                text_code += "#srwl_uti_save_intens_ascii(arI1, mesh1, <file_path>)" + "\n"
                text_code += "plotMesh1x = [1000*mesh1.xStart, 1000*mesh1.xFin, mesh1.nx]" + "\n"
                text_code += "plotMesh1y = [1000*mesh1.yStart, 1000*mesh1.yFin, mesh1.ny]" + "\n"
                text_code += "uti_plot2d1d(arI1, plotMesh1x, plotMesh1y, labels=['Horizontal Position [mm]', 'Vertical Position [mm]', 'Intensity After Propagation'])" + "\n"

        if not is_multi_electron: text_code += "uti_plot_show()" + "\n"

        if is_multi_electron:
            parameters = data[2]

            sampFactNxNyForProp  = parameters[0]
            nMacroElec           = parameters[1]
            nMacroElecAvgOneProc = parameters[2]
            nMacroElecSavePer    = parameters[3]
            srCalcMeth           = parameters[4]
            srCalcPrec           = parameters[5]
            strIntPropME_OutFileName = parameters[6]
            _char = parameters[7]

            text_code += "\n\n####################################################\n# MULTI ELECTRON PROPAGATION\n\n"

            text_code += "radStokesProp = srwl_wfr_emit_prop_multi_e(part_beam," + "\n"
            text_code += "                                           magnetic_field_container," + "\n"
            text_code += "                                           initial_mesh," + "\n"
            text_code += "                                           " + str(srCalcMeth) + "," + "\n"
            text_code += "                                           " + str(srCalcPrec) + "," + "\n"
            text_code += "                                           " + str(nMacroElec) + "," + "\n"
            text_code += "                                           " + str(nMacroElecAvgOneProc) + "," + "\n"
            text_code += "                                           " + str(nMacroElecSavePer) + "," + "\n"
            text_code += "                                           '" + str(strIntPropME_OutFileName) + "'," + "\n"
            text_code += "                                           " + str(sampFactNxNyForProp) + "," + "\n"
            text_code += "                                           optBL," + "\n"
            text_code += "                                           _char=" + str(int(_char)) + ")" + "\n"

        return text_code

