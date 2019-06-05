# Copyright (c) Hilscher GmbH. All Rights Reserved.
#
# $Author: bgeorgiev $
# $Date: 2019-05-16 11:34:02 +0300 (Thu, 16 May 2019) $
# $Revision: 654 $


"""
This is a socket i/o control module wrapping the python pigpio client.
PIGPIO is a client/server library using sockets for remote control of
the general purpose input outputs(GPIO).


*** Example: ***

```python

import htpio.socketio as socketio

r = socketio.RaspberryPi(host = '192.168.199.31',
                         port = 8888)

try:
    r.lock(14)
except:
    r.logout()
    raise

r.configure(14, socketio.RaspberryPi.OUTPUT)
r.set(14, 1)

print(r.get(14))

r.unlock(14)
r.deconfigure(14)
```

"""

# Compatibility imports
from __future__ import unicode_literals
from __future__ import absolute_import

# Third party imports
import pigpio

# Local imports
from .exceptions import PinLockedByOtherProcess, CannotConnectToTarget
from .bridge import Device


"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DEVICE CLASSES : RaspberryPi, OrangePi, Arduino, etc.
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class RaspberryPi(pigpio.pi, Device):

    """
    This class allows users to connect and control the GPIO
    on a Raspberry remotely by using and extending the pigpio library.

    ## Configuration

    Enable Remote GPIO

        sudo raspi-config
        Menu : Interfacing Options -> Remote GPIO

    Enable pigpiod to start on boot

        sudo systemctl enable pigpiod


    ## Class attributes

        LOCK_DIR        : Location of lock files (ramdisk)
        MAX_GPIO        : Maximum number of gpio locks ( from 0 .. MAX)
        INPUT           : GPIO is digital input
        OUTPUT          : GPIO is digital output
        EOF             : End of file


    ## Instance attributes

        host            : ip v4 address
        port            : port (from 0 to 65535)

    ## Public methods

        islocked(gpio)              : Check if the gpio is locked
        lock(gpio)                  : Locks the gpio
        unlock(gpio)                : Unlocks the gpio
        isconfigured(gpio)          : Checks if the gpio is configured
        configure(gpio, direction)  : Configures the gpio with direction
        deconfigure(gpio)           : Restores the default configuration
        get(gpio)                   : Reads the gpio status
        set(gpio, value)            : Writes new value to gpio
        login()                     : Registers to the remote system
        logout()                    : Unregisters from the remote system
        reset()                     : Deletes all configuration data

    """

    MAX_GPIO = 128
    """ Maximum number of GPIOs """

    INPUT = pigpio.INPUT
    """ Signal direction is INPUT """

    OUTPUT = pigpio.OUTPUT
    """ Signal direction is OUTPUT """

    LOCKDIR = "/tmp/htp/locks"
    """ Lock files directory """

    EOF = "\n"
    """ Symbol for end of transmission """

    def __init__(self, host=None, port=8888):
        """
        ## Constructor

        When called with host address, the constructor creates
        a telnet connection and performs automatic login (default=8888).

        ```python
        import htpio.socketio as socketio

        t = socketio.RaspberryPi('192.168.199.31')
        ```

        """

        pigpio.pi.__init__(self, host, port)

        self._host = host
        self._port = port
        self._session = None
        self._iotag = "gpio"
        self._lockdir = RaspberryPi.LOCKDIR

        if host is not None:
            self.login()

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  islocked : Check if pin is locked and returns the owner
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def islocked(self, pin):
        """
        Opens the gpio lock file and checks it size. If the size is more than
        zero then the gpio is considered to be locked by another process.

        *** Example: ***
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')
        led.lock(14)
        if led.islocked(14) :
            print("LED is locked!!!")
        ...
        ```
        """

        # Consistent directory name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # Generate lock file name
        iotag = self._iotag + str(pin)
        lockfile = (self._lockdir + iotag)

        # Prepare mode
        mode = pigpio.FILE_READ
        h = self.file_open(lockfile.encode('ascii'), mode)

        # Read file
        (size, data) = self.file_read(h, 100)

        # Evaluate result
        if size > 0:

            # Someone is locking the file
            result = data.decode()
            result = result.replace(self.EOF, "")

        else:

            # Nobody is locking the file
            result = None

        self.file_close(h)

        return result

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  lock : Open the lock file and write this instance socket parameters
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def lock(self, pin):
        """
        Lock the given pin by creating a lock file and writing the current
        session id into it.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')
        led.lock(14)
        ...
        ```
        """

        # Consistent directory name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # Generate lock file name
        iotag = self._iotag + str(pin)
        lockfile = self._lockdir + iotag

        # Check ownership and lock
        lock_owner = self.islocked(pin)

        if lock_owner is not None:
            raise PinLockedByOtherProcess(lock_owner.encode('ascii'),
                                          self._session)
        else:

            # Prepare mode
            mode = pigpio.FILE_WRITE | pigpio.FILE_CREATE
            h = self.file_open(lockfile.encode('ascii'), mode)

            # Write content
            content = (self._session + RaspberryPi.EOF).encode('ascii')
            self.file_write(h, content)

            # Close file
            self.file_close(h)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  unlock : Opens the corresponding file and erases the content
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def unlock(self, pin):
        """
        Unlock the pin by truncating the size of the lock file to zero.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')
        led.unlock(14)
        ...
        ```

        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        iotag = self._iotag + str(pin)
        lockfile = self._lockdir + iotag

        h = self.file_open(lockfile.encode('ascii'),
                           pigpio.FILE_READ |
                           pigpio.FILE_TRUNC)

        self.file_close(h)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # isconfigured : Check if the pin is configured (mode <> default)
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def isconfigured(self, pin):
        """
        Check if gpio is configured by comparing the current direction
        configuration with the default one (INPUT).

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.configure(14, socketio.RaspberryPi.OUTPUT)
        if led.isconfigured(14):
            print("LED is configured!!!")
        ...
        ```
        """

        return self.get_mode(pin)

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  configure : Configures pin mode using pigpio 
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def configure(self, pin, direction):
        """
        Configures the gpio for input or output operation.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.configure(14, socketio.RaspberryPi.OUTPUT)
        ...
        ```
        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        self.set_mode(pin, direction)

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  cleanup : Resets pin configuration to the default value (INPUT)
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def deconfigure(self, pin):
        """
        Removes the gpio configuration.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.deconfigure(14)
        ...
        ```
        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        self.set(pin, 0)
        self.set_mode(pin, pigpio.INPUT)

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  get : Reads the value of the pin using pigpio
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    """

    def get(self, pin):
        """
        Reads the value of the gpio.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.get(14)
        ...
        ```
        """

        return self.read(pin)

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  set : Writes to the pin using pigpio
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    """

    def set(self, pin, value):
        """
        Writes the value to the gpio.

        *** Example: ***
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.configure(14, socketio.RaspberryPi.OUTPUT)
        led.set(14, 1)
        ...
        ```
        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        self.write(pin, value)

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  login : Check for connectivity and create lock files
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def login(self):
        """
        Registers device for use with target device by checking for
        an established connection and creating all gpio lock files.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi()
        led.host = '192.168.199.31'
        led.port = 8888
        led.login()
        ...
        ```
        """

        # Check if socket connection is up
        if not self.connected:
            raise CannotConnectToTarget

        # Check if device is already registered
        if not self._session:
            self._session = self.__session()
            self.__populate()

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  logout : Close socket
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def logout(self):
        """
        Unregisters device from remote device.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.logout()

        ...
        ```
        """

        self.stop()

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  reset : Deletes all coockies
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def reset(self, pin):
        """
        Deletes the content of all generated lock files.

        ***Example***:
        ```python
        import htpio.socketio as socketio

        led = socketio.RaspberryPi('192.168.199.31')

        led.reset(14)

        ...
        ```
        """

        # Consistent directory name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # Generate lock file name
        iotag = self._iotag + str(pin)
        lockfile = self._lockdir + iotag

        h = self.file_open(file_name=lockfile.encode('ascii'),
                           file_mode=pigpio.FILE_READ | pigpio.FILE_TRUNC)

        self.file_close(h)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  session : Retrieves connection data and generates a lock identification
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __session(self):
        """
        Gets the socket data for this connection and converts the to one
        unique identification number. This ID is used to lock gpios.
        """

        mysocket = self.sl.s
        mysocket = mysocket.getsockname()
        result = '.'.join(map(str, mysocket))
        result = result.replace(".", "")

        return result

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  locklist : retries all gpios currently locked by other processes
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __locklist(self):
        """
        Gets a listing of all lock files in the lock directory.
        """

        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        lockdir = self._lockdir + "*"

        # Function returns number of bytes(r) and a byte array(r2)
        size, data = self.file_list(lockdir.encode('ascii'))

        result = []
        if size > 0:
            data = data.decode()
            data = data.split(RaspberryPi.EOF)

            for element in data[:-1]:
                result.append(element)

        return result

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  populate : generate GPIO lock files from 0 to MAX_GPIO
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __populate(self):
        """ Creates all lock files in the lock directory. """

        # Consistent directory name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # Generate lock files
        for gpio in range(RaspberryPi.MAX_GPIO):
            iotag = self._iotag + str(gpio)
            lockfile = self._lockdir + iotag

            h = self.file_open(file_name=lockfile.encode('ascii'),
                               file_mode=pigpio.FILE_WRITE | pigpio.FILE_CREATE)

            self.file_close(h)

        return 0
