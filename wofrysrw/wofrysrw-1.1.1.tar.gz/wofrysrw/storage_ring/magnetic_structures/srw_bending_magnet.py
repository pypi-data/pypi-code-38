from oasys_srw.srwlib import SRWLMagFldM

from syned.storage_ring.magnetic_structures.bending_magnet import BendingMagnet
from wofrysrw.storage_ring.srw_magnetic_structure import SRWMagneticStructure

class SRWBendingMagnet(BendingMagnet, SRWMagneticStructure):

    def __init__(self,
                 radius = 0.0,
                 magnetic_field = 0.0,
                 length = 0.0):
        BendingMagnet.__init__(self, radius, magnetic_field, length)

    def get_SRWMagneticStructure(self):
        return SRWLMagFldM(_G=self._magnetic_field, _m=1, _n_or_s='n', _Leff=self._length)

    def to_python_code_aux(self):
        text_code = "magnetic_structure = SRWLMagFldM(_G=" + str(self._magnetic_field) + ", _m=1, _n_or_s='n', _Leff=" + str(self._length) + ")" + "\n"

        return text_code

