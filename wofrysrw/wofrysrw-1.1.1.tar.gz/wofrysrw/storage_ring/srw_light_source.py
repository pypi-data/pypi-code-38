import numpy

from oasys_srw.srwlib import srwl

from syned.storage_ring.light_source import LightSource

from wofry.beamline.decorators import LightSourceDecorator
from wofrysrw.srw_object import SRWObject
from wofrysrw.storage_ring.srw_magnetic_structure import SRWMagneticStructure
from wofrysrw.storage_ring.srw_electron_beam import SRWElectronBeam, SRWElectronBeamGeometricalProperties
from wofrysrw.propagator.wavefront2D.srw_wavefront import SRWWavefront, WavefrontParameters

class PowerDensityPrecisionParameters(object):
    def __init__(self,
                 precision_factor = 1.5,
                 computation_method = 1, # (1- "near field", 2- "far field")
                 initial_longitudinal_position = 0.0, # (effective if initial_longitudinal_position < final_longitudinal_position)
                 final_longitudinal_position = 0.0, # (effective if initial_longitudinal_position < final_longitudinal_position)
                 number_of_points_for_trajectory_calculation = 20000 #number of points for (intermediate) trajectory calculation
                 ):
        self._precision_factor = precision_factor
        self._computation_method = computation_method
        self._initial_longitudinal_position = initial_longitudinal_position
        self._final_longitudinal_position = final_longitudinal_position
        self._number_of_points_for_trajectory_calculation = number_of_points_for_trajectory_calculation

    def to_SRW_array(self):
        return [float(self._precision_factor),
                int(self._computation_method),
                float(self._initial_longitudinal_position),
                float(self._final_longitudinal_position),
                int(self._number_of_points_for_trajectory_calculation)]

class PhotonSourceProperties(object):

    def __init__(self,
                 rms_h = 0.0,
                 rms_v = 0.0,
                 rms_hp = 0.0,
                 rms_vp = 0.0,
                 coherence_volume_h = 0.0,
                 coherence_volume_v = 0.0,
                 diffraction_limit = 0.0):
        self._rms_h = rms_h
        self._rms_v = rms_v
        self._rms_hp = rms_hp
        self._rms_vp = rms_vp
        self._coherence_volume_h = coherence_volume_h
        self._coherence_volume_v = coherence_volume_v
        self._diffraction_limit = diffraction_limit

    def to_info(self):
        info = 'Photon beam (convolution): \n'
        info += '   RMS size H/V [um]: '+ repr(self._rms_h*1e6) + '  /  ' + repr(self._rms_v*1e6) + '\n'
        info += '   RMS divergence H/V [urad]: '+ repr(self._rms_hp*1e6) + '  /  ' + repr(self._rms_vp*1e6) + '\n\n'
        info += '   Coherent volume in H phase space: '+ repr(self._coherence_volume_h) + '\n'
        info += '   Coherent volume in V phase space: '+ repr(self._coherence_volume_v) + '\n\n'
        info += '   RMS diffraction limit source size [um]: '+ repr(self._diffraction_limit*1e6) + '\n'
        info += '   FWHM diffraction limit source size [um]: '+ repr(self._diffraction_limit*2.35*1e6)

        return info

class SRWLightSource(LightSource, LightSourceDecorator, SRWObject):
    def __init__(self,
                 name="Undefined",
                 electron_beam=SRWElectronBeam(),
                 magnetic_structure=SRWMagneticStructure()):
        LightSource.__init__(self, name, electron_beam, magnetic_structure)

        self.__source_wavefront_parameters = None

    def get_gamma(self):
        return self._electron_beam.gamma()

    def get_photon_source_properties(self):
        return NotImplementedError("must be implemented in subclasses")

    # from Wofry Decorator
    def get_wavefront(self, wavefront_parameters):
        return self.get_SRW_Wavefront(source_wavefront_parameters=wavefront_parameters).toGenericWavefront()

    def get_SRW_Wavefront(self, source_wavefront_parameters = WavefrontParameters()):
        self.__source_wavefront_parameters = source_wavefront_parameters

        mesh = source_wavefront_parameters.to_SRWRadMesh()

        wfr = SRWWavefront()
        wfr.allocate(mesh.ne, mesh.nx, mesh.ny)
        wfr.mesh = mesh
        wfr.partBeam = self._electron_beam.to_SRWLPartBeam()

        srwl.CalcElecFieldSR(wfr,
                             0,
                             self._magnetic_structure.get_SRWLMagFldC(),
                             source_wavefront_parameters._wavefront_precision_parameters.to_SRW_array())

        return wfr

    def get_source_wavefront_parameters(self):
        return self.__source_wavefront_parameters

    def to_python_code(self, data=None):
        is_multi_electron = data

        text_code = self.get_electron_beam().to_python_code()
        text_code += "\n"
        text_code += self.get_magnetic_structure().to_python_code()

        source_wavefront_parameters = self.get_source_wavefront_parameters()

        if not source_wavefront_parameters is None:
            text_code += "\n"
            text_code += source_wavefront_parameters.to_python_code()
            text_code += "\n"
            text_code += "wfr = SRWLWfr()" + "\n"
            text_code += "wfr.allocate(mesh.ne, mesh.nx, mesh.ny)" + "\n"
            text_code += "wfr.mesh = mesh" + "\n"
            text_code += "wfr.partBeam = part_beam" + "\n"
            text_code += "\n"
            text_code += "initial_mesh = deepcopy(wfr.mesh)"
            text_code += "\n"

            if not is_multi_electron:
                text_code += "srwl.CalcElecFieldSR(wfr, 0, magnetic_field_container, "
                text_code += source_wavefront_parameters._wavefront_precision_parameters.to_python_code() + ")" + "\n"

        return text_code

    def get_power_density(self,
                          source_wavefront_parameters = WavefrontParameters(),
                          power_density_precision_parameters = PowerDensityPrecisionParameters()):

        stkP = source_wavefront_parameters.to_SRWLStokes()

        srwl.CalcPowDenSR(stkP,
                          self._electron_beam.to_SRWLPartBeam(),
                          0,
                          self._magnetic_structure.get_SRWLMagFldC(),
                          power_density_precision_parameters.to_SRW_array())

        hArray = numpy.zeros(stkP.mesh.nx)
        vArray = numpy.zeros(stkP.mesh.ny)
        powerArray = numpy.zeros((stkP.mesh.nx,stkP.mesh.ny))

        # fill arrays
        ij = -1
        for j in range(stkP.mesh.ny):
            for i in range(stkP.mesh.nx):
                ij += 1
                xx = stkP.mesh.xStart + i*(stkP.mesh.xFin-stkP.mesh.xStart)/(stkP.mesh.nx-1)
                yy = stkP.mesh.yStart + j*(stkP.mesh.yFin-stkP.mesh.yStart)/(stkP.mesh.ny-1)
                powerArray[i,j] = stkP.arS[ij]
                hArray[i] = xx # mm
                vArray[j] = yy # mm

        return (hArray, vArray, powerArray)

    @classmethod
    def get_total_power_from_power_density(cls, h_array, v_array, power_density_matrix):
        area = (numpy.abs(h_array[1]-h_array[0])*numpy.abs(v_array[1]-v_array[0]))*1e6
        total_power = 0
        for i in range(0, len(h_array)):
            for j in range(0, len(v_array)):
                total_power += power_density_matrix[i, j]*area

        return total_power

