# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# System imports
import time
import unittest

# Local imports
from htpio import telnetio
from htpio.exceptions import PinLockedByOtherProcess


HOST = '192.168.199.31'
PORT = 23


class TestTelnetIO(unittest.TestCase):
    """
    Unit test class telnet io control [htpio.telnetio]
    """

    def test_telnetio(self):
        # TelnetIO functionality
        r1 = telnetio.RaspberryPi(host=HOST)

        r2 = telnetio.RaspberryPi(host=HOST)

        # Lock pin from first telnet session
        r1.lock(14)
        self.assertTrue(r1.islocked(14))

        # Check if pin can be unlocked by second telnet session
        raised = False
        try:
            r2.unlock(14)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, True)

        # Configure pin from first telnet session
        r1.configure(14, telnetio.RaspberryPi.OUTPUT)
        self.assertTrue(r1.isconfigured(14))

        # Check if pin can be configured by second telnet session
        raised = False
        try:
            r2.configure(14, telnetio.RaspberryPi.OUTPUT)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, True)

        # Set value from first telnet session
        r1.set(14, 1)
        self.assertEqual(r1.get(14), 1)

        # Check if we can set the value from the second telnet session
        raised = False
        try:
            r2.set(14, 0)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, True)

        time.sleep(1)

        # Unlock pin from first telnet session
        r1.unlock(14)
        self.assertFalse(r1.islocked(14))

        # Check if we can set a new value from the second telnet session
        raised = False
        try:
            r2.set(14, 0)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, False)

        # Deconfigure pin from first telnet session
        r1.deconfigure(14)
        self.assertFalse(r1.isconfigured(14))

        # Check if we can configure/set pin from second telnet session
        raised = False
        try:
            r2.configure(14, telnetio.RaspberryPi.OUTPUT)
            r2.set(14, 1)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, False)
            r2.set(14, 0)
            r2.deconfigure(14)

        # Logout
        r1.logout()
        r2.logout()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
