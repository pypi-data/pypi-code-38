from wofrysrw.propagator.wavefront2D.srw_wavefront import WavefrontParameters, SRWWavefront
from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.storage_ring.srw_electron_beam import SRWElectronBeam

from oasys_srw.srwlib import *

'''
x = 0.0, #Transverse Coordinates of Gaussian Beam Center at Waist [m]
y = 0.0,
z = 0.0, #Longitudinal Coordinate of Waist [m]
xp = 0.0,  #Average Angles of Gaussian Beam at Waist [rad]
yp = 0.0,
avgPhotEn = 12400, #5000 #Photon Energy [eV]
pulseEn = 0.001, #Energy per Pulse [J] - to be corrected
repRate = 1, #Rep. Rate [Hz] - to be corrected
polar = 1, #1- linear hoirizontal
sigX = 23e-06/2.35, #Horiz. RMS size at Waist [m]
sigY = 23e-06/2.35, #Vert. RMS size at Waist [m]
sigT = 10e-15, #Pulse duration [s] (not used?)
mx = 0, #Transverse Gauss-Hermite Mode Orders
my = 0
'''

class Polarization:
    LINEAR_HORIZONTAL  = 1
    LINEAR_VERTICAL    = 2
    LINEAR_45_DEGREES  = 3
    LINEAR_135_DEGREES = 4
    CIRCULAR_RIGHT     = 5
    CIRCULAR_LEFT      = 6

    @classmethod
    def tuple(cls):
        return ["Linear Horizontal",
                "Linear Vertical",
                "Linear 45\u00b0",
                "Linear 135\u00b0",
                "Circular Right",
                "Circular Left"]

class SRWGaussianLightSource(SRWLightSource):

    def __init__(self,
                 name="Undefined",
                 beam_center_at_waist_x = 0.0, #Transverse Coordinates of Gaussian Beam Center at Waist [m]
                 beam_center_at_waist_y = 0.0,
                 beam_center_at_waist_z = 0.0, #Longitudinal Coordinate of Waist [m]
                 average_angle_at_waist_x = 0.0, #Average Angles of Gaussian Beam at Waist [rad]
                 average_angle_at_waist_y = 0.0,
                 photon_energy = 12400,
                 energy_per_pulse = 0.001, #Energy per Pulse [J]
                 repetition_rate = 1, #[Hz]
                 polarization = Polarization.LINEAR_HORIZONTAL,
                 horizontal_sigma_at_waist = 1e-6,
                 vertical_sigma_at_waist = 1e-6,
                 pulse_duration = 10e-15, #[s]
                 transverse_gauss_hermite_mode_order_x = 0,
                 transverse_gauss_hermite_mode_order_y = 0
                 ):
        super().__init__(name,
                         electron_beam=None,
                         magnetic_structure=None)

        self.beam_center_at_waist_x                = beam_center_at_waist_x
        self.beam_center_at_waist_y                = beam_center_at_waist_y
        self.beam_center_at_waist_z                = beam_center_at_waist_z
        self.average_angle_at_waist_x              = average_angle_at_waist_x
        self.average_angle_at_waist_y              = average_angle_at_waist_y
        self.photon_energy                         = photon_energy
        self.energy_per_pulse                      = energy_per_pulse
        self.repetition_rate                       = repetition_rate
        self.polarization                          = polarization
        self.horizontal_sigma_at_waist             = horizontal_sigma_at_waist
        self.vertical_sigma_at_waist               = vertical_sigma_at_waist
        self.pulse_duration                        = pulse_duration
        self.transverse_gauss_hermite_mode_order_x = transverse_gauss_hermite_mode_order_x
        self.transverse_gauss_hermite_mode_order_y = transverse_gauss_hermite_mode_order_y

    # from Wofry Decorator
    def get_wavefront(self, wavefront_parameters):
        return self.get_SRW_Wavefront(source_wavefront_parameters=wavefront_parameters).toGenericWavefront()

    def get_SRW_Wavefront(self, source_wavefront_parameters = WavefrontParameters()):
        self.__source_wavefront_parameters = source_wavefront_parameters

        source_wavefront_parameters.photon_energy_min = self.photon_energy
        source_wavefront_parameters.photon_energy_max = self.photon_energy
        source_wavefront_parameters.photon_energy_points = 1

        mesh = source_wavefront_parameters.to_SRWRadMesh()

        GsnBm = SRWLGsnBm() #Gaussian Beam structure (just parameters)
        GsnBm.x         = self.beam_center_at_waist_x
        GsnBm.y         = self.beam_center_at_waist_y
        GsnBm.z         = self.beam_center_at_waist_z
        GsnBm.xp        = self.average_angle_at_waist_x
        GsnBm.yp        = self.average_angle_at_waist_y
        GsnBm.avgPhotEn = self.photon_energy
        GsnBm.pulseEn   = self.energy_per_pulse
        GsnBm.repRate   = self.repetition_rate
        GsnBm.polar     = self.polarization
        GsnBm.sigX      = self.horizontal_sigma_at_waist
        GsnBm.sigY      = self.vertical_sigma_at_waist
        GsnBm.sigT      = self.pulse_duration
        GsnBm.mx        = self.transverse_gauss_hermite_mode_order_x
        GsnBm.my        = self.transverse_gauss_hermite_mode_order_y

        wfr = SRWWavefront()
        wfr.allocate(mesh.ne, mesh.nx, mesh.ny)
        wfr.mesh = mesh

        wfr.partBeam.partStatMom1.x = GsnBm.x
        wfr.partBeam.partStatMom1.y = GsnBm.y
        wfr.partBeam.partStatMom1.z = GsnBm.z
        wfr.partBeam.partStatMom1.xp = GsnBm.xp
        wfr.partBeam.partStatMom1.yp = GsnBm.yp

        arPrecPar = [source_wavefront_parameters._wavefront_precision_parameters._sampling_factor_for_adjusting_nx_ny]

        srwl.CalcElecFieldGaussian(wfr, GsnBm, arPrecPar)

        return wfr

    def get_source_wavefront_parameters(self):
        return self.__source_wavefront_parameters

    def to_python_code(self, data=None):
        is_multi_electron = data

        text_code = ""

        source_wavefront_parameters = self.get_source_wavefront_parameters()

        if not source_wavefront_parameters is None:
            text_code += source_wavefront_parameters.to_python_code()
            text_code += "\n"
            text_code += "wfr = SRWLWfr()" + "\n"
            text_code += "wfr.allocate(mesh.ne, mesh.nx, mesh.ny)" + "\n"
            text_code += "wfr.mesh = mesh" + "\n"
            text_code += "\n"
            text_code += "initial_mesh = deepcopy(wfr.mesh)" + "\n"
            text_code += "\n"
            text_code += "GsnBm = SRWLGsnBm()" + "\n"
            text_code += "GsnBm.x         = " + str(self.beam_center_at_waist_x) + "\n"
            text_code += "GsnBm.y         = " + str(self.beam_center_at_waist_y) + "\n"
            text_code += "GsnBm.z         = " + str(self.beam_center_at_waist_z) + "\n"
            text_code += "GsnBm.xp        = " + str(self.average_angle_at_waist_x) + "\n"
            text_code += "GsnBm.yp        = " + str(self.average_angle_at_waist_y) + "\n"
            text_code += "GsnBm.avgPhotEn = " + str(self.photon_energy) + "\n"
            text_code += "GsnBm.pulseEn   = " + str(self.energy_per_pulse) + "\n"
            text_code += "GsnBm.repRate   = " + str(self.repetition_rate) + "\n"
            text_code += "GsnBm.polar     = " + str(self.polarization) + "\n"
            text_code += "GsnBm.sigX      = " + str(self.horizontal_sigma_at_waist) + "\n"
            text_code += "GsnBm.sigY      = " + str(self.vertical_sigma_at_waist) + "\n"
            text_code += "GsnBm.sigT      = " + str(self.pulse_duration) + "\n"
            text_code += "GsnBm.mx        = " + str(self.transverse_gauss_hermite_mode_order_x) + "\n"
            text_code += "GsnBm.my        = " + str(self.transverse_gauss_hermite_mode_order_y) + "\n"
            text_code += "\n"
            text_code += "wfr.partBeam.partStatMom1.x = GsnBm.x" + "\n"
            text_code += "wfr.partBeam.partStatMom1.y = GsnBm.y" + "\n"
            text_code += "wfr.partBeam.partStatMom1.z = GsnBm.z" + "\n"
            text_code += "wfr.partBeam.partStatMom1.xp = GsnBm.xp" + "\n"
            text_code += "wfr.partBeam.partStatMom1.yp = GsnBm.yp" + "\n"
            text_code += "\n"

            if not is_multi_electron:
                text_code += "srwl.CalcElecFieldGaussian(wfr, GsnBm, [" + str(source_wavefront_parameters._wavefront_precision_parameters._sampling_factor_for_adjusting_nx_ny) + "])" + "\n"

        return text_code
