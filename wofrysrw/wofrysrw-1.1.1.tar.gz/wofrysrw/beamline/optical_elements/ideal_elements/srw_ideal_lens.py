from syned.beamline.optical_elements.ideal_elements.lens import IdealLens

from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElement

from oasys_srw.srwlib import SRWLOptL

class SRWIdealLens(IdealLens, SRWOpticalElement):
    def __init__(self,
                 name="Undefined",
                 optical_element_displacement=None,
                 focal_x=1.0,
                 focal_y=1.0,
                 x=0.0,
                 y=0.0):
        SRWOpticalElement.__init__(self, optical_element_displacement=optical_element_displacement)
        IdealLens.__init__(self, name=name, focal_x=focal_x, focal_y=focal_y)

        self.set_lens_position(x, y)

    def set_lens_position(self, x=0.0, y=0.0):
        self._x = x
        self._y = y

    def toSRWLOpt(self):
        return SRWLOptL(_Fx=self.focal_x(), _Fy=self.focal_y(), _x=self._x, _y=self._y)

    def fromSRWLOpt(self, srwlopt=SRWLOptL()):
        if not isinstance(srwlopt, SRWLOptL):
            raise ValueError("SRW object is not a SRWLOptL object")

        self.__init__(focal_x=srwlopt.Fx, focal_y=srwlopt.Fy, x=srwlopt.x, y=srwlopt.y)

    def to_python_code(self, data=None):
        return data[0] + "="+  "SRWLOptL(_Fx=" + str(self.focal_x()) + ", _Fy=" + str(self.focal_y()) + ", _x=" + str(self._x) + ", _y=" + str(self._y) + ")" + "\n"
