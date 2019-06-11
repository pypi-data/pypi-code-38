from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElement
from syned.beamline.shape import Circle, Ellipse, Rectangle

from oasys_srw.srwlib import *

class PlaneOfFocusing:
    HORIZONTAL=1
    VERTICAL=2
    BOTH=3

    @classmethod
    def items(cls):
        return ["Horizontal", "Vertical", "Both"]

class CRLShape:
    PARABOLIC=1
    SPHERICAL=2

    @classmethod
    def items(cls):
        return ["Parabolic", "Spherical"]

class SRWCRL(SRWOpticalElement):

    """
    Setup Transmission type Optical Element which simulates Compound Refractive Lens (CRL)
    :param _foc_plane: plane of focusing: 1- horizontal, 2- vertical, 3- both
    :param _delta: refractive index decrement (can be one number of array vs photon energy)
    :param _atten_len: attenuation length [m] (can be one number of array vs photon energy)
    :param _shape: 1- parabolic, 2- circular (spherical)
    :param _apert_h: horizontal aperture size [m]
    :param _apert_v: vertical aperture size [m]
    :param _r_min: radius (on tip of parabola for parabolic shape) [m]
    :param _n: number of lenses (/"holes")
    :param _wall_thick: min. wall thickness between "holes" [m]
    :param _xc: horizontal coordinate of center [m]
    :param _yc: vertical coordinate of center [m]
    :param _void_cen_rad: flat array/list of void center coordinates and radii: [x1, y1, r1, x2, y2, r2,...]
    :param _e_start: initial photon energy
    :param _e_fin: final photon energy
    :param _nx: number of points vs horizontal position to represent the transmission element
    :param _ny: number of points vs vertical position to represent the transmission element
    :param _ang_rot_ex: angle [rad] of CRL rotation about horizontal axis
    :param _ang_rot_ey: angle [rad] of CRL rotation about vertical axis
    :param _ang_rot_ez: angle [rad] of CRL rotation about longitudinal axis
    :return: transmission (SRWLOptT) type optical element which simulates CRL
    """
    def __init__(self,
                 name="Undefined",
                 optical_element_displacement       = None,
                 plane_of_focusing=PlaneOfFocusing.BOTH,
                 refractive_index=1e-6,
                 attenuation_length=1e-3,
                 shape=CRLShape.PARABOLIC,
                 horizontal_aperture_size=1e-3,
                 vertical_aperture_size=1e-3,
                 radius_of_curvature=5e-3,
                 number_of_lenses=10,
                 wall_thickness=5e-5,
                 horizontal_center_coordinate=0.0,
                 vertical_center_coordinate=0.0,
                 void_center_coordinates=None,
                 initial_photon_energy=8000,
                 final_photon_energy=8010,
                 horizontal_points=1001,
                 vertical_points=1001):
        SRWOpticalElement.__init__(self, optical_element_displacement=optical_element_displacement)

        self._name = name

        self.plane_of_focusing = plane_of_focusing
        self.refractive_index = refractive_index
        self.attenuation_length = attenuation_length
        self.shape = shape
        self.horizontal_aperture_size = horizontal_aperture_size
        self.vertical_aperture_size = vertical_aperture_size
        self.radius_of_curvature = radius_of_curvature
        self.number_of_lenses = number_of_lenses
        self.wall_thickness = wall_thickness
        self.horizontal_center_coordinate = horizontal_center_coordinate
        self.vertical_center_coordinate = vertical_center_coordinate
        self.void_center_coordinates = void_center_coordinates
        self.initial_photon_energy = initial_photon_energy
        self.final_photon_energy = final_photon_energy
        self.horizontal_points = horizontal_points
        self.vertical_points = vertical_points

    def toSRWLOpt(self):
        return srwl_opt_setup_CRL(_foc_plane=self.plane_of_focusing,
                                  _delta=self.refractive_index,
                                  _atten_len=self.attenuation_length,
                                  _shape=self.shape,
                                  _apert_h=self.horizontal_aperture_size,
                                  _apert_v=self.vertical_aperture_size,
                                  _r_min=self.radius_of_curvature,
                                  _n=self.number_of_lenses,
                                  _wall_thick=self.wall_thickness,
                                  _xc=self.horizontal_center_coordinate,
                                  _yc=self.vertical_center_coordinate,
                                  _void_cen_rad=self.void_center_coordinates,
                                  _e_start=self.initial_photon_energy,
                                  _e_fin=self.final_photon_energy,
                                  _nx=self.horizontal_points,
                                  _ny=self.vertical_points)

    def fromSRWLOpt(self, srwlopt=None):
        if not srwlopt.input_params or not srwlopt.input_params["type"] == "crl":
            raise TypeError("SRW optical element is not a CRL")

        self.plane_of_focusing = srwlopt.input_params["focalPlane"]
        self.refractive_index = srwlopt.input_params["refractiveIndex"]
        self.attenuation_length = srwlopt.input_params["attenuationLength"]
        self.shape = srwlopt.input_params["shape"]
        self.horizontal_aperture_size = srwlopt.input_params["horizontalApertureSize"]
        self.vertical_aperture_size = srwlopt.input_params["verticalApertureSize"]
        self.radius_of_curvature = srwlopt.input_params["radius"]
        self.number_of_lenses = srwlopt.input_params["numberOfLenses"]
        self.wall_thickness = srwlopt.input_params["wallThickness"]
        self.horizontal_center_coordinate = srwlopt.input_params["horizontalCenterCoordinate"]
        self.vertical_center_coordinate = srwlopt.input_params["verticalCenterCoordinate"]
        self.void_center_coordinates = srwlopt.input_params["voidCenterCoordinates"]
        self.initial_photon_energy = srwlopt.input_params["initialPhotonEnergy"]
        self.final_photon_energy = srwlopt.input_params["finalPhotonPnergy"]
        self.horizontal_points = srwlopt.input_params["horizontalPoints"]
        self.vertical_points = srwlopt.input_params["verticalPoints"]

    def to_python_code(self, data=None):
        text_code = data[0] + "=srwl_opt_setup_CRL(_foc_plane=" + str(self.plane_of_focusing) + ",\n"
        text_code += "                _delta=" + str(self.refractive_index) + ",\n"
        text_code += "                _atten_len=" + str(self.attenuation_length) + ",\n"
        text_code += "                _shape=" + str(self.shape) + ",\n"
        text_code += "                _apert_h=" + str(self.horizontal_aperture_size) + ",\n"
        text_code += "                _apert_v=" + str(self.vertical_aperture_size) + ",\n"
        text_code += "                _r_min=" + str(self.radius_of_curvature) + ",\n"
        text_code += "                _n=" + str(self.number_of_lenses) + ",\n"
        text_code += "                _wall_thick=" + str(self.wall_thickness) + ",\n"
        text_code += "                _xc=" + str(self.horizontal_center_coordinate) + ",\n"
        text_code += "                _yc=" + str(self.vertical_center_coordinate) + ",\n"
        text_code += "                _void_cen_rad=" + str(self.void_center_coordinates) + ",\n"
        text_code += "                _e_start=" + str(self.initial_photon_energy) + ",\n"
        text_code += "                _e_fin=" + str(self.final_photon_energy) + ",\n"
        text_code += "                _nx=" + str(self.horizontal_points) + ",\n"
        text_code += "                _ny=" + str(self.vertical_points) + ")\n"

        return text_code

    def get_boundary_shape(self):
        if self.plane_of_focusing == PlaneOfFocusing.BOTH:
            return Ellipse(a_axis_min=self.horizontal_center_coordinate - self.horizontal_aperture_size/2,
                           a_axis_max=self.horizontal_center_coordinate + self.horizontal_aperture_size/2,
                           b_axis_min=self.vertical_center_coordinate + self.vertical_aperture_size/2,
                           b_axis_max=self.vertical_center_coordinate + self.vertical_aperture_size/2)
        else:
            return Rectangle(x_left=self.horizontal_center_coordinate - self.horizontal_aperture_size/2,
                             x_right=self.horizontal_center_coordinate + self.horizontal_aperture_size/2,
                             y_bottom=self.vertical_center_coordinate + self.vertical_aperture_size/2,
                             y_top=self.vertical_center_coordinate + self.vertical_aperture_size/2)
