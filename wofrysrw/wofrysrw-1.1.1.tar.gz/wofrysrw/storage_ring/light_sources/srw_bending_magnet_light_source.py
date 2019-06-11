from wofrysrw.storage_ring.srw_light_source import SRWLightSource
from wofrysrw.storage_ring.magnetic_structures.srw_bending_magnet import SRWBendingMagnet
from wofrysrw.storage_ring.srw_electron_beam import SRWElectronBeam

from syned.storage_ring.magnetic_structures.bending_magnet import BendingMagnet

class SRWBendingMagnetLightSource(SRWLightSource):

    def __init__(self,
                 name="Undefined",
                 electron_beam=SRWElectronBeam(),
                 bending_magnet_magnetic_structure=SRWBendingMagnet()):


        super().__init__(name,
                         electron_beam=electron_beam,
                         magnetic_structure=bending_magnet_magnetic_structure)
