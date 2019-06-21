from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from iotile.core.utilities.typedargs.annotate import returns, param, annotated, return_type, context
from iotile.core.utilities.typedargs import type_system
from iotile.core.utilities.packed import unpack
from iotile.core.exceptions import *


@context("TileManager")
class TileManagerPlugin (TileBusProxyPlugin):
    def __init__(self, parent):
        super(TileManagerPlugin, self).__init__(parent)

    @return_type("integer")
    def count_tiles(self):
        res = self.rpc(0x2a, 0x01, result_type=(1, False))

        return res['ints'][0]

    @return_type("fw_tiledescriptor")
    @param("index", "integer", desc="Index of tile to describe")
    def describe_tile(self, index):
        """
        Return a tile's registration information by index
        """
        res = self.rpc(0x2a, 0x02, index, result_type=(0, True))

        return type_system.convert_to_type(res['buffer'], 'fw_tiledescriptor')

    @return_type("fw_tiledescriptor")
    @param("selector", "fw_tileselector", desc="Slot to examine (0 for controller slot)")
    def describe_selector(self, selector):
        """Get the registration information for the tile in a given slot
        """

        for i in range(0, self.count_tiles()):
            desc = self.describe_tile(i)

            if selector.matches_descriptor(desc):
                return desc

        raise HardwareError("No tile was found that matches the specified selector", selector=selector)
