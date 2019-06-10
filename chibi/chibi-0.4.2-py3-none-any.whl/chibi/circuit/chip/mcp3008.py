import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


class MCP3008:
    """
    clase para abstraer el uso del chip MCP3008

    Attributes
    ==========
    v_dd: float
        voltaje del chip
    v_ref: float
        voltaje de refencia del chil
    """
    def __init__( self, v_dd=5, v_ref=5, spi_port=0, spi_device=0 ):
        self._chip = Adafruit_MCP3008.MCP3008(
            spi=SPI.SpiDev( spi_port, spi_device ) )
        self.v_dd = v_dd
        self.v_ref = v_ref
        self._channels = self._build_channels( 8 )

    def read( self, channel ):
        """
        lee un canal del chip

        Parameters
        ==========
        channel: int

        Returns
        =======
        int
            valor entre 0 y 1024
        """
        return self._chip.read_adc( channel )

    def read_voltage( self, channel ):
        """
        lee el voltaje de un canal del chip

        Parameters
        ==========
        channel: int

        Returns
        =======
        float
            valor entre 0 y v_ref
        """
        analogic, voltage = self.read_analogic_voltage( channel )
        return self[ channel ].read_voltage()

    def read_analogic_voltage( self, channel ):
        return self[ channel ].read_analogic_voltage()

    def __getitem__( self, channel ):
        return self._channels[ channel ]

    def __iter__( self ):
        return ( channel for channel in self._channels )

    def _build_channels( self, number_of_channels ):
        return [
            MCP3008_channel( self, i )
            for i in range( number_of_channels ) ]


class MCP3008_channel:
    """
    clase para leer un canal de manera dedicada de MCP3008
    """
    def __init__( self, chip, channel ):
        self.chip = chip
        self.channel = channel

    def read( self ):
        return self.chip.read( self.channel )

    def read_voltage( self ):
        analogic = self.read()
        voltage = analogic * ( self.chip.v_ref / 1023 )
        return voltage

    def read_analogic_voltage( self ):
        analogic = self.read()
        voltage = analogic * ( self.chip.v_ref / 1023 )
        return analogic, voltage
