import unittest
import Xethru_radar.X4_parser as parser


class TestParser(unittest.TestCase):

    def test_iq(self):
        """
        Method to test if .dat binary file was converted successfully to .csv file with in-phase and quadrature
        components together.

        :return:

        1
        """
        file_iq = parser.iq_data('X4data.dat')
        self.asserEqual(file_iq,1)

    def test_raw(self):
        """
        Method to test if .dat binary file was converted successfully to .csv file with in-phase and quadrature
        component separated.

        :return:

        1
        """
        file_raw = parser.raw_data('X4data.dat')
        self.asserEqual(file_raw,1)


if __name__ == '__main__':
    unittest.main()