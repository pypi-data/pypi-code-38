from openProduction.product import ProductExecutor

class HardwareCleanUp(ProductExecutor.ProductExecutor):
    """Result connector setup hooks"""
    
    def __init__(self, ctor):
        super(HardwareCleanUp, self).__init__(ctor)

    def unload_hardware_manager_00100(self, params, values):
        """Hardwarereferenzen löschen"""
        self.hardwareManager.stop()