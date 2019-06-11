import numpy

from syned.beamline.optical_elements.crystals.crystal import Crystal, DiffractionGeometry
from syned.beamline.shape import Ellipse, Rectangle, Circle, Plane

from wofrysrw.beamline.optical_elements.srw_optical_element import SRWOpticalElement
from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontPropagationParameters

from oasys_srw.srwlib import SRWLOptCryst
from oasys_srw.srwlib import srwl, srwl_opt_setup_surf_height_1d, srwl_opt_setup_surf_height_2d, srwl_uti_read_data_cols

from wofrysrw.beamline.optical_elements.mirrors.srw_mirror import Orientation, TreatInputOutput, ApertureShape, SimulationMethod

'''
        :param _d_sp: (_d_space) crystal reflecting planes d-spacing (John's dA) [A]
        :param _psi0r: real part of 0-th Fourier component of crystal polarizability (John's psi0c.real) (units?)
        :param _psi0i: imaginary part of 0-th Fourier component of crystal polarizability (John's psi0c.imag) (units?)
        :param _psi_hr: (_psiHr) real part of H-th Fourier component of crystal polarizability (John's psihc.real) (units?)
        :param _psi_hi: (_psiHi) imaginary part of H-th Fourier component of crystal polarizability (John's psihc.imag) (units?)
        :param _psi_hbr: (_psiHBr:) real part of -H-th Fourier component of crystal polarizability (John's psimhc.real) (units?)
        :param _psi_hbi: (_psiHBi:) imaginary part of -H-th Fourier component of crystal polarizability (John's psimhc.imag) (units?)
        :param _tc: crystal thickness [m] (John's thicum)
        :param _ang_as: (_Tasym) asymmetry angle [rad] (John's alphdg)
        :param _nvx: horizontal coordinate of outward normal to crystal surface (John's angles: thdg, chidg, phidg)
        :param _nvy: vertical coordinate of outward normal to crystal surface (John's angles: thdg, chidg, phidg)
        :param _nvz: longitudinal coordinate of outward normal to crystal surface (John's angles: thdg, chidg, phidg)
        :param _tvx: horizontal coordinate of central tangential vector (John's angles: thdg, chidg, phidg)
        :param _tvy: vertical coordinate of central tangential vector (John's angles: thdg, chidg, phidg)
        :param _uc: crystal use case: 1- Bragg Reflection, 2- Bragg Transmission (Laue cases to be added)

'''

class SRWCrystal(Crystal, SRWOpticalElement):
    def __init__(self,
                 name                                 = "Undefined",
                 optical_element_displacement         = None,
                 orientation_of_reflection_plane      = Orientation.UP,
                 invert_tangent_component             = False,
                 d_spacing                            = 0.0,
                 psi_0r                               = 0.0,
                 psi_0i                               = 0.0,
                 psi_hr                               = 0.0,
                 psi_hi                               = 0.0,
                 psi_hbr                              = 0.0,
                 psi_hbi                              = 0.0,
                 asymmetry_angle                      = 0.0,
                 thickness                            = 0.0,
                 diffraction_geometry                 = DiffractionGeometry.BRAGG,
                 incident_angle                       = 0.0
                ):
        SRWOpticalElement.__init__(self, optical_element_displacement=optical_element_displacement)

        Crystal.__init__(self,
                         name,
                         surface_shape=Plane(),
                         boundary_shape=Rectangle(x_left=0.0,
                                                  x_right=0.0,
                                                  y_bottom=0.0,
                                                  y_top=0.0),
                         material="Unknown",
                         diffraction_geometry=diffraction_geometry,
                         asymmetry_angle = asymmetry_angle,
                         thickness = thickness
                        )

        self.orientation_of_reflection_plane                  = orientation_of_reflection_plane
        self.invert_tangent_component                         = invert_tangent_component

        self.d_spacing                            = d_spacing
        self.psi_0r                               = psi_0r
        self.psi_0i                               = psi_0i
        self.psi_hr                               = psi_hr
        self.psi_hi                               = psi_hi
        self.psi_hbr                              = psi_hbr
        self.psi_hbi                              = psi_hbi
        self.asymmetry_angle                      = asymmetry_angle
        self.thickness                            = thickness
        self.diffraction_geometry                 = diffraction_geometry
        self.grazing_angle                        = incident_angle

        if diffraction_geometry == DiffractionGeometry.LAUE: raise NotImplementedError("Laue Geometry is not yet supported")

    def toSRWLOpt(self):
        nvx, nvy, nvz, tvx, tvy = self.get_orientation_vectors()

        return SRWLOptCryst(_d_sp=self.d_spacing,
                            _psi0r=self.psi_0r,
                            _psi0i=self.psi_0i,
                            _psi_hr=self.psi_hr,
                            _psi_hi=self.psi_hi,
                            _psi_hbr=self.psi_hbr,
                            _psi_hbi=self.psi_hbi,
                            _tc=self.thickness,
                            _ang_as=self.asymmetry_angle,
                            _nvx=nvx,
                            _nvy=nvy,
                            _nvz=nvz,
                            _tvx=tvx,
                            _tvy=tvy,
                            _uc=1 if self.diffraction_geometry==DiffractionGeometry.BRAGG else 0)

    def to_python_code(self, data=None):
        oe_name = data[0]

        nvx, nvy, nvz, tvx, tvy = self.get_orientation_vectors()

        text_code  = oe_name + "="+ "SRWLOptCryst(_d_sp=" + str(self.d_spacing) + "," + "\n"
        text_code += "                        _psi0r=" + str(self.psi_0r) + "," + "\n"
        text_code += "                        _psi0i=" + str(self.psi_0i) + "," + "\n"
        text_code += "                        _psi_hr=" + str(self.psi_hr) + "," + "\n"
        text_code += "                        _psi_hi=" + str(self.psi_hi) + "," + "\n"
        text_code += "                        _psi_hbr=" + str(self.psi_hbr) + "," + "\n"
        text_code += "                        _psi_hbi=" + str(self.psi_hbi) + "," + "\n"
        text_code += "                        _tc=" + str(self.thickness) + "," + "\n"
        text_code += "                        _ang_as=" + str(self.asymmetry_angle) + "," + "\n"
        text_code += "                        _nvx=" + str(nvx) + "," + "\n"
        text_code += "                        _nvy=" + str(nvy) + "," + "\n"
        text_code += "                        _nvz=" + str(nvz) + "," + "\n"
        text_code += "                        _tvx=" + str(tvx) + "," + "\n"
        text_code += "                        _tvy=" + str(tvy)+ "," + "\n"
        text_code += "                        _uc=" + str(1 if self.diffraction_geometry==DiffractionGeometry.BRAGG else 0) + ")" + "\n"

        return text_code
