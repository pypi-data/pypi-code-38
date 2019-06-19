import pandas as pd
from psense_common import PSenseParser
from psense_common.psense_parser import is_float
import unittest
from unittest.mock import (patch, MagicMock, Mock)
from datetime import (datetime, timedelta)


class TestPSenseParser(unittest.TestCase):
    def setUp(self):
        self.parser = PSenseParser(debugmode=True)
        pass

    def test_is_float(self):
        self.assertTrue(is_float(0))
        self.assertTrue(is_float('0'))
        self.assertTrue(is_float('0.5'))
        self.assertFalse(is_float('A'))
        self.assertFalse(is_float({'value': 0.5}))
        self.assertFalse(is_float([0.5]))

    def test_force_source(self):
        self.assertRaises(IOError, self.parser.force_source, 'not-a-real-data-type')
        type1 = 'PSHIELD'
        self.parser.force_source(type1)
        self.assertEqual(self.parser.source, type1)
        self.assertEqual(self.parser.we_count, self.parser.num_channels[type1])
        type2 = 'BWII-DL'
        self.parser.force_source(type2)
        self.assertEqual(self.parser.source, type2)
        self.assertEqual(self.parser.we_count, self.parser.num_channels[type2])

    def test_find_header_text(self):
        mock_type = 'PSHIELD'
        search_string = self.parser.header_text[mock_type]

        m_open = MagicMock()
        m_methods = Mock()
        m_methods.tell.side_effect = [1, 2, 3, 4, 5, 15, 15]
        m_methods.readline.side_effect = ['random', 'random', search_string, 'random', 'random', 'random']
        m_open().__enter__.return_value = m_methods

        with patch('builtins.open', m_open, create=True):
            with patch('os.path.getsize', return_value=11):
                self.assertTrue(self.parser.find_header_text('fake_file', search_string))
                self.assertFalse(self.parser.find_header_text('fake_file', 'string-that-doesnt-exist'))

    def test_identify_file_source(self):

        self.assertRaises(FileNotFoundError, self.parser.identify_file_source, 'fake_file')

        self.parser.identify_file_source(fpath='tests/pshield_example')
        self.assertEqual(self.parser.source, 'PSHIELD')
        self.assertEqual(self.parser.we_count, self.parser.num_channels['PSHIELD'])
        self.parser.identify_file_source(fpath='tests/gamry_example')
        self.assertEqual(self.parser.source, 'EXPLAIN')
        self.parser.identify_file_source('tests/__init__.py')
        self.assertEqual(self.parser.source, None)

    def test_parse_record(self):
        starting_time = datetime.now()
        self.parser.force_source('BWII-DL')
        data = ','.join([starting_time.isoformat(), 'sensor_record', '1', '1', '.2', '.1', '', '', '', '10', '.4', '.2'])
        res = self.parser.parse_record(data)
        self.assertTrue(datetime.fromisoformat(res[0]) - starting_time < timedelta(seconds=3))
        self.assertTrue(res[1] == [0.0001, 0.0002])
        self.assertTrue(res[2] == [1.0, 10.0])

        data = '1, 1554417874.0000026, 12.51'
        self.parser.force_source('PSHIELD')
        res = self.parser.parse_record(data)
        self.assertEqual(res[0], '2019-04-04T15:44:34.000003')  # local time, not utc
        self.assertTrue(res[1] is None)
        self.assertEqual(res[2], 12.51)

        data = '0.399550	7.3E-9'
        self.parser.force_source('VFP')
        res = self.parser.parse_record(data)
        self.assertTrue(datetime.fromisoformat(res[0]) - starting_time < timedelta(seconds=3))
        self.assertTrue(res[1] == 0.39955)
        self.assertTrue(res[2] == 7.3)

        data = '2019-03-13 14:25:46,10,0.5,0.48,0.48,0.5,-0.0,0.0,0.0,0.48'
        self.parser.force_source('WEB1CHAN')
        res = self.parser.parse_record(data)
        self.assertEqual(res[0], '2019-03-13T14:25:46')
        self.assertEqual(res[1], .5)
        self.assertEqual(res[2], 10)

    def test_load_rawfile(self):
        testfile = 'tests/pshield_example'

        # fake source
        self.parser.source = 'fake-source'
        self.assertRaises(ValueError, self.parser.load_rawfile, testfile, None, None)

        # pshield file
        self.parser.identify_file_source(testfile)
        self.assertTrue(self.parser.load_rawfile(testfile, None, None))
        df = self.parser.data
        self.assertEqual(df['vout1'].iloc[-1], .5)
        self.assertEqual(df['signal1'].iloc[-1], 5.29)
        self.assertEqual(df['timestamp'].iloc[-1], pd.Timestamp('2018-07-23 17:28:08.229594946'))

        # psense format (bwii-instrument.py)
        testfile = 'tests/psense_example'
        self.parser.identify_file_source(testfile)
        self.assertTrue(self.parser.load_rawfile(testfile, None, None))
        df = self.parser.data
        self.assertEqual(df['vout1'].iloc[-1], 0)
        self.assertEqual(df['signal1'].iloc[-1], 1)
        self.assertEqual(df['vout2'].iloc[-1], 2)
        self.assertEqual(df['signal2'].iloc[-1], 3)
        self.assertEqual(df['timestamp'].iloc[-1], pd.Timestamp('2019-03-04T13:08:54'))

        # bwii format (bwii_util)
        testfile = 'tests/bwii_example'
        self.parser.identify_file_source(testfile)
        self.assertTrue(self.parser.load_rawfile(testfile, None, None))
        df = self.parser.data
        self.assertEqual(df['vout1'].iloc[-1], 0.487)
        self.assertEqual(df['signal1'].iloc[-1], 1.76)
        self.assertEqual(df['vout2'].iloc[-1], 0)
        self.assertEqual(df['signal2'].iloc[-1], 0)
        self.assertEqual(df['timestamp'].iloc[-1], pd.Timestamp('2019-03-04 16:37:42'))

        start_time = '2019/01/01 12:00'
        self.assertTrue(self.parser.load_rawfile(testfile, start_time, False))
        df = self.parser.data
        self.assertEqual(df['vout1'].iloc[-1], 0.487)
        self.assertEqual(df['signal1'].iloc[-1], 1.76)
        self.assertEqual(df['vout2'].iloc[-1], 0)
        self.assertEqual(df['signal2'].iloc[-1], 0)
        self.assertEqual(df['timestamp'].iloc[-1], pd.Timestamp('2019-01-01 12:05:00'))

        self.assertTrue(self.parser.load_rawfile(testfile, start_time, True))
        df = self.parser.data
        self.assertEqual(df['vout1'].iloc[-1], 0.487)
        self.assertEqual(df['signal1'].iloc[-1], 1.76)
        self.assertEqual(df['vout2'].iloc[-1], 0)
        self.assertEqual(df['signal2'].iloc[-1], 0)
        self.assertEqual(df['timestamp'].iloc[-1], pd.Timestamp('2019-01-01 12:00:00'))

        # web app file
        testfile = 'tests/web1chan_example'
        self.parser.identify_file_source(testfile)
        self.assertTrue(self.parser.load_rawfile(testfile, None, None))
        df = self.parser.data
        self.assertEqual(df['vout1'].iloc[-1], .5)
        self.assertEqual(df['signal1'].iloc[-1], 0.62)
        self.assertEqual(df['timestamp'].iloc[-1], pd.Timestamp('2019-03-13 14:26:46'))

        # vfp600
        start_time = '2019/01/01 12:00'
        testfile = 'tests/vfp_example'
        self.parser.identify_file_source(testfile)
        self.assertTrue(self.parser.load_rawfile(testfile, start_time, False))
        df = self.parser.data
        self.assertEqual(df['timestamp'].iloc[0], pd.Timestamp(start_time))
        self.assertTrue(self.parser.load_rawfile(testfile, start_time, True))
        df = self.parser.data
        self.assertTrue(df['timestamp'].iloc[0] < pd.Timestamp(start_time))
        ts = [df['timestamp'].iloc[-1], pd.Timestamp(start_time)]
        self.assertTrue(pd.Timedelta(max(ts) - min(ts)).seconds < 1)

        # gamry explain
        start_time = '2018/09/11 12:00'
        testfile = 'tests/gamry_example'
        self.parser.identify_file_source(testfile)
        self.assertTrue(self.parser.load_rawfile(testfile, start_time, False))
        df = self.parser.data
        self.assertEqual(df['timestamp'].iloc[0], pd.Timestamp(start_time))
        self.assertTrue(self.parser.load_rawfile(testfile, start_time, True))
        df = self.parser.data
        self.assertEqual(df['timestamp'].iloc[0], pd.Timestamp(start_time))

        """
        data = 'test'
        header = 'test'
        with patch('psense_common.PSenseParser.read_variable_header_file', return_value=(data, header)):
            self.parser.load_rawfile()

        """
