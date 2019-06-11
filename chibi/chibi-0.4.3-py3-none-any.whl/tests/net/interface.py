from unittest import TestCase
from chibi.snippet.iter import cut_until, chunk_each
from chibi.command.network import ip_addr
from chibi.net.network.interface import Network


class Test_load_interface_from_ip( TestCase ):
    def setUp( self ):
        self.example = (
            '1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue '
            'state UNKNOWN group default qlen 1000\n    '
            'link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n    '
            'inet 127.0.0.1/8 scope host lo\n       '
            'valid_lft forever preferred_lft forever\n    '
            'inet6 ::1/128 scope host \n       '
            'valid_lft forever preferred_lft forever\n2: enp0s25: '
            '<NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel '
            'state DOWN group default qlen 1000\n    '
            'link/ether 00:21:cc:65:7a:0a brd ff:ff:ff:ff:ff:ff\n3: '
            'wlp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq '
            'state UP group default qlen 1000\n    '
            'link/ether 74:e5:0b:03:07:30 brd ff:ff:ff:ff:ff:ff\n   '
            ' inet 10.106.70.59/21 brd 10.106.71.255 scope global dynamic '
            'noprefixroute wlp3s0\n       valid_lft 1889sec preferred_lft '
            '1889sec\n    inet6 fe80::727a:540:5d5e:2b55/64 scope '
            'link noprefixroute \n       valid_lft forever preferred_lft '
            'forever\n4: vboxnet0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500'
            'qdisc fq_codel state UP group default qlen 1000\n    '
            'link/ether 0a:00:27:00:00:00 brd ff:ff:ff:ff:ff:ff\n    '
            'inet 192.168.56.1/24 brd 192.168.56.255 scope global vboxnet0'
            '\n       valid_lft forever preferred_lft forever\n    '
            'inet6 fe80::800:27ff:fe00:0/64 scope link \n       '
            'valid_lft forever preferred_lft forever\n5: vboxnet1:'
            ' <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN '
            'group default qlen 1000\n    '
            'link/ether 0a:00:27:00:00:01 brd ff:ff:ff:ff:ff:ff\n'
        )


    def test_should_return_4_interfaces( self ):
        result = Network.load_from_string( self.example )
        self.assertIn( 'lo', result )
        self.assertIn( 'vboxnet1', result )
        self.assertIn( 'wlp3s0', result )
        self.assertIn( 'enp0s25', result )
        self.assertIn( 'vboxnet1', result )

    def test_the_ip_should_be_the_expected( self ):
        result = Network.load_from_string( self.example )
        self.assertEqual( result.lo.ip_v4, '127.0.0.1/8' )
        self.assertEqual( result.enp0s25.ip_v4, None )
        self.assertEqual( result.wlp3s0.ip_v4, '10.106.70.59/21' )
        self.assertEqual( result.vboxnet0.ip_v4, '192.168.56.1/24' )
        self.assertEqual( result.vboxnet1.ip_v4, None )
