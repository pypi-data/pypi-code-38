import unittest
from ttlab.frames import Frames


class FARTInfoReaderTestCases(unittest.TestCase):

    class FARTInfoExample:
        filename = 'tests/mock_data/17-Apr-2019_12-41-02.txt'
        info = {
            'x pixels': 30,
            'y pixels': 2160,
            'exposure time': 0.020003,
            'number of accumulations': 10,
            'vertical binning': 1,
            'horisontal binning': 1,
            'pixel readout rate': '280 MHz',
            'overlap readout': True,
            'spurious noise filter': True,
            'cycle mode': 'Continuous',
            'trigger mode': 'Internal',
            'simple pre amp gain control': '16-bit (low noise & high well capacity)',
            'pixel encoding': 'Mono32',
            'fan speed': 'Off',
            'electronic shuttering mode': 'Rolling',
            'fast AOI frame rate enabled': True
        }

    def test_read_fart_info(self):
        result = Frames(filename=self.FARTInfoExample.filename).measurement_info
        self.assertEqual(self.FARTInfoExample.info['x pixels'], result['x pixels'])
        self.assertEqual(self.FARTInfoExample.info['y pixels'], result['y pixels'])
        self.assertEqual(self.FARTInfoExample.info['exposure time'], result['exposure time'])
        self.assertEqual(self.FARTInfoExample.info['number of accumulations'], result['number of accumulations'])
        self.assertEqual(self.FARTInfoExample.info['vertical binning'], result['vertical binning'])
        self.assertEqual(self.FARTInfoExample.info['horisontal binning'], result['horisontal binning'])
        self.assertEqual(self.FARTInfoExample.info['pixel readout rate'], result['pixel readout rate'])
        self.assertEqual(self.FARTInfoExample.info['cycle mode'], result['cycle mode'])
        self.assertEqual(self.FARTInfoExample.info['spurious noise filter'], result['spurious noise filter'])
        self.assertEqual(self.FARTInfoExample.info['overlap readout'], result['overlap readout'])
        self.assertEqual(self.FARTInfoExample.info['trigger mode'], result['trigger mode'])
        self.assertEqual(self.FARTInfoExample.info['simple pre amp gain control'], result['simple pre amp gain control'])
        self.assertEqual(self.FARTInfoExample.info['pixel encoding'], result['pixel encoding'])
        self.assertEqual(self.FARTInfoExample.info['fan speed'], result['fan speed'])
        self.assertEqual(self.FARTInfoExample.info['electronic shuttering mode'], result['electronic shuttering mode'])
        self.assertEqual(self.FARTInfoExample.info['fast AOI frame rate enabled'], result['fast AOI frame rate enabled'])