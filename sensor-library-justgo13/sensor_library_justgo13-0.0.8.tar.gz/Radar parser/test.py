import unittest
import X4_parser as X4
import TI_parser as TI


class TestParser(unittest.TestCase):

    def test_iq(self):
        """
        Method to test if .dat binary file was converted successfully to .csv file with in-phase and quadrature
        components together.

        :return:

        Tells user if binary file was correctly converted to csv file.
        """
        file_iq = X4.iq_data('X4data.dat','X4iq')
        self.assertEqual(file_iq, 'converted')

    def test_raw(self):
        """
        Method to test if .dat binary file was converted successfully to .csv file with in-phase and quadrature
        component separated.

        :return:

        Tells user if binary file was correctly converted to csv file.
        """
        file_raw = X4.raw_data('X4data.dat','X4raw')
        self.assertEqual(file_raw, 'converted')

    def test_TI(self):
        """
        Method to test if .bin binary file was converted successfully to .csv file with iq data put together.

        :return:

        Tells user if binary file was correctly converted to csv file.
        """

        file_TI = TI.readTIdata('TIdata.bin','TIiq')
        self.assertEqual(file_TI,'converted')

if __name__ == '__main__':
    unittest.main()
