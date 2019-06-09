import datetime
import re
import warnings
from unittest import TestCase, mock

import settings
from app.parser import ParserGeneric, ParserDCB, ParserOrbit, ParserChannels, ParserRinexChannels


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test


file = 'mock_file.txt'
file_dcb_content = """ DSB  G063 G01           C1C  C1W  2019:001:00000 2019:002:00000 ns                 -1.0300      0.0075
 DSB  G061 G02           C1C  C1W  2019:001:00000 2019:002:00000 ns                  1.2410      0.0090
 DSB  G069 G03           C1C  C1W  2019:001:00000 2019:002:00000 ns                 -1.5680      0.0075
 DSB  G036 G04           C1C  C1W  2019:001:00000 2019:002:00000 ns                  0.4980      0.0080
 DSB  G050 G05           C1C  C1W  2019:001:00000 2019:002:00000 ns                 -1.1500      0.0075
 DSB  G067 G06           C1C  C1W  2019:001:00000 2019:002:00000 ns                 -1.5750      0.0095
 DSB  G048 G07           C1C  C1W  2019:001:00000 2019:002:00000 ns                 -0.5190      0.0075
 DSB  G072 G08           C1C  C1W  2019:001:00000 2019:002:00000 ns                  0.0030      0.0075
 DSB  G068 G09           C1C  C1W  2019:001:00000 2019:002:00000 ns                 -0.3320      0.0075
 DSB  G063 G01           C1W  C2W  2019:001:00000 2019:002:00000 ns                 -7.7630      0.0245
 DSB  G061 G02           C1W  C2W  2019:001:00000 2019:002:00000 ns                  9.4950      0.0290
 DSB  G069 G03           C1W  C2W  2019:001:00000 2019:002:00000 ns                 -5.3420      0.0245
 DSB  G036 G04           C1W  C2W  2019:001:00000 2019:002:00000 ns                 -0.4400      0.0255
 DSB  G050 G05           C1W  C2W  2019:001:00000 2019:002:00000 ns                  3.4680      0.0250
 DSB  G067 G06           C1W  C2W  2019:001:00000 2019:002:00000 ns                 -6.6870      0.0290
 DSB  R730 R01           C1C  C1P  2019:001:00000 2019:002:00000 ns                  0.1110      0.0310
 DSB  R747 R02           C1C  C1P  2019:001:00000 2019:002:00000 ns                  0.0650      0.0310
 DSB  R744 R03           C1C  C1P  2019:001:00000 2019:002:00000 ns                 -0.5350      0.0315
 DSB  R742 R04           C1C  C1P  2019:001:00000 2019:002:00000 ns                 -0.7780      0.0315
 DSB  R730 R01           C1C  C2P  2019:001:00000 2019:002:00000 ns                 -5.5750      0.0470
 DSB  R747 R02           C1C  C2P  2019:001:00000 2019:002:00000 ns                 -0.8890      0.0470
 DSB  R744 R03           C1C  C2P  2019:001:00000 2019:002:00000 ns                  2.5780      0.0470
 DSB  R742 R04           C1C  C2P  2019:001:00000 2019:002:00000 ns                  3.6200      0.0470"""


file_orbit_content = """*  2019  2  5  0  0  0.00000000
PG01  13689.627799 -22555.370301   -650.728111   -157.447757
PG02 -18013.732812   7314.318105 -17409.676649   -131.460067
PG03  12652.724320 -13059.856292 -19370.192481    181.318014
PG04 -10176.146200 -24408.514602  -2461.105501    104.960821
PG05 -26209.469903   2660.615074   4030.157795      1.012843
PG06 -13756.762813  -6015.158863 -21869.348045    282.609321
PG07   2919.356103 -22449.026320  13748.160956     38.646392
PG08  11629.695600  -9835.711776  21792.009163   -131.566330
PG09  -6296.426998 -24285.332009  -8754.193999    462.899520
PG10  18449.923250  11375.863455  15531.091301    123.019872"""


file_channels_content = """|  730  | 2456 | 1/01 |   1  | 14.12.2009 | 30.01.2010 | operating | .......... |
|  747  | 2485 | 1/02 |  -4  | 26.04.2013 | 04.07.2013 | operating | .......... |
|  744  | 2476 | 1/03 |  05  | 04.11.2011 | 08.12.2011 | operating | .......... |
|  742  | 2474 | 1/04 |  06  | 02.10.2011 | 25.10.2011 | operating | .......... |
|  756  | 2527 | 1/05 |  01  | 17.06.2018 | 29.08.2018 | operating | .......... |
|  733  | 2457 | 1/06 |  -4  | 14.12.2009 | 24.01.2010 | operating | .......... |
|  745  | 2477 | 1/07 |  05  | 04.11.2011 | 18.12.2011 | operating | .......... |
|  743  | 2475 | 1/08 |  06  | 14.11.2011 | 25.12.2011 | operating | .......... |
|  702  | 2501 | 2/09 |  -2  | 01.12.2014 | 25.12.2014 | operating | .......... |
|  717  | 2426 | 2/10 |  -7  | 25.12.2006 | 03.04.2007 | operating | .......... |
|  753  | 2516 | 2/11 |  00  | 29.05.2016 | 27.06.2016 | operating | .......... |
|  723  | 2436 | 2/12 |  -1  | 25.12.2007 | 22.01.2008 | operating | .......... |
|  721  | 2434 | 2/13 |  -2  | 25.12.2007 | 08.02.2008 | operating | .......... |
|  752  | 2522 | 2/14 |  -7  | 22.09.2017 | 16.10.2017 | operating | .......... |
|  757  | 2529 | 2/15 |  00  | 03.11.2018 | 27.11.2018 | operating | .......... |
|  736  | 2464 | 2/16 |  -1  | 02.09.2010 | 01.10.2010 | operating | .......... |
|  751  | 2514 | 3/17 |  04  | 07.02.2016 | 24.02.2016 | operating | .......... |
|  754  | 2492 | 3/18 |  -3  | 24.03.2014 | 14.04.2014 | operating | .......... |
|  720  | 2433 | 3/19 |  03  | 26.10.2007 | 25.11.2007 | operating | .......... |
|  719  | 2432 | 3/20 |  02  | 26.10.2007 | 27.11.2007 | operating | .......... |
|  755  | 2500 | 3/21 |  04  | 14.06.2014 | 03.08.2014 | operating | .......... |
|  731  | 2459 | 3/22 |  -3  | 02.03.2010 | 28.03.2010 | operating | .......... |
|  732  | 2460 | 3/23 |  03  | 02.03.2010 | 28.03.2010 | operating | .......... |
|  735  | 2461 | 3/24 |  02  | 02.03.2010 | 28.03.2010 | operating | .......... |"""


conten_rinex = """ 25 R01  1 R02 -4 R03  5 R04  6 R05  1 R06 -4 R07  5 R08  6      R09 -2 R10 -7 R11  0 R12 -1 R13 -2 R14 -7 R15  0 R16 -1      R17  4 R18 -3 R19  3 R20  2 R21  4 R22 -3 R23  3 R24  2      R26 -5 """


class ParserGenericTest(TestCase):
    def setUp(self):
        self.parse = ParserGeneric(file)

    def test_file_name(self):
        """Must return the file name"""
        self.assertEqual(file, self.parse.file)

    @ignore_warnings
    def test_openfile(self):
        """Must test the open file function"""
        with mock.patch('app.parser.open', new=mock.mock_open()) as file:
            self.parse.openfile()
            file.assert_called_once_with(self.parse.file, mode='r')


class ParserDCBTest(TestCase):
    def setUp(self):
        self.dcb = ParserDCB(file)

    def test_regex_DCB1(self):
        """_regex_DCB1 must be equals settings.REGEX_DCB_1"""
        self.assertEqual(self.dcb._regex_DCB1, settings.REGEX_DCB_1)

    def test_regex_DCB2(self):
        """_regex_DCB2 must be equals settings.REGEX_DCB_2"""
        self.assertEqual(self.dcb._regex_DCB2, settings.REGEX_DCB_2)

    def test__default_regex(self):
        """The default regex must return r'{}{}\\s\\s{}{}"""
        self.assertEqual(r'{}{}\s\s{}{}', self.dcb._default_regex)

    def test_obs_mgex2(self):
        """obs_mgex must be equals settings.OBS_MGEX"""
        self.assertEqual(self.dcb.obs_mgex, settings.OBS_MGEX)

    def test_parsed(self):
        """Initial parsed must return {}"""
        self.assertEqual({}, self.dcb.parsed)

    def test_parsed_is_a_dict(self):
        """Parsed must be a dict"""
        self.assertIsInstance(self.dcb.parsed, dict)

    def test_regex(self):
        """Must return the recompile regex"""
        part_one = 'C1C'
        part_two = 'C1W'
        mounted_regex = self.dcb._default_regex.format(self.dcb._regex_DCB1, part_one, part_two, self.dcb._regex_DCB2)
        self.assertEqual(self.dcb.regex('C1C', 'C1W'), re.compile(mounted_regex))

    @ignore_warnings
    def test_parser(self):
        """Must test the parser function and also the find function"""
        with mock.patch('app.parser.open', new=mock.mock_open(read_data=file_dcb_content)) as mock_file:
            self.dcb.parser()
            mock_file.assert_called_with(self.dcb.file, mode='r')

            with self.subTest("The parsed must be the keys C1-P1 and P1-P2"):
                self.assertTrue('C1-P1' in self.dcb.parsed)
                self.assertTrue('P1-P2' in self.dcb.parsed)

            with self.subTest("The parsed key C1-P1 must have length 13"):
                self.assertEqual(0, len(self.dcb.parsed['C1-P1']))

            with self.subTest("The parsed key P1-P2 must have length 6"):
                self.assertEqual(0, len(self.dcb.parsed['P1-P2']))


class ParserOrbitTest(TestCase):
    def setUp(self):
        self.orbit = ParserOrbit(file)

    def test_file_name(self):
        """Must return the file name"""
        self.assertEqual(file, self.orbit.file)

    def test_date(self):
        """_date must return empty"""
        self.assertEqual('', self.orbit._date)

    def test_parsed(self):
        """Initial parsed must return {}"""
        self.assertEqual({}, self.orbit.parsed)

    @ignore_warnings
    def test_orbit_openfile(self):
        """Must test the open file function"""
        with mock.patch('app.parser.open', new=mock.mock_open()) as file:
            self.orbit.openfile()
            file.assert_called_once_with(self.orbit.file, mode='r')

    @ignore_warnings
    def test_parser(self):
        """Must test the parser function and also the find function"""
        with mock.patch('app.parser.open', new=mock.mock_open(read_data=file_orbit_content)) as mock_file:
            self.orbit.parser()
            mock_file.assert_called_with(self.orbit.file, mode='r')
            with self.subTest("Must return the length of parsed"):
                self.assertEqual(10, len(self.orbit.parsed))

            with self.subTest("Parsed must have the G01 key"):
                self.assertTrue('G01' in self.orbit.parsed)

            with self.subTest("The G01 key must be a list"):
                self.assertIsInstance(self.orbit.parsed['G01'], list)

            with self.subTest("The elements inside of G01 list must be a dict"):
                self.assertIsInstance(self.orbit.parsed['G01'][0], dict)

            with self.subTest("G01 lists must have 4 keys (date, x, y, z) "):
                self.assertEqual(4, len(self.orbit.parsed['G01'][0]))
                self.assertTrue('date' in self.orbit.parsed['G01'][0])
                self.assertTrue('x' in self.orbit.parsed['G01'][0])
                self.assertTrue('y' in self.orbit.parsed['G01'][0])
                self.assertTrue('z' in self.orbit.parsed['G01'][0])

            with self.subTest("The key date in G01 elements must be a datetime"):
                self.assertIsInstance(self.orbit.parsed['G01'][0]['date'], datetime.datetime)


class ParserChannelsTest(TestCase):
    def setUp(self):
        self.channels = ParserChannels(file)

    def test_regex(self):
        """The _regex must be equals settings.REGEX_GLONASS_CHANNEL"""
        self.assertEqual(self.channels._regex, settings.REGEX_GLONASS_CHANNEL)

    def test_parsed(self):
        """Initial parsed must return {}"""
        self.assertEqual({}, self.channels.parsed)

    def test_parsed_is_a_dict(self):
        """Parsed must be a dict"""
        self.assertEqual(self.channels.pattern, re.compile(self.channels._regex))

    @ignore_warnings
    def test_parser(self):
        """Must test the parser function and also the find function"""
        with mock.patch('app.parser.open', new=mock.mock_open(read_data=file_channels_content)) as mock_file:
            self.channels.parser()
            mock_file.assert_called_with(self.channels.file, mode='r')
            with self.subTest("Must return the length of parsed"):
                self.assertEqual(24, len(self.channels.parsed))

            with self.subTest("Must test the result for random keys in dict parsed"):
                self.assertEqual(self.channels.parsed['01'], [1602562500.0, 1246437500.0, 1602562503.3798902, 1602562494.6544268])
                self.assertEqual(self.channels.parsed['10'], [1598062500.0, 1242937500.0, 1598062503.3682156, 1598062494.6694372])
                self.assertEqual(self.channels.parsed['17'], [1604250000.0, 1247750000.0, 1604250003.3842683, 1604249994.648798])


class ParserRinexChannelsTest(TestCase):
    def setUp(self):
        self.rinex = ParserRinexChannels(conten_rinex)

    def test_regex(self):
        """The _regex must be equals settings.REGEX_GLONASS_CHANNEL_RINEX"""
        self.assertEqual(self.rinex._regex, settings.REGEX_GLONASS_CHANNEL_RINEX)

    def test_A(self):
        """The A must be equals settings.A"""
        self.assertEqual(self.rinex.A, settings.A)

    def test_TECU(self):
        """The TECU must be equals settings.TECU"""
        self.assertEqual(self.rinex.TECU, settings.TECU)

    def test_parsed(self):
        """Initial parsed must return {}"""
        self.assertEqual({}, self.rinex.parsed)

    def test_parser(self):
        """Must test the parser function and also the find function"""
        self.rinex.find()
        with self.subTest("Must return the length of parsed"):
            self.assertEqual(25, len(self.rinex.parsed))

        with self.subTest("Must test the result by PRN"):
            self.assertEqual(self.rinex.parsed['01'], [1602562500.0, 1246437500.0, 1602562503.3798902, 1602562494.6544268])
            self.assertEqual(self.rinex.parsed['10'], [1598062500.0, 1242937500.0, 1598062503.3682156, 1598062494.6694372])
            self.assertEqual(self.rinex.parsed['17'], [1604250000.0, 1247750000.0, 1604250003.3842683, 1604249994.648798])
