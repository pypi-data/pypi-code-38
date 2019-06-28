import pigpio

from iot_gh.GHService import GHService

class IoTGreenhouseService(GHService):
    """A container class for IoT Greenhouse services implemented on the 
    Raspberry Pi.
    """

    def __init__(self):
        import spidev

        pi = pigpio.pi()
        spi = spidev.SpiDev()
        super().__init__(pi, spi)
