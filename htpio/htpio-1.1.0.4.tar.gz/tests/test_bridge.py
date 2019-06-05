# Compatibility imports
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

# System imports
import time
import unittest

# Local imports
from htpio import bridge
from htpio import telnetio
from htpio import socketio
from htpio.exceptions import PinLockedByOtherProcess

HOST = '192.168.199.31'


class TestBridgeIO(unittest.TestCase):
    """
    Unit test class bridge pattern [htpio.bridge]
    """

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    #  test_bridge_telnetio : Control IO with telnetio initialized using bridge
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    def test_bridge_telnetio(self):
        # Initialize bridge and protocol library
        a = bridge.RemoteAccess(telnetio.RaspberryPi(HOST))
        b = bridge.RemoteAccess(socketio.RaspberryPi(HOST))

        # Test/Assert 01 : Lock pin
        a.lock(14)
        self.assertTrue(b.islocked(14))

        # Test/Assert 02 : Configure pin
        a.configure(14, a.OUTPUT)
        self.assertTrue(b.isconfigured(14))

        # Test/Assert 03 : Set pin to ON
        a.set(14, 1)
        self.assertEqual(b.get(14), 1)

        time.sleep(1)

        # Test/Assert 04 : Set pin to OFF
        a.set(14, 0)
        self.assertEqual(b.get(14), 0)

        # Test/Assert 05 : Unlock pin
        a.unlock(14)
        self.assertFalse(b.islocked(14))

        # Test/Assert 06 : Cleanup configuration
        a.deconfigure(14)
        self.assertFalse(b.isconfigured(14))

        # Test/Assert 07 : Close connection
        a.logout()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
