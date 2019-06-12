import logging

class Converter(object):
    string_unit_dict = {} # override in child
    convert_from_methods = {}
    convert_to_methods = {}

    def string_to_units(self,unit_string):
        """Attempt to translate string description of units to known units"""
        if unit_string in self.string_unit_dict:
            return self.string_unit_dict[unit_string]
        raise ValueError("Unknown unit: %s" % unit_string)

    def convert_from(self,value,from_units):
        """Convert from given units to default units"""
        if from_units in self.convert_from_methods:
            return self.convert_from_methods[from_units](float(value))
        raise NotImplementedError("No method found for converting from %s" % from_units)

    def convert_to(self,value,to_units):
        """Convert from default units to given units"""
        if to_units in self.convert_to_methods:
            return self.convert_to_methods[to_units](float(value))
        raise NotImplementedError("No method found for converting to %s" % to_units)

    @staticmethod
    def no_conversion(value):
        return value

class TemperatureConverter(Converter):
    CELSIUS = 1
    FAHRENHEIT = 2

    string_unit_dict = {
        "degC" : CELSIUS,
        "degF" : FAHRENHEIT
    }

    def __init__(self):
        self.convert_from_methods = {
            self.CELSIUS : self.no_conversion,
            self.FAHRENHEIT : self.fahrenheit_to_celsius
        }

        self.convert_to_methods = {
            self.CELSIUS : self.no_conversion,
            self.FAHRENHEIT : self.celsius_to_fahrenheit
        }

    @staticmethod
    def celsius_to_fahrenheit(value):
        return value * float(9)/5 + 32

    @staticmethod
    def fahrenheit_to_celsius(value):
        return (value - 32) * float(5)/9

class PressureConverter(Converter):
    MBARA = 1
    KPAA = 2
    PSIA = 3
    MMHG = 4
    KGCM2 = 5

    string_unit_dict = {
        "mBar.A" : MBARA,
        "kPa.A" : KPAA,
        "PSI.A" : PSIA,
        "mmHg" : MMHG,
        "kg/cm2" : KGCM2
    }

    def __init__(self):
        self.convert_from_methods = {
            self.MBARA : self.no_conversion,
            self.KPAA : self.kpaa_to_mbara,
            self.PSIA : self.psia_to_mbara,
            self.MMHG : self.mmhg_to_mbara,
            self.KGCM2 : self.kgcm2_to_mbara,
        }

        self.convert_to_methods = {
            self.MBARA : self.no_conversion,
            self.KPAA : self.mbara_to_kpaa,
            self.PSIA : self.mbara_to_psia,
            self.MMHG : self.mbara_to_mmhg,
            self.KGCM2 : self.mbara_to_kgcm2,
        }

    @staticmethod
    def mbara_to_kpaa(value):
        return 0.1 * value

    @staticmethod
    def kpaa_to_mbara(value):
        return 10 * value

    @staticmethod
    def mbara_to_psia(value):
        return value * 0.01450377

    @staticmethod
    def psia_to_mbara(value):
        return value * 68.94757

    @staticmethod
    def mbara_to_mmhg(value):
        return value * 0.7500617

    @staticmethod
    def mmhg_to_mbara(value):
        return value * 1.333224

    @staticmethod
    def mbara_to_kgcm2(value):
        return value * 0.001019716

    @staticmethod
    def kgcm2_to_mbara(value):
        return value * 980.665