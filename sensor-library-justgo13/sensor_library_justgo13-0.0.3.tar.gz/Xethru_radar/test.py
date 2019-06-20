import unittest
import X4_parser as X4
import TI_parser as TI


class TestParser(unittest.TestCase):

    def test_iq(self):
        """
        Method to test if .dat binary file was converted successfully to .csv file with in-phase and quadrature
        components together.

        :return:

        converted
        """
        file_iq = X4.iq_data('data.dat')
        self.asserEqual(file_iq,'converted')

    def test_raw(self):
        """
        Method to test if .dat binary file was converted successfully to .csv file with in-phase and quadrature
        component separated.

        :return:

        converted
        """
        file_raw = X4.raw_data('data.dat')
        self.asserEqual(file_raw,'converted')

    def test_TI(self):
        """
        Method to test if .bin binary file was converted successfully to .csv file with iq data put together.

        :return:

        converted
        """

        file_TI = TI.readTIdata('data.dat')
        self.assertEqual(file_TI,'converted')

if __name__ == '__main__':
    unittest.main()
