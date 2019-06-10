class MQ:
    """
    clase general para leer los sensores de aire MQ

    Attributes
    ==========
    channel: py:class:`chibi.circuit.chip.mcp3008.MCP3008_channel`
    voltage: float
        voltage de entrada del sensor ( default=5 )
    resistance: float
        resistencia del sensor ( default=1000 )
    """
    def __init__( self, channel, voltage=5, resistance=1000 ):
        self.channel = channel
        self.voltage = voltage
        self.resistance = resistance

    def read( self ):
        """
        lee los valores del sensor

        Returns
        =======
        dict
        """
        raise NotImplementedError

    def read_analogic_voltage( self ):
        return self.channel.read_analogic_voltage()

    def read_all_lectures( self ):
        analog, voltage = self.read_analogic_voltage()
        resistance = self.calculate_resistance( voltage )
        return analog, voltage, resistance

    def read_voltage( self ):
        return self.channel.read_voltage()

    def resistance( self ):
        voltage_lecture = self.read_voltage()
        return self.calculate_resistance( voltage_lecture )

    def calculate_resistance( self, voltage ):
        return self.resistance * ( ( self.voltage - voltage ) / voltage )


class MQ2( MQ ):
    """
    sensor de gas lp
    """
    name = "MQ-2"
    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        value = self.calculate_gas_lp( resistance )
        return {
            'gas_lp': {
                "unit": "ppm",
                "description":
                    "Gas licuado del petróleo ( Propano, Butano, ambos )",
                "chemical_formula": [ "C3H8", "C4H10" ],
                "value": value,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            }
        }

    def read_gas_lp( self ):
         return self.calcualte_gas_lp( self.resistance )

    def calculate_gas_lp( self, resistance ):
         return 8555 * pow( resistance / 5463, -1.74 )


class MQ3( MQ ):
    """
    sensor de alcohol
    """
    name = "MQ-3"

    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        value = self.calculate_alcohol( resistance )
        return {
            'alchohol': {
                "unit": "mg/L",
                "description": "Alcohol ( Benceno, Propano, Etanol, Metanol )",
                "chemical_formula": [ "C6H6", "C3H8", "C2H6O", "CH3OH" ],
                "value": value,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            }
        }

    def read_alcohol( self ):
        return self.calculate_alcohol( self.resistance )

    def calculate_alcohol( self, resistance ):
        return  1.108 * pow( resistance / 5463, -1.41 )


class MQ4( MQ ):
    """
    sensor de metano
    """
    name = "MQ-4"

    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        value = self.calculate_methane( resistance )
        return {
            'methane': {
                "unit": "ppm",
                "description": "Gas natural, Metano",
                "chemical_formula": [ "CH4" ],
                "value": value,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            }
        }

    def read_methane( self ):
        return self.calculate_methane( self.resistance )

    def calculate_methane( self, resistance ):
        return 6922 * pow( resistance / 5463, -1.91 )


class MQ6( MQ ):
    """
    sensor de propano
    """
    name = "MQ-6"

    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        value = self.calculate_propane( resistance )
        return {
            'propane': {
                "unit": "ppm",
                "description": "Propano",
                "chemical_formula": [ "C3H8" ],
                "value": value,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            }
        }

    def read_propane( self ):
        return self.calculate_propane( self.resistance )

    def calculate_propane( self, resistance ):
        return 2738 * pow( resistance / 5463, -1.81 )


class MQ7( MQ ):
    """
    sensor de monocido de carbono
    """
    name = "MQ-7"

    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        value = self.calculate_co( resistance )
        return {
            'carbon_monoxide': {
                "unit": "ppm",
                "description": "Monóxido de Carbono",
                "chemical_formula": [ "CO" ],
                "value": value,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            }
        }

    def read_co( self ):
        return self.calculate_propane( self.resistance )

    def calculate_co( self, resistance ):
        return 233.9 * pow( resistance / 5463, -1.40 )



class MQ8( MQ ):
    """
    sensor de hidrogeno
    """

    name = "MQ-8"

    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        value = self.calculate_hydrogen( resistance )
        return {
            'hydrogen': {
                "unit": "ppm",
                "description": "Hidrógeno",
                "chemical_formula": [ "H2" ],
                "value": value,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            }
        }

    def read_hydrogen( self ):
        return self.calculate_hydrogen( self.resistance )

    def calculate_hydrogen( self, resistance ):
        return 1803 * pow( resistance / 5463, -0.66 )


class MQ135( MQ ):
    """
    sensor de de CO2, N2O y amoniaco
    """

    name = "MQ-135"

    def read( self ):
        analog, voltage, resistance = self.read_all_lectures()
        co2 = self.calculate_co2( resistance )
        n2o = self.calculate_n2o( resistance )
        ammonia = self.calculate_ammonia( resistance )

        return {
            'co2': {
                "unit": "ppm",
                "description": "Dióxido de carbono",
                "chemical_formula": [ "H2" ],
                "value": co2,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            },
            'n2o': {
                "unit": "ppm",
                "description":
                    "Óxidos de nitrógeno (Óxido nitroso, Óxido nítrico,"
                    "Anhídrido nitroso, Tetraóxido de nitrógeno,"
                    "Peróxido nítrico, Anhídrido nítrico)",
                "chemical_formula":
                    [ "NOx", "N2O", "NO", "N2O3", "N2O4", "NO2", "N2O5" ],
                "value": n2o,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            },
            'ammonia': {
                "unit": "ppm",
                "description": "Amoníaco",
                "chemical_formula": [ "NH3" ],
                "value": ammonia,
                "voltage": voltage,
                "resistance": resistance,
                "analogic_value": analog,
                "sensor": self.name
            },
        }

    def read_co2( self ):
        return self.calculate_co2( self.resistance )

    def read_n2o( self ):
        return self.calculate_n2o( self.resistance )

    def read_ammonia( self ):
        return self.calculate_ammonia( self.resistance )

    def calculate_co2( self, resistance ):
        return 245 * pow( resistance / 5463, -2.26 )

    def calculate_n2o( self, resistance ):
        return 132.6 * pow( resistance / 5463, -2.74 )

    def calculate_ammonia( self, resistance ):
        return 161.7 * pow( resistance / 5463, -2.26 )
