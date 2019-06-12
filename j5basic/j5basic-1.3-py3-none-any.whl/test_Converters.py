from j5basic import Converters
from j5test.Utils import raises

def test_temperature_converter():
    temp_conv = Converters.TemperatureConverter()
    assert temp_conv.string_to_units('degC') == Converters.TemperatureConverter.CELSIUS
    assert temp_conv.convert_from(32, temp_conv.string_to_units('degF')) == 0
    assert temp_conv.convert_to(0, temp_conv.string_to_units('degF')) == 32

    assert raises(NotImplementedError, temp_conv.convert_from, 32, 'degF')
    assert raises(NotImplementedError, temp_conv.convert_to, 0, 'degC')

def test_pressure_converter():
    pc = Converters.PressureConverter()
    assert pc.convert_from(12, pc.KGCM2) is not None



