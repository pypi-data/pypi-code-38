from oasys_srw.srwlib import SRWLMagFldH, SRWLMagFldU

from syned.storage_ring.magnetic_structures.undulator import Undulator
from wofrysrw.storage_ring.srw_magnetic_structure import SRWMagneticStructure

class SRWUndulator(Undulator, SRWMagneticStructure):

    def __init__(self,
                 horizontal_central_position = 0.0,
                 vertical_central_position = 0.0,
                 longitudinal_central_position = 0.0,
                 K_vertical = 0.0,
                 K_horizontal = 0.0,
                 period_length = 0.0,
                 number_of_periods = 1,
                 initial_phase_vertical = 0.0, # initial phase [rad]
                 initial_phase_horizontal = 0.0, # initial phase [rad]
                 symmetry_vs_longitudinal_position_vertical = -1, # symmetry vs longitudinal position 1 - symmetric (B ~ cos(2*Pi*n*z/per + ph)) , -1 - anti-symmetric (B ~ sin(2*Pi*n*z/per + ph))
                 symmetry_vs_longitudinal_position_horizontal = 1, # symmetry vs longitudinal position 1 - symmetric (B ~ cos(2*Pi*n*z/per + ph)) , -1 - anti-symmetric (B ~ sin(2*Pi*n*z/per + ph))
                 coefficient_for_transverse_dependence_vertical = 1.0, # coefficient for transverse depenednce B*cosh(2*Pi*n*a*y/per)*cos(2*Pi*n*z/per + ph)
                 coefficient_for_transverse_dependence_horizontal = 1.0 # coefficient for transverse depenednce B*cosh(2*Pi*n*a*y/per)*cos(2*Pi*n*z/per + ph)
                ):
        Undulator.__init__(self, K_vertical, K_horizontal, period_length, number_of_periods)
        SRWMagneticStructure.__init__(self, horizontal_central_position, vertical_central_position, longitudinal_central_position)

        self.initial_phase_vertical = initial_phase_vertical
        self.initial_phase_horizontal = initial_phase_horizontal
        self.symmetry_vs_longitudinal_position_vertical = symmetry_vs_longitudinal_position_vertical
        self.symmetry_vs_longitudinal_position_horizontal = symmetry_vs_longitudinal_position_horizontal
        self.coefficient_for_transverse_dependence_vertical = coefficient_for_transverse_dependence_vertical
        self.coefficient_for_transverse_dependence_horizontal = coefficient_for_transverse_dependence_horizontal

    def get_SRWMagneticStructure(self):
        magnetic_fields = []

        if self._K_vertical > 0.0:
            magnetic_fields.append(SRWLMagFldH(1,
                                               'v',
                                               _B=self.magnetic_field_vertical(),
                                               _ph=self.initial_phase_vertical,
                                               _s=self.symmetry_vs_longitudinal_position_vertical,
                                               _a=self.coefficient_for_transverse_dependence_vertical))

        if self._K_horizontal > 0.0:
            magnetic_fields.append(SRWLMagFldH(1,
                                               'h',
                                               _B=self.magnetic_field_horizontal(),
                                               _ph=self.initial_phase_horizontal,
                                               _s=self.symmetry_vs_longitudinal_position_horizontal,
                                               _a=self.coefficient_for_transverse_dependence_horizontal))

        return SRWLMagFldU(_arHarm=magnetic_fields,
                           _per=self._period_length,
                           _nPer=self._number_of_periods)

    def to_python_code_aux(self):
        text_code = "magnetic_fields = []" + "\n"

        if self._K_vertical > 0.0:
            text_code += "magnetic_fields.append(SRWLMagFldH(1, 'v', " + "\n"
            text_code += "                                   _B=" + str(self.magnetic_field_vertical()) + ", " + "\n"
            text_code += "                                   _ph=" + str(self.initial_phase_vertical) + ", " + "\n"
            text_code += "                                   _s=" + str(self.symmetry_vs_longitudinal_position_vertical) + ", " + "\n"
            text_code += "                                   _a=" + str(self.coefficient_for_transverse_dependence_vertical) + "))" + "\n"

        if self._K_horizontal > 0.0:
            text_code += "magnetic_fields.append(SRWLMagFldH(1, 'h', " + "\n"
            text_code += "                                   _B=" + str(self.magnetic_field_horizontal()) + ", " + "\n"
            text_code += "                                   _ph=" + str(self.initial_phase_horizontal) + ", " + "\n"
            text_code += "                                   _s=" + str(self.symmetry_vs_longitudinal_position_horizontal) + ", " + "\n"
            text_code += "                                   _a=" + str(self.coefficient_for_transverse_dependence_horizontal) + "))" + "\n"

        text_code += "magnetic_structure = SRWLMagFldU(_arHarm=magnetic_fields, _per=" + str(self._period_length) + ", _nPer=" + str(self._number_of_periods) + ")" + "\n"

        return text_code
