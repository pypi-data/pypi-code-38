from wofrysrw.beamline.optical_elements.mirrors.srw_mirror import SRWMirror, Orientation, SimulationMethod, TreatInputOutput
from syned.beamline.shape import Ellipsoid

from oasys_srw.srwlib import SRWLOptMirEl

class SRWEllipticalMirror(SRWMirror):
    def __init__(self,
                 name                                       = "Undefined",
                 optical_element_displacement       = None,
                 tangential_size                            = 1.2,
                 sagittal_size                              = 0.01,
                 grazing_angle                              = 0.003,
                 orientation_of_reflection_plane            = Orientation.UP,
                 invert_tangent_component                   = False,
                 distance_from_first_focus_to_mirror_center =1,
                 distance_from_mirror_center_to_second_focus=1,
                 height_profile_data_file                   = "mirror.dat",
                 height_profile_data_file_dimension         = 1,
                 height_amplification_coefficient           = 1.0):

        super().__init__(name=name,
                         optical_element_displacement=optical_element_displacement,
                         tangential_size=tangential_size,
                         sagittal_size=sagittal_size,
                         grazing_angle=grazing_angle,
                         orientation_of_reflection_plane=orientation_of_reflection_plane,
                         invert_tangent_component=invert_tangent_component,
                         height_profile_data_file=height_profile_data_file,
                         height_profile_data_file_dimension=height_profile_data_file_dimension,
                         height_amplification_coefficient=height_amplification_coefficient)

        self.distance_from_first_focus_to_mirror_center  = distance_from_first_focus_to_mirror_center
        self.distance_from_mirror_center_to_second_focus = distance_from_mirror_center_to_second_focus

    def get_shape(self):
        return Ellipsoid()

    def get_SRWLOptMir(self, nvx, nvy, nvz, tvx, tvy, x, y, ap_shape):
        return SRWLOptMirEl(_size_tang=self.tangential_size,
                            _size_sag=self.sagittal_size,
                            _p=self.distance_from_first_focus_to_mirror_center,
                            _q=self.distance_from_mirror_center_to_second_focus,
                            _ang_graz=self.grazing_angle,
                            _ap_shape=ap_shape,
                            _sim_meth=SimulationMethod.THICK,
                            _treat_in_out=TreatInputOutput.WAVEFRONT_INPUT_CENTER_OUTPUT_CENTER,
                            _nvx=nvx,
                            _nvy=nvy,
                            _nvz=nvz,
                            _tvx=tvx,
                            _tvy=tvy,
                            _x=x,
                            _y=y)

    def fromSRWLOpt(self, srwlopt=SRWLOptMirEl()):
        if not isinstance(srwlopt, SRWLOptMirEl):
            raise ValueError("SRW object is not a SRWLOptMirEl object")

        super().fromSRWLOpt(srwlopt)

        self.distance_from_first_focus_to_mirror_center = srwlopt.p
        self.distance_from_mirror_center_to_second_focus = srwlopt.q

    def to_python_code_aux(self, nvx, nvy, nvz, tvx, tvy, x, y, ap_shape):
        text_code  = "SRWLOptMirEl(_size_tang=" + str(self.tangential_size) +"," + "\n"
        text_code += "                     _size_sag=" + str(self.sagittal_size) +"," + "\n"
        text_code += "                     _p=" + str(self.distance_from_first_focus_to_mirror_center) +"," + "\n"
        text_code += "                     _q=" + str(self.distance_from_mirror_center_to_second_focus) +"," + "\n"
        text_code += "                     _ang_graz=" + str(self.grazing_angle) +"," + "\n"
        text_code += "                     _ap_shape='" + str(ap_shape) +"'," + "\n"
        text_code += "                     _sim_meth=" + str(SimulationMethod.THICK) +"," + "\n"
        text_code += "                     _treat_in_out=" + str(TreatInputOutput.WAVEFRONT_INPUT_CENTER_OUTPUT_CENTER) +"," + "\n"
        text_code += "                     _nvx=" + str(nvx) +"," + "\n"
        text_code += "                     _nvy=" + str(nvy) +"," + "\n"
        text_code += "                     _nvz=" + str(nvz) +"," + "\n"
        text_code += "                     _tvx=" + str(tvx) +"," + "\n"
        text_code += "                     _tvy=" + str(tvy) +"," + "\n"
        text_code += "                     _x=" + str(x) +"," + "\n"
        text_code += "                     _y=" + str(y) +")" + "\n"

        return text_code
