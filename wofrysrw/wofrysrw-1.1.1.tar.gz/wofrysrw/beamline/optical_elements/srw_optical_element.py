import numpy

from syned.beamline.shape import Ellipse, Rectangle, Circle
from wofry.beamline.decorators import OpticalElementDecorator

from wofry.propagator.propagator import PropagationParameters
from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontPropagationParameters, WavefrontPropagationOptionalParameters
from wofrysrw.srw_object import SRWObject

from oasys_srw.srwlib import SRWLOptC, srwl, SRWLOptShift, SRWLOptAng

class Orientation:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class SRWOpticalElementDisplacement(SRWObject):

    BEFORE=0
    AFTER=1

    def __init__(self, shift_x=0.0, shift_y=0.0, rotation_x=0.0, rotation_y=0.0):
        self.shift_x=shift_x
        self.shift_y=shift_y
        self.rotation_x=rotation_x
        self.rotation_y=rotation_y

        self.has_shift = self.shift_x != 0.0 or self.shift_y != 0.0
        self.has_rotation = self.rotation_x != 0.0 or self.rotation_y != 0.0

    def to_python_code(self, data=None):
        oe_name = data[0]
        where = data[2]

        if where==SRWOpticalElementDisplacement.BEFORE:
            sign = -1
            suffix = "before_"
            text_where = "Before"
        elif where==SRWOpticalElementDisplacement.AFTER:
            sign = 1
            suffix = "after_"
            text_where = "After"

        text_code = ""

        if self.has_shift:
            text_code += "# " + oe_name + " Displacement (" + text_where + ")\n\n"

            text_code += "shift_" + suffix + oe_name + " = SRWLOptShift(_shift_x=" + str(sign*self.shift_x) + ", _shift_y=" + str(sign*self.shift_y) + ")" + "\n"
            text_code += "pp_shift_" + suffix + oe_name + " = " + WavefrontPropagationParameters().to_python_code() + "\n"

        if self.has_rotation:
            if self.has_shift: text_code += "\n"
            else: text_code += "# " + oe_name + " Displacement (" + text_where + ")\n\n"
            text_code += "rotation_" + suffix + oe_name + " = SRWLOptAng(_ang_x=" + str(sign*self.rotation_x) + ", _ang_y=" + str(sign*self.rotation_y) + ")" + "\n"
            text_code += "pp_rotation_" + suffix + oe_name + " = " + WavefrontPropagationParameters().to_python_code() + "\n"

        return text_code

class SRWOpticalElementDecorator(SRWObject):
    def toSRWLOpt(self):
        raise NotImplementedError("")

    def fromSRWLOpt(self, srwlopt=None):
        raise NotImplementedError("")

class SRWOpticalElement(SRWOpticalElementDecorator, OpticalElementDecorator):

    def __init__(self, optical_element_displacement=None):
        self.displacement = optical_element_displacement

    def add_displacement_to_array(self, oe_array, pp_array, where=SRWOpticalElementDisplacement.BEFORE):

        sign = -1 if where==SRWOpticalElementDisplacement.BEFORE else 1

        if self.displacement.has_shift:
            oe_array.append(SRWLOptShift(_shift_x=sign*self.displacement.shift_x, _shift_y=sign*self.displacement.shift_y))
            pp_array.append(self.get_default_propagation_parameters())

        if self.displacement.has_rotation:
            oe_array.append(SRWLOptAng(_ang_x=sign*self.displacement.rotation_x, _ang_y=sign*self.displacement.rotation_y))
            pp_array.append(self.get_default_propagation_parameters())

    def applyOpticalElement(self, wavefront=None, parameters=None, element_index=None):
        oe_array = []
        pp_array = []

        if not self.displacement is None:
            self.add_displacement_to_array(oe_array, pp_array, where=SRWOpticalElementDisplacement.BEFORE)

        oe_array.append(self.toSRWLOpt())
        pp_array.append(self.get_srw_wavefront_propagation_parameter(parameters))

        if not self.displacement is None:
            self.add_displacement_to_array(oe_array, pp_array, where=SRWOpticalElementDisplacement.AFTER)

        optBL = SRWLOptC(oe_array,
                         pp_array)

        srwl.PropagElecField(wavefront, optBL)

        return wavefront

    def add_to_srw_native_array(self, oe_array = [], pp_array=[], parameters=None, wavefront=None):
        if not self.displacement is None:
            self.add_displacement_to_array(oe_array, pp_array, where=SRWOpticalElementDisplacement.BEFORE)

        oe_array.append(self.toSRWLOpt())
        pp_array.append(self.get_srw_wavefront_propagation_parameter(parameters))

        if not self.displacement is None:
            self.add_displacement_to_array(oe_array, pp_array, where=SRWOpticalElementDisplacement.AFTER)

    def get_srw_wavefront_propagation_parameter(self, parameters):
        if isinstance(parameters, PropagationParameters):
            if not parameters.has_additional_parameter("srw_oe_wavefront_propagation_parameters"):
                wavefront_propagation_parameters = WavefrontPropagationParameters()
            else:
                wavefront_propagation_parameters = parameters.get_additional_parameter("srw_oe_wavefront_propagation_parameters")

                if not isinstance(wavefront_propagation_parameters, WavefrontPropagationParameters):
                    raise ValueError("SRW Wavefront Propagation Parameters are inconsistent")

            srw_parameters_array = wavefront_propagation_parameters.to_SRW_array()

            if parameters.has_additional_parameter("srw_oe_wavefront_propagation_optional_parameters"):
                wavefront_propagation_optional_parameters = parameters.get_additional_parameter("srw_oe_wavefront_propagation_optional_parameters")

                if not isinstance(wavefront_propagation_optional_parameters, WavefrontPropagationOptionalParameters):
                    raise ValueError("SRW Wavefront Propagation Optional Parameters are inconsistent")

                wavefront_propagation_optional_parameters.append_to_srw_array(srw_parameters_array)
        elif isinstance(parameters, list):
            wavefront_propagation_parameters = parameters[0]
            wavefront_propagation_optional_parameters = parameters[1]

            srw_parameters_array = wavefront_propagation_parameters.to_SRW_array()
            if not wavefront_propagation_optional_parameters is None: wavefront_propagation_optional_parameters.append_to_srw_array(srw_parameters_array)

        return srw_parameters_array

    def getXY(self):
        boundary_shape = self.get_boundary_shape()

        if not boundary_shape is None:
            if isinstance(boundary_shape, Rectangle) or isinstance(boundary_shape, Ellipse):
                x_left, x_right, y_bottom, y_top = boundary_shape.get_boundaries()

                return x_left + 0.5*(x_right-x_left), \
                       y_bottom + 0.5*(y_top-y_bottom)

            elif isinstance(boundary_shape, Circle):
                radius, x_center, y_center = boundary_shape.get_boundaries()

                return x_center, y_center
        else:
            return 0.0, 0.0

    def get_orientation_vectors(self):
        sign = (-1 if self.invert_tangent_component else 1)

        if self.orientation_of_reflection_plane == Orientation.LEFT:
            nvx = -numpy.cos(self.grazing_angle)
            nvy = 0
            nvz = -numpy.sin(self.grazing_angle)
            tvx = sign*numpy.sin(self.grazing_angle)
            tvy = 0
        elif self.orientation_of_reflection_plane == Orientation.RIGHT:
            nvx = numpy.cos(self.grazing_angle)
            nvy = 0
            nvz = -numpy.sin(self.grazing_angle)
            tvx = -sign*numpy.sin(self.grazing_angle)
            tvy = 0
        elif self.orientation_of_reflection_plane == Orientation.UP:
            nvx = 0
            nvy = numpy.cos(self.grazing_angle)
            nvz = -numpy.sin(self.grazing_angle)
            tvx = 0
            tvy = -sign*numpy.sin(self.grazing_angle)
        elif self.orientation_of_reflection_plane == Orientation.DOWN:
            nvx = 0
            nvy = -numpy.cos(self.grazing_angle)
            nvz = -numpy.sin(self.grazing_angle)
            tvx = 0
            tvy = -sign*numpy.sin(self.grazing_angle)

        return nvx, nvy, nvz, tvx, tvy

    def get_default_propagation_parameters(self):
        return WavefrontPropagationParameters().to_SRW_array()

from oasys_srw.srwlib import SRWLOptA

class SRWOpticalElementWithAcceptanceSlit(SRWOpticalElement):

    def __init__(self,
                 optical_element_displacement         = None,
                 tangential_size                      = 1.2,
                 sagittal_size                        = 0.01,
                 vertical_position_of_mirror_center   = 0.0,
                 horizontal_position_of_mirror_center = 0.0,
                 grazing_angle                        = 0.003,
                 orientation_of_reflection_plane      = Orientation.UP,
                 invert_tangent_component             = False,
                 add_acceptance_slit                  = False):

        super(SRWOpticalElementWithAcceptanceSlit, self).__init__(optical_element_displacement)

        self.vertical_position_of_mirror_center = vertical_position_of_mirror_center
        self.horizontal_position_of_mirror_center = horizontal_position_of_mirror_center

        self.tangential_size                                  = tangential_size
        self.sagittal_size                                    = sagittal_size
        self.grazing_angle                                    = grazing_angle
        self.orientation_of_reflection_plane                  = orientation_of_reflection_plane
        self.invert_tangent_component                         = invert_tangent_component

        self.add_acceptance_slit=add_acceptance_slit

    def get_acceptance_slit(self):
        if self.orientation_of_reflection_plane == Orientation.UP or \
                self.orientation_of_reflection_plane==Orientation.DOWN:
            vertical_aperture   = self.tangential_size*numpy.sin(self.grazing_angle)
            horizontal_aperture = self.sagittal_size
        else:
            vertical_aperture   = self.sagittal_size
            horizontal_aperture = self.tangential_size*numpy.sin(self.grazing_angle)

        return SRWLOptA('r', 'a', horizontal_aperture, vertical_aperture)

    def create_propagation_elements(self):
        optical_elements = []
        propagation_parameters = []

        if not self.displacement is None and self.displacement.where == SRWOpticalElementDisplacement.BEFORE:
            self.add_displacement_to_array(optical_elements, propagation_parameters)

        if not self.add_acceptance_slit:
            optical_elements.append(self.toSRWLOpt())
            propagation_parameters.append(self.get_srw_wavefront_propagation_parameter())
        else:
            optical_elements.extend([self.get_acceptance_slit(), self.toSRWLOpt()])
            propagation_parameters.extend([self.get_srw_wavefront_propagation_parameter(), # all the resizing/resampling goes to the slit
                                           self.get_default_propagation_parameters()]) # no resizing/resampling needed

        if not self.displacement is None and self.displacement.where == SRWOpticalElementDisplacement.AFTER:
            self.add_displacement_to_array(optical_elements, propagation_parameters)

        return optical_elements, propagation_parameters

    def add_to_srw_native_array(self, oe_array = [], pp_array=[], parameters=None, wavefront=None):
        if not self.displacement is None:
            self.add_displacement_to_array(oe_array, pp_array, where=SRWOpticalElementDisplacement.BEFORE)

        if not self.add_acceptance_slit:
            oe_array.append(self.toSRWLOpt())
            pp_array.append(self.get_srw_wavefront_propagation_parameter(parameters))
        else:
            oe_array.append(self.get_acceptance_slit())
            oe_array.append(self.toSRWLOpt())
            pp_array.append(self.get_srw_wavefront_propagation_parameter(parameters)) # all the resizing/resampling goes to the slit
            pp_array.append(self.get_default_propagation_parameters()) # no resizing/resampling needed

        if not self.displacement is None:
            self.add_displacement_to_array(oe_array, pp_array, where=SRWOpticalElementDisplacement.AFTER)
