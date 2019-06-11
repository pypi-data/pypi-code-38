import numpy

from oasys_srw.srwlib import SRWLPartBeam

from syned.storage_ring.electron_beam import ElectronBeam

from wofrysrw.srw_object import SRWObject

class SRWElectronBeamDecorator():

    def to_SRWLPartBeam(self):
        pass

    @classmethod
    def from_SRWLPartBeam(cls, srw_part_beam, number_of_bunches = 400):
        pass

class SRWElectronBeamGeometricalProperties(object):
    def __init__(self,
                 electron_beam_size_h = 0.0,
                 electron_beam_divergence_h = 0.0,
                 electron_beam_size_v = 0.0,
                 electron_beam_divergence_v = 0.0):
        self._electron_beam_size_h = electron_beam_size_h
        self._electron_beam_divergence_h = electron_beam_divergence_h
        self._electron_beam_size_v = electron_beam_size_v
        self._electron_beam_divergence_v = electron_beam_divergence_v

    def to_info(self):
        info = 'Electron beam : \n'
        info += '   RMS size H/V [um]: '+ repr(self._electron_beam_size_h*1e6) + '  /  ' + repr(self._electron_beam_size_v*1e6) + '\n'
        info += '   RMS divergence H/V [urad]: '+ repr(self._electron_beam_divergence_h*1e6) + '  /  ' + repr(self._electron_beam_divergence_v*1e6) + '\n\n'

        return info

class SRWElectronBeam(ElectronBeam, SRWElectronBeamDecorator, SRWObject):
    def __init__(self,
                 energy_in_GeV = 1.0,
                 energy_spread = 0.0,
                 current = 0.1,
                 number_of_bunches = 400,
                 moment_x=0.0,
                 moment_xp=0.0,
                 moment_y=0.0,
                 moment_yp=0.0,
                 moment_z=0.0,
                 moment_xx=0.0,
                 moment_xxp=0.0,
                 moment_xpxp=0.0,
                 moment_yy=0.0,
                 moment_yyp=0.0,
                 moment_ypyp=0.0):
        super().__init__(energy_in_GeV,
                         energy_spread,
                         current,
                         number_of_bunches,
                         moment_xx,
                         moment_xxp,
                         moment_xpxp,
                         moment_yy,
                         moment_yyp,
                         moment_ypyp)

        self._moment_x = moment_x
        self._moment_xp = moment_xp
        self._moment_y = moment_y
        self._moment_yp = moment_yp
        self._moment_z = moment_z

    def set_moments_from_twiss(self, horizontal_emittance = 0.0,
                                     horizontal_beta = 0.0,
                                     horizontal_alpha = 0.0,
                                     horizontal_eta = 0.0,
                                     horizontal_etap   = 0.0,
                                     vertical_emittance=0.0,
                                     vertical_beta     = 0.0,
                                     vertical_alpha    = 0.0,
                                     vertical_eta = 0.0,
                                     vertical_etap = 0.0):
        
        srw_electron_beam = self.to_SRWLPartBeam()
        srw_electron_beam.from_Twiss(_Iavg    =self._current,
                                     _e       =self._energy_in_GeV,
                                     _sig_e   =self._energy_spread,
                                     _emit_x  =horizontal_emittance,
                                     _beta_x  =horizontal_beta,
                                     _alpha_x =horizontal_alpha,
                                     _eta_x   =horizontal_eta,
                                     _eta_x_pr=horizontal_etap,
                                     _emit_y  =vertical_emittance,
                                     _beta_y  =vertical_beta,
                                     _alpha_y =vertical_alpha,
                                     _eta_y   =vertical_eta,
                                     _eta_y_pr=vertical_etap)
                                     
        srw_electron_beam = SRWElectronBeam.from_SRWLPartBeam(srw_electron_beam, self._number_of_bunches)

        self._energy_in_GeV       = srw_electron_beam._energy_in_GeV
        self._energy_spread       = srw_electron_beam._energy_spread
        self._current             = srw_electron_beam._current
        self._number_of_bunches   = srw_electron_beam._number_of_bunches
        self._moment_xx           = srw_electron_beam._moment_xx
        self._moment_xxp          = srw_electron_beam._moment_xxp
        self._moment_xpxp         = srw_electron_beam._moment_xpxp
        self._moment_yy           = srw_electron_beam._moment_yy
        self._moment_yyp          = srw_electron_beam._moment_yyp
        self._moment_ypyp         = srw_electron_beam._moment_ypyp
        self._moment_x            = srw_electron_beam._moment_x
        self._moment_xp           = srw_electron_beam._moment_xp
        self._moment_y            = srw_electron_beam._moment_y
        self._moment_yp           = srw_electron_beam._moment_yp
        self._moment_z            = srw_electron_beam._moment_z

    def set_moments_from_electron_beam_geometrical_properties(self, electron_beam_geometrical_properties = SRWElectronBeamGeometricalProperties()):
        self.set_sigmas_all(sigma_x=electron_beam_geometrical_properties._electron_beam_size_h,
                            sigma_xp=electron_beam_geometrical_properties._electron_beam_divergence_h,
                            sigma_y=electron_beam_geometrical_properties._electron_beam_size_v,
                            sigma_yp=electron_beam_geometrical_properties._electron_beam_divergence_v)

    def get_electron_beam_geometrical_properties(self):
        x, xp, y, yp = self.get_sigmas_all()

        return SRWElectronBeamGeometricalProperties(electron_beam_size_h=x,
                                                    electron_beam_divergence_h=xp,
                                                    electron_beam_size_v=y,
                                                    electron_beam_divergence_v=yp)
    def to_SRWLPartBeam(self):
        srw_electron_beam = SRWLPartBeam()
        srw_electron_beam.Iavg           = self._current

        srw_electron_beam.partStatMom1.x = self._moment_x
        srw_electron_beam.partStatMom1.y = self._moment_y
        srw_electron_beam.partStatMom1.z = self._moment_z
        srw_electron_beam.partStatMom1.xp = self._moment_xp
        srw_electron_beam.partStatMom1.yp = self._moment_yp
        srw_electron_beam.partStatMom1.gamma = self.gamma()

        #2nd order statistical moments:
        srw_electron_beam.arStatMom2[0] = self._moment_xx   # <(x-x0)^2> [m^2]
        srw_electron_beam.arStatMom2[1] = self._moment_xxp  # <(x-x0)*(x'-x'0)> [m]
        srw_electron_beam.arStatMom2[2] = self._moment_xpxp # <(x'-x'0)^2>
        srw_electron_beam.arStatMom2[3] = self._moment_yy   #<(y-y0)^2>
        srw_electron_beam.arStatMom2[4] = self._moment_yyp  #<(y-y0)*(y'-y'0)> [m]
        srw_electron_beam.arStatMom2[5] = self._moment_ypyp #<(y'-y'0)^2>
        srw_electron_beam.arStatMom2[10] = self._energy_spread**2 #<(E-E0)^2>/E0^2
                
        return srw_electron_beam

    @classmethod
    def from_SRWLPartBeam(cls, srw_part_beam, number_of_bunches = 400):
        srw_electron_beam = SRWElectronBeam(energy_spread = numpy.sqrt(srw_part_beam.arStatMom2[10]),
                                            current = srw_part_beam.Iavg,
                                            number_of_bunches = number_of_bunches,
                                            moment_x=srw_part_beam.partStatMom1.x,
                                            moment_y=srw_part_beam.partStatMom1.y,
                                            moment_z=srw_part_beam.partStatMom1.z,
                                            moment_xp=srw_part_beam.partStatMom1.xp,
                                            moment_yp=srw_part_beam.partStatMom1.yp,
                                            moment_xx  = srw_part_beam.arStatMom2[0],
                                            moment_xxp = srw_part_beam.arStatMom2[1],
                                            moment_xpxp= srw_part_beam.arStatMom2[2],
                                            moment_yy  = srw_part_beam.arStatMom2[3],
                                            moment_yyp = srw_part_beam.arStatMom2[4],
                                            moment_ypyp= srw_part_beam.arStatMom2[5])

        srw_electron_beam.set_energy_from_gamma(srw_part_beam.partStatMom1.gamma)

        return srw_electron_beam

    def to_python_code(self, data=None):
        text_code  = "part_beam = SRWLPartBeam()" + "\n"
        text_code += "part_beam.Iavg               = " + str(self._current) + "\n"
        text_code += "part_beam.partStatMom1.x     = " + str(self._moment_x) + "\n"
        text_code += "part_beam.partStatMom1.y     = " + str(self._moment_y) + "\n"
        text_code += "part_beam.partStatMom1.z     = " + str(self._moment_z) + "\n"
        text_code += "part_beam.partStatMom1.xp    = " + str(self._moment_xp) + "\n"
        text_code += "part_beam.partStatMom1.yp    = " + str(self._moment_yp) + "\n"
        text_code += "part_beam.partStatMom1.gamma = " + str(self.gamma()) + "\n"
        text_code += "part_beam.arStatMom2[0]      = " + str(self._moment_xx) + "\n"
        text_code += "part_beam.arStatMom2[1]      = " + str(self._moment_xxp) + "\n"
        text_code += "part_beam.arStatMom2[2]      = " + str(self._moment_xpxp) + "\n"
        text_code += "part_beam.arStatMom2[3]      = " + str(self._moment_yy) + "\n"
        text_code += "part_beam.arStatMom2[4]      = " + str(self._moment_yyp) + "\n"
        text_code += "part_beam.arStatMom2[5]      = " + str(self._moment_ypyp) + "\n"
        text_code += "part_beam.arStatMom2[10]     = " + str(self._energy_spread**2) + "\n"

        return text_code
