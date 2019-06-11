from unittest import TestCase
from unittest.mock import patch, Mock
from chibi.circuit.chip.mcp3008 import MCP3008, MCP3008_channel
from chibi.circuit.sensor.MQ import MQ2, MQ3, MQ4, MQ6, MQ7, MQ8, MQ135
from chibi.circuit.sensor.rack_sensor import Rack_sensor
from tests.circuit.mcp3008 import Set_up_mcp3008


def Test_rack_sensors( Set_up_mcp3008, TestCase ):
    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensors = [
            MQ2( self.channel ), MQ3( self.channel ), MQ4( self.channel ),
            MQ6( self.channel ), MQ7( self.channel ), MQ8( self.channel ),
            MQ135( self.channel ) ]
        self.rack_sensor = Rack_sensor( self.sensors )

    def test_read_should_combine_all_the_read_sensors( self ):
        result = self.rack_sensor.read()
        for sensor in self.sensors:
            sensor_read = sensor.read()
