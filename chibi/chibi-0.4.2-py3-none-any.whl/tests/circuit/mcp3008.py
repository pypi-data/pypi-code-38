from unittest import TestCase
from unittest.mock import patch, Mock
from chibi.circuit.chip.mcp3008 import MCP3008, MCP3008_channel


class Set_up_mcp3008:
    @patch( 'spidev.SpiDev' )
    @patch( 'Adafruit_MCP3008.MCP3008' )
    def setUp( self, mcp3008, SpiDev ):
        super().setUp()
        self.chip = MCP3008()


class Test_mcp3008( Set_up_mcp3008, TestCase ):
    @patch( 'spidev.SpiDev' )
    @patch( 'Adafruit_MCP3008.MCP3008' )
    def test_should_can_espeficied_the_voltages( self, mcp3008, spidev ):
        chip = MCP3008( v_dd=12, v_ref=32 )
        self.assertEqual( chip.v_dd, 12 )
        self.assertEqual( chip.v_ref, 32 )

    def test_when_init_should_create_a_list_of_channels( self ):
        for i, channel in enumerate( self.chip._channels ):
            self.assertIsInstance( channel, MCP3008_channel )
            self.assertIs( channel.chip, self.chip )
            self.assertEqual( i, channel.channel )

    def test_when_build_channels_should_use_the_same_chip_for_everbody( self ):
        for i, channel in enumerate( self.chip._build_channels( 16 ) ):
            self.assertIsInstance( channel, MCP3008_channel )
            self.assertIs( channel.chip, self.chip )
            self.assertEqual( i, channel.channel )

    def test_when_iter_a_chip_should_return_a_iter_of_channels( self ):
        for i, channel in enumerate( self.chip ):
            self.assertIsInstance( channel, MCP3008_channel )
            self.assertIs( channel.chip, self.chip )
            self.assertEqual( i, channel.channel )

    def test_should_get_the_channel_using_the_get_item( self ):
        for i, channel in enumerate( self.chip ):
            self.assertIs( channel, self.chip[i] )


class Test_mcp3008_read_analogic( TestCase ):
    @patch( 'spidev.SpiDev' )
    @patch( 'Adafruit_MCP3008.MCP3008' )
    def setUp( self, mcp3008, SpiDev ):
        self.chip = MCP3008()

    @patch( 'chibi.circuit.chip.mcp3008.MCP3008_channel' )
    def test_analogic_and_voltage_should_return_a_tuple( self, mcp_channel ):
        MCP3008_channel.read.return_value = 512
        result = self.chip.read_analogic_voltage( 1 )
        self.assertIsInstance( result, tuple )
        self.assertEqual( len( result ), 2 )

    def test_read_should_call_the_base_chip( self ):
        for i in range( 8 ):
            self.chip.read( i )
            self.chip._chip.read_adc.assert_called_with( i )


class Test_mcp3008_read_voltage( Set_up_mcp3008, TestCase ):

    def test_voltage_should_return_a_float( self ):
        self.chip._chip.read_adc.return_value = 512
        result = self.chip.read_voltage( 1 )
        self.assertIsInstance( result, float )
        self.assertAlmostEqual( result, 2.5, delta=0.1 )

    def test_read_should_call_the_base_chip( self ):
        for i in range( 8 ):
            self.chip.read_voltage( i )
            self.chip._chip.read_adc.assert_called_with( i )
