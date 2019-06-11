
from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.storage_ring.magnetic_structures.srw_wiggler import SRWWiggler

class SRWWigglerLightSource(SRWLightSource):

    def __init__(self,
                 name="Undefined",
                 electron_energy_in_GeV = 1.0,
                 electron_energy_spread = 0.0,
                 ring_current = 0.1,
                 electrons_per_bunch = 400,
                 electron_beam_size_h=0.0,
                 electron_beam_size_v=0.0,
                 emittance=0.0,
                 coupling_costant=0.0,
                 K_vertical = 0.0,
                 K_horizontal = 0.0,
                 period_length = 0.0,
                 number_of_periods = 1):

        super().__init__(name,
                         electron_energy_in_GeV = electron_energy_in_GeV,
                         electron_energy_spread = electron_energy_spread,
                         ring_current = ring_current,
                         electrons_per_bunch = electrons_per_bunch,
                         electron_beam_size_h=electron_beam_size_h,
                         electron_beam_size_v=electron_beam_size_v,
                         emittance=emittance,
                         coupling_costant=coupling_costant,
                         magnetic_structure=SRWWiggler(K_vertical,
                                                       K_horizontal,
                                                       period_length,
                                                       number_of_periods))

        self._electron_beam.set_drift_distance(-1.1*self.get_length()/2)

    def get_length(self):
        return self._magnetic_structure._period_length*self._magnetic_structure._number_of_periods

