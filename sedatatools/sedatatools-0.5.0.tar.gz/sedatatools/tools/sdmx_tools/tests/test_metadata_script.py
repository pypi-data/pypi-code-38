import pytest
from metadataGenerator_v2_3 import *


class TestHelpers:
    def test_geting_config_file(self):
        tableFips = 'SL200_FIPS'
        geoLevelInfo = [['SL100', 'Canada', '2', '2', '0'],['SL200', 'Provinces/Territories', '2', '2', '1']]
        assert getTableFipses(tableFips, geoLevelInfo) == 'SL200_FIPS,SL100_FIPS'

    def test_accronym_creation(self):
        testString = 'FORWARD SORTATION AREA'
        assert createAcronym(testString) == 'FSA'

    def test_accronym_creation_single_word(self):
        testString = 'state'
        assert createAcronym(testString) == 'STATE'

    def test_accronym_creation_weird_chars(self):
        testString = 'Province/Territories'
        assert createAcronym(testString) == 'PT'

    def test_data_type_checks_char(self):
        assert checkDataType('some string') == 1

    def test_data_type_checks_int(self):
        assert checkDataType(45) == 3

    def test_data_type_checks_float(self):
        assert checkDataType(3.5) == 2


    def test_config_verification(self):
        assert verifyConfig('c:\some invalid path') == False