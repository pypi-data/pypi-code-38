# Compatibility imports
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

# System imports
import time
import unittest

# Local imports
from htpio import socketio
from htpio.exceptions import PinLockedByOtherProcess

HOST = '192.168.199.31'
PORT = 8888


class TestSocketIO(unittest.TestCase):
    """
    Unit test class socket io control [htpio.socketio]
    """

    def test_socketio(self):

        # Create socketio sessions
        r1 = socketio.RaspberryPi(host=HOST)
        r2 = socketio.RaspberryPi(host=HOST)

        # Lock pin from first socketio
        r1.lock(14)
        self.assertTrue(r1.islocked(14))

        # Check if pin can be unlocked by second socketio
        raised = False
        try:
            r2.unlock(14)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, True)

        # Configure pin from first socketio
        r1.configure(14, socketio.RaspberryPi.OUTPUT)
        self.assertTrue(r1.isconfigured(14))

        # Check if pin can be configured from second socketio
        raised = False
        try:
            r2.configure(14, socketio.RaspberryPi.OUTPUT)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, True)

        # Set value of pin from first socketio
        r1.set(14, 1)
        self.assertEqual(r1.get(14), 1)

        # Check if we can set the value from the second socketio
        raised = False
        try:
            r2.set(14, 0)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, True)

        time.sleep(1)

        # Unlock pin from first socketio
        r1.unlock(14)
        self.assertFalse(r1.islocked(14))

        # Check if we can set a new value from the second socketio
        raised = False
        try:
            r2.set(14, 0)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, False)

        # Deconfigure pin from first socketio
        r1.deconfigure(14)
        self.assertFalse(r1.isconfigured(14))

        # Check if we can configure/set pin from second socketio
        raised = False
        try:
            r2.configure(14, socketio.RaspberryPi.OUTPUT)
            r2.set(14, 1)
        except PinLockedByOtherProcess:
            raised = True
        finally:
            self.assertEqual(raised, False)
            r2.set(14, 0)
            r2.deconfigure(14)

        # Cleanup
        r1.logout()
        r2.logout()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_socketio']
    unittest.main()
