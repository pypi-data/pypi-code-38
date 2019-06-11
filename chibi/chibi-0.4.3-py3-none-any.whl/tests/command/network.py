from chibi.command.network import iwconfig, Interfaces, Interface
from chibi.atlas import Chibi_atlas
from unittest.mock import patch
from unittest import TestCase


class Test_iwconfig( TestCase ):
    def setUp( self ):
        self.iwconfig_raw_output = (
            'wlan0     IEEE 802.11bgn  ESSID:"TP-LINK_E758"  \n          '
            'Mode:Managed  Frequency:2.417 GHz  '
            'Access Point: 84:16:F9:EB:E7:58 '
            '  \n          Bit Rate=72 Mb/s   Tx-Power=1496 dBm   \n          '
            'Retry short limit:7   RTS thr:off   Fragment thr:off\n          '
            'Encryption key:off\n          Power Management:on\n          '
            'Link Quality=66/70  Signal level=-44 dBm  \n          '
            'Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0\n        '
            '  Tx excessive retries:0  Invalid misc:0   Missed beacon:0\n\n'
            'wlan1mon  IEEE 802.11bgn  Mode:Monitor  Frequency:2.457 GHz  '
            'Tx-Power=20 dBm   \n          Retry short limit:7   RTS thr:off   '
            'Fragment thr:off\n          Power Management:off\n          \n',
            None, 0 )
        self.expected_iwconfig_result = {
            'wlan0': {
                'access_point': ' 84:16:f9:eb:e7:58', 'bit_rate': '72 mb/s',
                'fragment_thr': 'off', 'retry_short_limit': '7',
                'frequency': '2.417 ghz', 'rts_thr': 'off',
                'tx_excessive_retries': '0', 'rx_invalid_crypt': '0',
                'link_quality': '66/70', 'essid': '"tp-link_e758"',
                'mode': 'managed', 'rx_invalid_nwid': '0',
                'missed_beacon': '0', 'rx_invalid_frag': '0',
                'ieee': '802.11bgn', 'tx-power': '1496 dbm',
                'power_management': 'on', 'encryption_key': 'off',
                'signal_level': '-44 dbm', 'invalid_misc': '0'
            },
            'wlan1mon': {
                'fragment_thr': 'off', 'ieee': '802.11bgn',
                'retry_short_limit': '7', 'power_management': 'off',
                'frequency': '2.457 ghz', 'rts_thr': 'off',
                'tx-power': '20 dbm', 'mode': 'monitor'
            }
        }
        self.expected_interfaces = [ 'wlan0', 'wlan1mon', ]

    def iwconfig_with_patch( self ):
        with patch( 'chibi.command.network.command' ) as command_mock:
            command_mock.return_value = self.iwconfig_raw_output
            result = iwconfig()
        return result

    def test_result_contain_the_container_interfaces( self ):
        result = self.iwconfig_with_patch()
        self.assertIsInstance( result, Interfaces )

    def test_result_should_have_the_expected_interfaces( self ):
        result = self.iwconfig_with_patch()
        self.assertCountEqual(
            result.interfaces.keys(), self.expected_interfaces )

    def test_result_should_have_wlan0( self ):
        result = self.iwconfig_with_patch()
        self.assertIn( 'wlan0', result.interfaces )
        self.assertIsInstance( result.interfaces.wlan0, Interface )

    def test_result_should_be_a_class_for_interfaces( self ):
        result = self.iwconfig_with_patch()
        self.assertIsInstance( result.interfaces, Chibi_atlas )
