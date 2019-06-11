from syned.beamline.shape import Circle

from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElement

from oasys_srw.srwlib import *

class SRWZonePlate(SRWOpticalElement):
    def __init__(self,
                 name="Undefined",
                 optical_element_displacement=None,
                 total_number_of_zones=100,
                 outer_zone_radius=0.1e-03,
                 thickness=10e-06,
                 delta_main_material=1e-06,
                 delta_complementary_material=0.0,
                 attenuation_length_main_material=0.1,
                 attenuation_length_complementary_material=1e-06,
                 x=0.0,
                 y=0.0):
        SRWOpticalElement.__init__(self, optical_element_displacement=optical_element_displacement)

        self._name=name

        self.total_number_of_zones=total_number_of_zones
        self.outer_zone_radius=outer_zone_radius
        self.thickness=thickness
        self.delta_main_material=delta_main_material
        self.delta_complementary_material=delta_complementary_material
        self.attenuation_length_main_material=attenuation_length_main_material
        self.attenuation_length_complementary_material=attenuation_length_complementary_material
        self.x = x
        self.y = y

    def toSRWLOpt(self):
        return SRWLOptZP(_nZones=self.total_number_of_zones,
                         _rn=self.outer_zone_radius,
                         _thick=self.thickness,
                         _delta1=self.delta_main_material,
                         _atLen1=self.attenuation_length_main_material,
                         _delta2=self.delta_complementary_material,
                         _atLen2=self.attenuation_length_complementary_material,
                         _x=self.x,
                         _y=self.y)

    def fromSRWLOpt(self, srwlopt=SRWLOptZP()):
        self.total_number_of_zones = srwlopt.nZones
        self.outer_zone_radius = srwlopt.rn
        self.thickness=srwlopt.thick
        self.delta_main_material=srwlopt.delta1
        self.delta_complementary_material=srwlopt.delta2
        self.attenuation_length_main_material=srwlopt.atLen1
        self.attenuation_length_complementary_material=srwlopt.atLen2
        self.x = srwlopt.x
        self.y = srwlopt.y

    def to_python_code(self, data=None):
        text_code = data[0] + "="+  "SRWLOptZP(_nZones=" + str(self.total_number_of_zones) + "," +  "\n"
        text_code += "                _rn=" + str(self.outer_zone_radius) + "," +  "\n"
        text_code += "                _thick=" + str(self.thickness) + "," +  "\n"
        text_code += "                _delta1=" + str(self.delta_main_material) + "," +  "\n"
        text_code += "                _atLen1=" + str(self.attenuation_length_main_material) + "," +  "\n"
        text_code += "                _delta2=" + str(self.delta_complementary_material) + "," +  "\n"
        text_code += "                _atLen2=" + str(self.attenuation_length_complementary_material) + "," +  "\n"
        text_code += "                _x=" + str(self.x) + "," +  "\n"
        text_code += "                _y=" + str(self.y) + ")" + "\n"

        return text_code

    def get_boundary_shape(self):
        return Circle(a_axis_min=self.outer_zone_radius,
                      x_center=self.x,
                      y_center=self.y)
