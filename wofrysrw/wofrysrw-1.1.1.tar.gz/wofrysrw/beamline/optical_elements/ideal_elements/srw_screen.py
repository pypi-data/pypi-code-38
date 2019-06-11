from syned.beamline.optical_elements.ideal_elements.screen import Screen

from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElement

class SRWScreen(Screen, SRWOpticalElement):
    def __init__(self, name="Undefined"):
        SRWOpticalElement.__init__(self, optical_element_displacement=None)
        Screen.__init__(self, name=name)

    def applyOpticalElement(self, wavefront=None, parameters=None, element_index=None):
        return wavefront

    def add_to_srw_native_array(self, oe_array = [], pp_array=[], parameters=None, wavefront=None):
        pass

    def to_python_code(self, data=None):
        return ""
