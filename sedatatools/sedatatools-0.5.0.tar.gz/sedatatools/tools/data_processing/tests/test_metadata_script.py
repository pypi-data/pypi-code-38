import pytest
from create_metadata_file import *


class TestHelpers:
    def test_geting_config_file(self):
        tableFips = 'SL200_FIPS'
        geoLevelInfo = [['SL100', 'Canada', '2', '2', '0'],['SL200', 'Provinces/Territories', '2', '2', '1']]
        assert get_table_fipses(tableFips, geoLevelInfo) == 'SL100_FIPS,SL200_FIPS'

    def test_accronym_creation(self):
        testString = 'FORWARD SORTATION AREA'
        assert create_acronym(testString) == 'FSA'

    def test_accronym_creation_single_word(self):
        testString = 'state'
        assert create_acronym(testString) == 'STATE'

    def test_accronym_creation_weird_chars(self):
        testString = 'Province/Territories'
        assert create_acronym(testString) == 'PT'

    def test_data_type_checks_char(self):
        assert check_data_type('char') == 1

    def test_data_type_checks_int(self):
        assert check_data_type('int') == 3

    def test_data_type_checks_float(self):
        assert check_data_type('float') == 2


    def test_config_verification(self):
        assert verify_config('c:\some invalid path') == False