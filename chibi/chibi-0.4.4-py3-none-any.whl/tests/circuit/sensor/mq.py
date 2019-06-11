from unittest import TestCase
from unittest.mock import patch, Mock
from chibi.circuit.chip.mcp3008 import MCP3008, MCP3008_channel
from chibi.circuit.sensor.MQ import MQ2, MQ3, MQ4, MQ6, MQ7, MQ8, MQ135

from tests.circuit.mcp3008 import Set_up_mcp3008


class Test_mq_sensor:
    name = ''
    base_read_key = ''
    unit = ''
    keys = (
        'unit', 'description', 'chemical_formula', 'value', 'voltage',
        'resistance', 'analogic_value', 'sensor' )

    def test_when_is_build_the_name_of_the_sensor_should_be_correct( self ):
        self.assertEqual( self.sensor.name, self.name )

    def test_read_should_return_the_base_read_key( self ):
        result = self.sensor.read()
        self.assertIn( self.base_read_key, result )

    def test_read_should_return_all_the_expected_keys( self ):
        result = self.sensor.read()[ self.base_read_key ]
        expected_keys = set( self.keys )
        current_keys = set( result.keys() )
        self.assertSetEqual( expected_keys, current_keys )

    def test_read_should_return_the_correct_unit_of_gas( self ):
        result = self.sensor.read()[ self.base_read_key ]
        self.assertEqual( result[ 'unit' ], self.unit )

    def test_read_should_return_the_correct_name_of_the_sensor( self ):
        result = self.sensor.read()[ self.base_read_key ]
        self.assertEqual( result[ 'sensor' ], self.name )

    def test_result_should_have_the_expected_types( self ):
        result = self.sensor.read()[ self.base_read_key ]
        self.assertIsInstance( result[ 'unit' ], str )
        self.assertIsInstance( result[ 'description' ], str )
        self.assertIsInstance( result[ 'chemical_formula' ], list )
        self.assertIsInstance( result[ 'value' ], ( float, int ) )
        self.assertIsInstance( result[ 'voltage' ], ( float, int ) )
        self.assertIsInstance( result[ 'resistance' ], ( float, int ) )
        self.assertIsInstance( result[ 'analogic_value' ], ( int, float ) )
        self.assertIsInstance( result[ 'sensor' ], str )


class Test_mq2( Set_up_mcp3008, Test_mq_sensor, TestCase ):
    name = 'MQ-2'
    base_read_key = 'gas_lp'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ2( self.channel )


class Test_mq3( Set_up_mcp3008, Test_mq_sensor, TestCase ):
    name = 'MQ-3'
    base_read_key = 'alchohol'
    unit = 'mg/L'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ3( self.channel )


class Test_mq4( Set_up_mcp3008, Test_mq_sensor, TestCase ):
    name = 'MQ-4'
    base_read_key = 'methane'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ4( self.channel )


class Test_mq6( Set_up_mcp3008, Test_mq_sensor, TestCase ):
    name = 'MQ-6'
    base_read_key = 'propane'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ6( self.channel )


class Test_mq7( Set_up_mcp3008, Test_mq_sensor, TestCase ):
    name = 'MQ-7'
    base_read_key = 'carbon_monoxide'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ7( self.channel )


class Test_mq8( Set_up_mcp3008, Test_mq_sensor, TestCase ):
    name = 'MQ-8'
    base_read_key = 'hydrogen'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ8( self.channel )


class Test_mq135_co2( Test_mq_sensor, Set_up_mcp3008, TestCase ):
    name = 'MQ-135'
    base_read_key = 'co2'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ135( self.channel )


class Test_mq135_n20( Test_mq_sensor, Set_up_mcp3008, TestCase ):
    name = 'MQ-135'
    base_read_key = 'n2o'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ135( self.channel )


class Test_mq135_ammonia( Test_mq_sensor, Set_up_mcp3008, TestCase ):
    name = 'MQ-135'
    base_read_key = 'ammonia'
    unit = 'ppm'

    def setUp( self ):
        super().setUp()
        self.chip._chip.read_adc.return_value = 512
        self.channel = self.chip[0]
        self.sensor = MQ135( self.channel )
