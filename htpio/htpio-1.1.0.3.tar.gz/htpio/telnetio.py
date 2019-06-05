# Copyright (c) Hilscher GmbH. All Rights Reserved.
#
# $Author: bgeorgiev $
# $Date: 2019-05-16 11:34:02 +0300 (Thu, 16 May 2019) $
# $Revision: 654 $


"""
This is a telnet client i/o control module.
Telnet is a client/server text-oriented communication protocol using a virtual
terminal connection and operates over TCP. It provides a command-line interface
to the operating system on a remote host.

*** Example: ***

```python

import htpio.telnetio as telnetio

r = telnetio.RaspberryPi(host = '192.168.199.31',
                         port = 23,
                         user = 'pi',
                         password = 'raspberry')

try:
    r.lock(14)
except:
    r.logout()
    raise

r.configure(14, telnetio.RaspberryPi.OUTPUT)
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
from telnetlib import Telnet

# Local imports
from .bridge import Device
from .exceptions import PinLockedByOtherProcess
from .exceptions import InvalidLoginDetails
from .exceptions import CannotMountRamDisk
from .exceptions import CannotCreateLockDirectory


"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DEVICE CLASSES : RaspberryPi, OrangePi, Arduino, etc.
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class RaspberryPi(Telnet, Device):
    """
    RaspberryPi telnet remote i/o access class.
    
    This class provides basic functionality for controlling the GPIO by
    using a remote telnet session and sending commands to the operating system.

    ## Configuration

    The user should be part of the sudo and gpio group and the visudo file
    should be configured for no password prompt when using the sudo. This is
    accomplished by executing the following commands :

    ```
    sudo adduser htp
    sudo usermod -a -G gpio htp                
    sudo usermod -a -G sudo htp

    sudo visudo                
        (add line) htp     ALL=(ALL) NOPASSWD: ALL            
        (add line) %gpio   ALL=(ALL) NOPASSWD: ALL

    ```

    ## Class attributes

        LOCK_DIR         Location of lock files (ramdisk)
        MAX_GPIO         Maximum number of gpio locks ( from 0 .. MAX)
        INPUT            GPIO is digital input
        OUTPUT           GPIO is digital output
        EOF              End of file


    ## Instance attributes

        host            : ip v4 address
        port            : port (from 0 to 65535)
        user            : user
        password        : user password
        login_prompt    : token to detect when login is expected
        password_prompt : token to detect when password is expected
        shell_prompt    : token to detect return after command execution
        timeout         : timeout time in case of connectivity problems

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

    LOCKDIR = "/tmp/htp/locks"
    """ Directory containing the lock files """

    RAMDISK = "htp_lockdir"
    """ Label for the ramdisk mounted on the lock directory """

    MAX_GPIO = 128
    """ Maximum number of gpio lock files """

    INPUT = 0
    """ Direction of gpio is input """

    OUTPUT = 1
    """ Direction of gpio is output """

    EOF = "\r\n"
    """ Character used to mark end of line transmission"""

    def __init__(
            self,
            host=None,
            port=23,
            user='htp',
            password='sokotnar',
            login_prompt="login:",
            password_prompt="Password:",
            shell_prompt="$",
            timeout=20
    ):

        """
        ## Constructor

        When called with host address, the constructor creates
        a telnet connection and performs automatic login:

        ```python
        import htpio.telnetio as telnetio

        t = telnetio.RaspberryPi('192.168.199.31')
        ```

        When called without host address, the constructor creates
        an unconnected instance. In this case the object might be
        configured by using the instance attributes:

        ```python
        import htpio.telnetio as telnetio

        t = telnetio.RaspberryPi()

        t.host = '192.168.199.31'
        t.port = 23
        t.user = 'user'
        t.password = 'password'
        t.login_prompt = 'login:'
        t.password_prompt = 'Password:'
        t.shell_prompt = '$'
        t.timeout = 20
        ```

        After the configuration above the user is required to use the
        following statements:

        ```python
        t.open(host, port)
        t.login()
        ```

        """

        Telnet.__init__(self, host, port)

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout

        self.login_prompt = login_prompt.encode('ascii')
        self.password_prompt = password_prompt.encode('ascii')
        self.shell_prompt = shell_prompt.encode('ascii')

        self._session = None
        self._locklist = None
        self._iotag = "gpio"

        self._lockdir = self.LOCKDIR
        self._ramdisk = self.RAMDISK

        if host is not None:
            self.login()

    def __del__(self):
        """ # Destructor -- close telnet connection"""

        self.close()

    """
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  islocked : Check if pin is locked and returns the owner
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    def islocked(self, pin):
        """
        Check if pin is already locked by an object of this class and returns
        the identification number of the locking process.

        *** Shell: ***
        ```
        sudo cat /tmp/htp/locks/gpio14
        ```

        *** Example: ***
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')
        led.lock(14)
        if led.islocked(14) :
            print("LED is locked!!!")
        ...
        ```
        """

        # Consistent folder name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # GPIO lock file
        iotag = self._iotag + str(pin)
        lockfile = (self._lockdir + iotag)

        # Command to open file
        command = "sudo cat " + \
                  lockfile + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush command echo
        self.read_until(self.EOF.encode('ascii'), self.timeout)

        # Read command result
        result = self.read_until(self.shell_prompt, self.timeout)
        result = bytes(result).decode()
        result = result.split()
        result = result[0].replace(self.EOF, "")

        # Verify result (should be a number)
        try:
            int(result)
        except ValueError:
            result = None

        return result

    """
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  lock : Checks if pin is used by other processes and creates a lock file
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    def lock(self, pin):
        """
        Throws an exception <b>PinLockedByOtherProcess</b> or opens the gpio
        lock file and writes the session id in it.

        ***Shell***:
        ```shell
        echo 1921681993055555 | sudo tee /tmp/htp/gpio14
        ```

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')
        led.lock(14)
        ...
        ```
        """

        # Consistent folder name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # GPIO lock file
        iotag = self._iotag + str(pin)
        lockfile = self._lockdir + iotag

        # Create lock file
        lock_owner = self.islocked(pin)
        if lock_owner is not None:
            raise PinLockedByOtherProcess(lock_owner, self._session)
        else:
            command = "echo " + \
                      self._session + \
                      " | sudo tee " + \
                      lockfile + \
                      self.EOF

            self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  unlock : Deltetes the lock file
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def unlock(self, pin, ):
        """
        Unlocks the gpio by deleting the content of the lock file.

        ***Shell***:
        ```shell
        sudo truncate --size=0 /tmp/htp/locks/gpio14
        ```

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')
        led.unlock(14)
        ...
        ```

        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        # Consistent folder name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # GPIO lock file
        iotag = self._iotag + str(pin)
        lockfile = self._lockdir + iotag

        # Empty lock file
        command = "sudo truncate --size=0 " + \
                  lockfile + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # isconfigured : Checks for folders with the name gpioXX
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def isconfigured(self, pin):
        """
        This function checks if the sysfs folder /sys/class/gpio/gpioNN exists.

        ***Shell:***
        ```shell
        find /sys/class/gpio -name gpio14
        ```

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.configure(14, telnetio.RaspberryPi.OUTPUT)
        if led.isconfigured(14):
            print("LED is configured!!!")
        ...
        ```
        """

        # Dictionary to transform mode strings to integers
        modes = {
            "in": self.INPUT,
            "out": self.OUTPUT,
        }

        # GPIO to check
        iotag = self._iotag + str(pin)

        # Check if pin folder is exported
        # find /sys/class/gpio -name gpio14
        command = "find " + \
                  "/sys/class/gpio " + \
                  "-name gpio[0-9][0-9]" + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush command echo
        self.read_until(self.EOF.encode('ascii'), self.timeout)

        # Read command response
        result = self.read_until(self.shell_prompt, self.timeout)
        result = bytes(result).decode()
        result = result.split(self.EOF)

        # Evaluate result in case sysfs folder exists
        if any(iotag in folders for folders in result):

            # Command to open file
            # sudo cat /sys/class/gpio/gpio14/direction
            command = "sudo cat " + \
                       "/sys/class/gpio/" + \
                       iotag + "/" + \
                       "direction" + \
                       self.EOF

            self.write(command.encode('ascii'))

            # Flush command echo
            self.read_until(self.EOF.encode('ascii'), self.timeout)

            # Read command result
            val = self.read_until(self.shell_prompt, self.timeout)
            val = bytes(val).decode()
            val = val.split()
            val = val[0].replace(self.EOF, "")
            val = val.lower()
            val = modes.get(val)

        else:
            val = 0

        return val

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  configure : Configures pin for use through the file system 
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def configure(self, pin, direction):
        """
        Create the sysfs virtual folder for gpio manipulation.

        *** Shell : ***
        ```shell
        echo 14 | tee /sys/class/gpio/export
        ```

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.configure(14, telnetio.RaspberryPi.OUTPUT)
        ...
        ```

        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        # Configure pin
        if not self.isconfigured(pin):

            # Export the desired pin (creates virtual folder)
            command = "echo " + \
                      str(pin) + \
                      " | tee /sys/class/gpio/export" + \
                      self.EOF

            self.write(command.encode('ascii'))

            # Flush buffer
            self.read_until(self.shell_prompt, self.timeout)

        # Configure the type of the pin = IN
        if direction == self.INPUT:
            command = "echo in | sudo tee /sys/class/gpio/gpio" + \
                      str(pin) + \
                      "/direction" + \
                      self.EOF

            self.write(command.encode('ascii'))

        # Configure the type of the pin = OUT
        if direction == self.OUTPUT:
            command = "echo out | sudo tee /sys/class/gpio/gpio" + \
                      str(pin) + \
                      "/direction" + \
                      self.EOF

            self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  cleanup : Deletes the current configuration of the pin 
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def deconfigure(self, pin):
        """
        Delete the sysfs virtual folder for pin manipulation.

        *** Shell : ***
        ```
        echo 14 | tee /sys/class/gpio/unexport
        ```

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.deconfigure(14)
        ...
        ```
        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        # Unexport desired pin (deletes virtual folder)
        command = "echo " + \
                  str(pin) + \
                  " | tee /sys/class/gpio/unexport" + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  get : Reads the value of the pin using the file system
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    """

    def get(self, pin):
        """
        Gets the current status of the given pin by reading the system file.

        *** Shell : ***
        ```shell
        cat /sys/class/gpio/gpio14/value
        ```

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.get(14)
        ...
        ```
        """

        command = "cat " + \
                  "/sys/class/gpio/gpio" + \
                  str(pin) + \
                  "/value" + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush command echo
        self.read_until(self.EOF.encode('ascii'), self.timeout)

        # Read command results
        value = self.read_until(self.EOF.encode('ascii'), self.timeout)
        value = bytes(value).decode()

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return int(value.replace(self.EOF, ""))

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  set : Writes to the pin using the file system
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    """

    def set(self, pin, value):
        """
        Sets the current value of the given pin by using the system file.

        *** Shell: ***
        ```
        echo 1 | sudo tee /sys/class/gpio/gpio14
        ```


        *** Example: ***
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.configure(14, telnetio.RaspberryPi.OUTPUT)
        led.set(14, 1)
        ...
        ```
        """

        # Verify is pin is locked by other process
        lock_owner = self.islocked(pin)
        if lock_owner is not None and lock_owner != self._session:
            raise PinLockedByOtherProcess(lock_owner, self._session)

        # Write to the desired pin (virtual file "value")
        command = "echo " + \
                  str(value) + \
                  " | sudo tee /sys/class/gpio/gpio" + \
                  str(pin) + \
                  "/value" + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  login : sends username and password to the telnet server
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def login(self):
        """
        Performs an automatic login to the remote system using the supplied
        user and password as instance properties.

        !!! Use only when creating an unconnected instance !!!


        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi()
        led.host = '192.168.199.31'
        led.port = 23
        led.user = 'htpio'
        led.password = 'sokotnar'

        led.open(host, port)
        led.login()

        ...
        ```
        """

        # Check if device already registered for use
        if not self._session:

            # Flush buffer and wait for login
            self.read_until(self.login_prompt, self.timeout)
            command = self.user + self.EOF
            self.write(command.encode('ascii'))

            # Flush buffer and wait for password
            self.read_until(self.password_prompt, self.timeout)
            command = self.password + self.EOF
            self.write(command.encode('ascii'))

            # Flush buffer
            result = self.read_until(self.shell_prompt, self.timeout)
            result = bytes(result).decode()

            if any('incorrect' in s for s in result.split()):
                raise InvalidLoginDetails
            else:
                self._session = self.__session()
                self.__makedir()

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  logout : Closes telnet connection
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def logout(self):
        """
        Closes the connection to the target.

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.logout()

        ...
        ```
        """

        # Add additional steps before closing the connection
        self.close()

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  reset : Initializes telnetio
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def reset(self, pin):
        """
        Deletes lock file for pin.

        ***Example***:
        ```python
        import htpio.telnetio as telnetio

        led = telnetio.RaspberryPi('192.168.199.31')

        led.reset(14)

        ...
        ```
        """

        # Consistent folder name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        iotag = self._iotag + str(pin)
        lockfile = self._lockdir + iotag

        # Delete lock file
        command = "sudo rm " + \
                  lockfile + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  __islockdir : Creates lock directory if not present
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __islockdir(self):
        """
        Checks if the lock directory exists.

        ```
        [ -d /tmp/htp/locks ] && echo 1 || echo 0
        ```
        """

        command = "[ -d " + \
                  self._lockdir + \
                  " ] " + \
                  "&& echo 1 || echo 0" + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush command line echo
        self.read_until(self.EOF.encode('ascii'), self.timeout)

        # Read command result
        result = self.read_until(self.EOF.encode('ascii'), self.timeout)
        result = bytes(result).decode()
        result = result.replace(self.EOF, "")

        return int(result)

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  __makedir : Creates lock directory if not present
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __makedir(self, folder=None):
        """
        Create the lock directory (stores the lock files).

        ```
        sudo mkdir -p /tmp/htp/locks
        ```
        """

        # Define lock folder name
        if folder is None:
            folder = self._lockdir
        else:
            self._lockdir = folder

        # Check and create lock directory
        if not self.__islockdir():

            command = "sudo mkdir -p " + \
                      folder + \
                      self.EOF

            self.write(command.encode('ascii'))

            if not self.__islockdir():
                raise CannotCreateLockDirectory

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        # Mount ram disk
        self.__mount(folder)

        return 0

    """
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  __ismounted : Check if ram disk mounted to lock directory
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    def __ismounted(self, ramdisk=None):
        """
        Check if ram disk is mounted on lock directory.

        ```
        mount | grep -i tmpfs
        ```
        """

        # Check if ram disk mounted
        command = "mount | grep -i " + \
                  ramdisk + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.EOF.encode('ascii'), self.timeout)

        # Read command result
        result = self.read_until(self.shell_prompt, self.timeout)
        result = bytes(result).decode()

        if any(ramdisk in mounts for mounts in result.split()):
            val = True
        else:
            val = False

        return val

    """
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  __mount : Mount ram disk
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    def __mount(self, folder=None):
        """
        Mount ram disk to lock folder. This is required to remove the problem
        of frequent read/write operations on the SD card.

        ```
        sudo mount -t tmpfs -o size=16m htp_ramdisk /tmp/htp/locks
        ```
        """

        if not self.__ismounted(folder):

            command = "sudo mount -t tmpfs -o size=16m " + \
                      self._ramdisk + \
                      " " + \
                      self._lockdir + \
                      self.EOF

            self.write(command.encode('ascii'))

            # Flush buffer
            self.read_until(self.shell_prompt, self.timeout)

            if not self.__ismounted(folder):
                raise CannotMountRamDisk

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  dismount : Ejects RAMDISK used to store the locksfiles
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __dismount(self, folder=None):
        """
        Dismounts htp ramdisk from lock folder directory.

        ```
        sudo umount /tmp/htp/locks
        ```
        """

        if folder is None:
            folder = self._lockdir

        # Unmount ram disk
        command = "sudo umount " + \
                  folder + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush buffer
        self.read_until(self.shell_prompt, self.timeout)

        return 0

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  session : Retrieves the current telnet session
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __session(self):
        """
        Gets the socket data for this connection and converts the to one
        unique identification number. This ID is used to lock gpios.
        """

        mysocket = self.sock
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

        ```
        ls /tmp/htp/locks
        ```
        """

        # List the content of the lock directory
        command = "ls " + \
                  self._lockdir + \
                  self.EOF

        self.write(command.encode('ascii'))

        # Flush command echo
        self.read_until(self.EOF.encode('ascii'), self.timeout)

        # Read command results
        self._locklist = self.read_until(self.shell_prompt, self.timeout)
        self._locklist = self._locklist.split()

        return self._locklist

    """
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  populate : generate GPIO lock files from 0 to MAX_GPIO
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    """

    def __populate(self):
        """
        Creates all lock files in the lock directory.

        ```
        touch -a gpio14
        ```
        """

        # Consistent directory name
        if not self._lockdir.endswith("/"):
            self._lockdir = self._lockdir + "/"

        # Create lock files
        for gpio in range(self.MAX_GPIO):
            iotag = self._iotag + str(gpio)
            lockfile = self._lockdir + iotag

            command = "touch -a " + \
                      lockfile + \
                      self.EOF

            self.write(command.encode('ascii'))

            # Flush buffer
            self.read_until(self.shell_prompt, self.timeout)

        return 0
