import numpy

from syned.beamline.optical_elements.gratings.grating import Grating
from syned.beamline.shape import Ellipse, Rectangle, Circle

from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElementWithAcceptanceSlit
from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontPropagationParameters
from wofrysrw.beamline.optical_elements.absorbers.srw_aperture import SRWAperture

from oasys_srw.srwlib import SRWLOptC, SRWLOptMir, SRWLOptG
from oasys_srw.srwlib import srwl, srwl_opt_setup_surf_height_1d, srwl_opt_setup_surf_height_2d, srwl_uti_read_data_cols

from wofrysrw.beamline.optical_elements.mirrors.srw_mirror import Orientation, TreatInputOutput, ApertureShape, SimulationMethod

class SRWGrating(Grating, SRWOpticalElementWithAcceptanceSlit):
    def __init__(self,
                 name                               = "Undefined",
                 optical_element_displacement       = None,
                 tangential_size                    = 1.2,
                 sagittal_size                      = 0.01,
                 grazing_angle                      = 0.003,
                 vertical_position_of_mirror_center = 0.0,
                 horizontal_position_of_mirror_center = 0.0,
                 orientation_of_reflection_plane    = Orientation.UP,
                 invert_tangent_component           = False,
                 add_acceptance_slit=False,
                 height_profile_data_file           = "mirror.dat",
                 height_profile_data_file_dimension = 1,
                 height_amplification_coefficient   = 1.0,
                 diffraction_order                  = 1,
                 grooving_density_0                 =800, # groove density [lines/mm] (coefficient a0 in the polynomial groove density: a0 + a1*y + a2*y^2 + a3*y^3 + a4*y^4)
                 grooving_density_1                 =0.0, # groove density polynomial coefficient a1 [lines/mm^2]
                 grooving_density_2                 =0.0, # groove density polynomial coefficient a2 [lines/mm^3]
                 grooving_density_3                 =0.0, # groove density polynomial coefficient a3 [lines/mm^4]
                 grooving_density_4                 =0.0, # groove density polynomial coefficient a4 [lines/mm^5]
                 grooving_angle                     = 0.0 # angle between the grove direction and the sagittal direction of the substrate
                 ):

        SRWOpticalElementWithAcceptanceSlit.__init__(self,
                                                     optical_element_displacement=optical_element_displacement,
                                                     tangential_size                      = tangential_size,
                                                     sagittal_size                        = sagittal_size,
                                                     grazing_angle                        = grazing_angle,
                                                     vertical_position_of_mirror_center   = vertical_position_of_mirror_center,
                                                     horizontal_position_of_mirror_center = horizontal_position_of_mirror_center,
                                                     orientation_of_reflection_plane      = orientation_of_reflection_plane,
                                                     invert_tangent_component             = invert_tangent_component,
                                                     add_acceptance_slit                  = add_acceptance_slit)

        Grating.__init__(self,
                        name=name,
                        boundary_shape=Rectangle(x_left=horizontal_position_of_mirror_center - 0.5*sagittal_size,
                                                 x_right=horizontal_position_of_mirror_center + 0.5*sagittal_size,
                                                 y_bottom=vertical_position_of_mirror_center - 0.5*tangential_size,
                                                 y_top=vertical_position_of_mirror_center + 0.5*tangential_size),
                        surface_shape=self.get_shape(),
                        ruling=grooving_density_0*1e3)

        self.height_profile_data_file = height_profile_data_file
        self.height_profile_data_file_dimension = height_profile_data_file_dimension
        self.height_amplification_coefficient = height_amplification_coefficient

        self.diffraction_order = diffraction_order

        self.grooving_density_0 = grooving_density_0
        self.grooving_density_1 = grooving_density_1
        self.grooving_density_2 = grooving_density_2
        self.grooving_density_3 = grooving_density_3
        self.grooving_density_4 = grooving_density_4
        self.grooving_angle     = grooving_angle

    def get_alpha_angle(self):
        return self.grazing_angle

    def get_beta_angle(self, photon_energy):
        wavelength = 1.239842e-3/photon_energy # in mm

        return numpy.arcsin(wavelength*self.grooving_density_0 - numpy.cos(self.get_alpha_angle())) # Grating Output Angle

    def get_deflection_angle(self, photon_energy):
        return self.get_alpha_angle() + self.get_beta_angle(photon_energy) + 1.57079632679 # Grating Deflection Angle

    def get_output_orientation_vectors(self, photon_energy):
        deflection_angle = self.get_deflection_angle(photon_energy)
        tangent = 1.0 if not self.invert_tangent_component else -1.0

        if self.orientation_of_reflection_plane == Orientation.UP:
            return 0,  numpy.sin(deflection_angle),  numpy.cos(deflection_angle), tangent, 0.0
        elif self.orientation_of_reflection_plane == Orientation.DOWN:
            return 0,  -numpy.sin(deflection_angle),  numpy.cos(deflection_angle), tangent, 0.0
        elif self.orientation_of_reflection_plane == Orientation.LEFT:
            return numpy.sin(deflection_angle),  0, numpy.cos(deflection_angle), 0.0, tangent
        elif self.orientation_of_reflection_plane == Orientation.RIGHT:
            return -numpy.sin(deflection_angle),  0, numpy.cos(deflection_angle), 0.0, tangent

    def get_shape(self):
        raise NotImplementedError()

    def applyOpticalElement(self, wavefront=None, parameters=None, element_index=None):
        optical_elements, propagation_parameters = super(SRWGrating, self).create_propagation_elements()

        if not self.height_profile_data_file is None:
            optical_elements.append(self.get_optTrEr(wavefront))
            propagation_parameters.append(WavefrontPropagationParameters().to_SRW_array())

        optBL = SRWLOptC(optical_elements, propagation_parameters)

        srwl.PropagElecField(wavefront, optBL)

        return wavefront

    def add_to_srw_native_array(self, oe_array = [], pp_array=[], parameters=None, wavefront=None):
        super(SRWGrating, self).add_to_srw_native_array(oe_array, pp_array, parameters)

        if not self.height_profile_data_file is None:
            oe_array.append(self.get_optTrEr(wavefront))
            pp_array.append(WavefrontPropagationParameters().to_SRW_array())

    def get_substrate_mirror(self):
        nvx, nvy, nvz, tvx, tvy = self.get_orientation_vectors()
        x, y = self.getXY()

        if isinstance(self.get_boundary_shape(), Rectangle):
            ap_shape = ApertureShape.RECTANGULAR
        elif isinstance(self.get_boundary_shape(), Ellipse) or isinstance(self.get_boundary_shape(), Circle):
            ap_shape = ApertureShape.ELLIPTIC

        return self.get_SRWLOptMir(nvx, nvy, nvz, tvx, tvy, x, y, ap_shape)


    def toSRWLOpt(self):
        substrate_mirror = self.get_substrate_mirror()

        grating = SRWLOptG(_mirSub=substrate_mirror,
                           _m=self.diffraction_order,
                           _grDen =self.grooving_density_0,
                           _grDen1=self.grooving_density_1,
                           _grDen2=self.grooving_density_2,
                           _grDen3=self.grooving_density_3,
                           _grDen4=self.grooving_density_4,
                           _grAng=self.grooving_angle)

        return grating


    def get_SRWLOptMir(self, nvx, nvy, nvz, tvx, tvy, x, y, ap_shape):
        mirror = SRWLOptMir()

        mirror.set_dim_sim_meth(_size_tang=self.tangential_size,
                                _size_sag=self.sagittal_size,
                                _ap_shape=ap_shape,
                                _sim_meth=SimulationMethod.THICK,
                                _treat_in_out=TreatInputOutput.WAVEFRONT_INPUT_CENTER_OUTPUT_CENTER)
        mirror.set_orient(_nvx=nvx,
                          _nvy=nvy,
                          _nvz=nvz,
                          _tvx=tvx,
                          _tvy=tvy,
                          _x = x,
                          _y = y)

        return mirror

    def get_optTrEr(self, wavefront):
        if self.orientation_of_reflection_plane == Orientation.LEFT or self.orientation_of_reflection_plane == Orientation.RIGHT:
            dim = 'x'
        elif self.orientation_of_reflection_plane == Orientation.UP or self.orientation_of_reflection_plane == Orientation.DOWN:
            dim = 'y'

        if self.height_profile_data_file_dimension == 1:
            height_profile_data = srwl_uti_read_data_cols(self.height_profile_data_file,
                                                          _str_sep='\t',
                                                          _i_col_start=0,
                                                          _i_col_end=1)

            optTrEr = srwl_opt_setup_surf_height_1d(_height_prof_data=height_profile_data,
                                                    _ang=self.grazing_angle,
                                                    _ang_r=self.get_deflection_angle(wavefront.get_photon_energy()),
                                                    _dim=dim,
                                                    _amp_coef=self.height_amplification_coefficient)

        elif self.height_profile_data_file_dimension == 2:
            height_profile_data = srwl_uti_read_data_cols(self.height_profile_data_file,
                                                          _str_sep='\t')

            optTrEr = srwl_opt_setup_surf_height_2d(_height_prof_data=height_profile_data,
                                                    _ang=self.grazing_angle,
                                                    _ang_r=self.get_deflection_angle(wavefront.get_photon_energy()),
                                                    _dim=dim,
                                                    _amp_coef=self.height_amplification_coefficient)

        return optTrEr



    def to_python_code(self, data=None):
        oe_name = data[0]
        wavefront = data[1]

        nvx, nvy, nvz, tvx, tvy = self.get_orientation_vectors()
        x, y = self.getXY()

        if isinstance(self.get_boundary_shape(), Rectangle):
            ap_shape = ApertureShape.RECTANGULAR
        elif isinstance(self.get_boundary_shape(), Ellipse) or isinstance(self.get_boundary_shape(), Circle):
            ap_shape = ApertureShape.ELLIPTIC

        if self.add_acceptance_slit:
            slit = SRWAperture()
            slit.fromSRWLOpt(self.get_acceptance_slit())

            text_code = slit.to_python_code(data=["acceptance_slits_" + oe_name])
            text_code += "\n"
        else:
            text_code = ""

        text_code += self.to_python_code_aux(nvx, nvy, nvz, tvx, tvy, x, y, ap_shape)

        text_code += "substrate_mirror.set_dim_sim_meth(_size_tang=" + str(self.tangential_size) + "," + "\n"
        text_code += "                                  _size_sag=" + str(self.sagittal_size) + "," + "\n"
        text_code += "                                  _ap_shape='" + str(ap_shape) + "'," + "\n"
        text_code += "                                  _sim_meth=" + str(SimulationMethod.THICK) + "," + "\n"
        text_code += "                                  _treat_in_out=" + str(TreatInputOutput.WAVEFRONT_INPUT_CENTER_OUTPUT_CENTER) + ")" + "\n"

        text_code += "substrate_mirror.set_orient(_nvx=" + str(nvx) + "," + "\n"
        text_code += "                            _nvy=" + str(nvy) + "," + "\n"
        text_code += "                            _nvz=" + str(nvz) + "," + "\n"
        text_code += "                            _tvx=" + str(tvx) + "," + "\n"
        text_code += "                            _tvy=" + str(tvy) + "," + "\n"
        text_code += "                            _x=" + str(x) + "," + "\n"
        text_code += "                            _y=" + str(y) + ")" + "\n"

        text_code += "\n"

        text_code += oe_name + "="+ "SRWLOptG(_mirSub=substrate_mirror" + "," + "\n"
        text_code += "               _m="     + str(self.diffraction_order) + "," + "\n"
        text_code += "               _grDen=" + str(self.grooving_density_0) + "," + "\n"
        text_code += "               _grDen1="+ str(self.grooving_density_1) + "," + "\n"
        text_code += "               _grDen2="+ str(self.grooving_density_2) + "," + "\n"
        text_code += "               _grDen3="+ str(self.grooving_density_3) + "," + "\n"
        text_code += "               _grDen4="+ str(self.grooving_density_4) + "," + "\n"
        text_code += "               _grAng= "+ str(self.grooving_angle) + ")" + "\n"

        if not self.height_profile_data_file is None:
            text_code += "\n"

            if self.orientation_of_reflection_plane == Orientation.LEFT or self.orientation_of_reflection_plane == Orientation.RIGHT:
                dim = 'x'
            elif self.orientation_of_reflection_plane == Orientation.UP or self.orientation_of_reflection_plane == Orientation.DOWN:
                dim = 'y'

            if self.height_profile_data_file_dimension == 1:
                text_code += "height_profile_data = srwl_uti_read_data_cols('" + self.height_profile_data_file + "'," + "\n"
                text_code += "                                              _str_sep='\\t'," + "\n"
                text_code += "                                              _i_col_start=0," + "\n"
                text_code += "                                              _i_col_end=1)" + "\n"

                text_code += "optTrEr_" + oe_name + " = srwl_opt_setup_surf_height_1d(_height_prof_data=height_profile_data," + "\n"
                text_code += "                                              _ang="+ str(self.grazing_angle) + "," + "\n"
                text_code += "                                              _ang_r="+ str(self.get_deflection_angle(wavefront.get_photon_energy())) + "," + "\n"
                text_code += "                                              _dim='"+ dim + "'," + "\n"
                text_code += "                                              _amp_coef="+ str(self.height_amplification_coefficient) + ")" + "\n"

            elif self.height_profile_data_file_dimension == 2:
                text_code += "height_profile_data = srwl_uti_read_data_cols('" + self.height_profile_data_file + "'," + "\n"
                text_code += "                                              _str_sep=\'\\t\')" + "\n"

                text_code += "optTrEr_" + oe_name + " = srwl_opt_setup_surf_height_2d(_height_prof_data=height_profile_data," + "\n"
                text_code += "                                              _ang="+ str(self.grazing_angle) + "," + "\n"
                text_code += "                                              _ang_r="+ str(self.get_deflection_angle(wavefront.get_photon_energy())) + "," + "\n"
                text_code += "                                              _dim='"+ dim + "'," + "\n"
                text_code += "                                              _amp_coef="+ str(self.height_amplification_coefficient) + ")" + "\n"

        return text_code

    def to_python_code_aux(self, nvx, nvy, nvz, tvx, tvy, x, y, ap_shape):
        raise NotImplementedError("This method is abstract")
