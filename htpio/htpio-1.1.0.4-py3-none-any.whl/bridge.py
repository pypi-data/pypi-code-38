# Copyright (c) Hilscher GmbH. All Rights Reserved.
#
# $Author: bgeorgiev $
# $Date: 2019-05-16 11:34:02 +0300 (Thu, 16 May 2019) $
# $Revision: 654 $


"""
This module provides the connection between the client application and the
remote i/o implementation.

*** Example *** :

```
import time
import htpio.bridge as bridge
import htpio.telnetio as telnetio
import htpio.socketio as socketio

device = telnetio.RaspberryPi('192.168.199.31')
gpio = bridge.RemoteAccess(device)

gpio.lock(14)
gpio.configure(14, gpio.OUTPUT)

gpio.set(14, 1)
time.sleep(1)
gpio.set(14, 0)

gpio.unlock(14)
gpio.deconfigure(14)
gpio.logout()

device = socketio.RaspberryPi('192.168.199.31')
gpio = bridge.RemoteAccess(device)

gpio.lock(15)
gpio.configure(15, gpio.OUTPUT)

gpio.set(15, 1)
time.sleep(1)
gpio.set(15, 0)

gpio.unlock(15)
gpio.deconfigure(15)
gpio.logout()

```

"""

# Compatibility imports
from __future__ import unicode_literals
from __future__ import absolute_import

# System imports
from abc import ABCMeta, abstractmethod


"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Class Device : Implementor interface abstraction
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


class Device(object):
    """
    Define the implementor's interface from the bridge pattern. This interface
    provides homogeneous interface for all remote I/O libraries.

    Typically the implementor interface provides only primitive operations,
    and abstraction defines higher-level operations based on these primitives.
    """

    __metaclass__ = ABCMeta

    # ----------------------------------------------------------------------

    INPUT = None
    """ Pin input mode"""

    OUTPUT = None
    """ Pin output mode"""

    MAX_GPIO = None
    """ Maximum number of GPIOS"""

    # ----------------------------------------------------------------------
    @abstractmethod
    def islocked(self, pin):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def lock(self, pin):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def unlock(self, pin):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def isconfigured(self, pin):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def configure(self, pin, direction):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def deconfigure(self, pin):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def login(self):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def logout(self):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def get(self, pin):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def set(self, pin, value):
        """ Abstract method """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    @abstractmethod
    def reset(self, pin):
        """ Abstract method """
        raise NotImplementedError


class DeviceFactoryMixin(Device):
    """
    Partial implementation of the device factories. In this case this class
    increases code reuse by implementing several repeating implementations of
    the device factory classes.

    Device factories are classes which return objects based on parameters
    in their constructors. They also define the interface of the concrete
    implementations.

    Example:

    >>> device = RaspberryPi(os="raspbian")

    """

    def __init__(self, factory):
        self.factory = factory

    # ----------------------------------------------------------------------

    def lock(self, pin):
        return self.factory.lock(pin)

    # ----------------------------------------------------------------------

    def unlock(self, pin):
        return self.factory.unlock(pin)

    # ----------------------------------------------------------------------

    def islocked(self, pin):
        return self.factory.islocked(pin)

    # ----------------------------------------------------------------------

    def set(self, pin, value):
        return self.factory.set(pin, value)

    # ----------------------------------------------------------------------

    def get(self, pin):
        return self.factory.get(pin)

    # ----------------------------------------------------------------------

    def configure(self, pin, direction):
        return self.factory.configure(pin, direction)

    # ----------------------------------------------------------------------

    def deconfigure(self, pin):
        return self.factory.deconfigure(pin)

    # ----------------------------------------------------------------------

    def isconfigured(self, pin):
        return self.factory.isconfigured(pin)

    # ----------------------------------------------------------------------

    def reset(self, pin):
        return self.factory.reset(pin)

    # ----------------------------------------------------------------------

    def login(self):
        return self.factory.login()

    # ----------------------------------------------------------------------

    def logout(self):
        return self.factory.logout()


"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Class RemoteAccess : Bridge interface for client applications
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
"""


class RemoteAccess(DeviceFactoryMixin):

    """
    Define the abstraction's interface from the bridge pattern used by the
    client application.

    Typically the implementor interface provides only primitive operations,
    and abstraction defines higher-level operations based on these primitives.
    """

    # ----------------------------------------------------------------------
    def __init__(self, device_api):

        # Define instance attributes. These cannot be defined as class
        # attributes as bridge might have different types of in/out
        # and max_gpio definitions.

        self.INPUT = device_api.INPUT
        self.OUTPUT = device_api.OUTPUT
        self.MAX_GPIO = device_api.MAX_GPIO

        # Define interface for remote access
        self._device_api = device_api

        super(RemoteAccess, self).__init__(device_api)

    # ----------------------------------------------------------------------
    def islocked(self, pin):
        """
        Check if pin is locked by another process

        *** Example: ***
        ```python
        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.lock(14)
        if led.islocked(14):
            print("LED is locked!!!")
        led.logout()
        ...
        ```
        """

        return super(RemoteAccess, self).islocked(pin)

    # ----------------------------------------------------------------------
    def lock(self, pin):
        """
        Lock pin if it is not used

        *** Example: ***
        ```python
        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.lock(14)
        ...
        ```

        """

        return super(RemoteAccess, self).lock(pin)

    # ----------------------------------------------------------------------
    def unlock(self, pin):
        """
        Unlock pin if it belongs to my session

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.unlock(14)
        ...
        ```
        """

        return super(RemoteAccess, self).unlock(pin)

    # ----------------------------------------------------------------------
    def isconfigured(self, pin):
        """
        Check if pin is configured

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.isconfigured(14)
        ...
        ```

        """

        return super(RemoteAccess, self).isconfigured(pin)

    # ----------------------------------------------------------------------
    def configure(self, pin, direction):
        """
        Configure pin with direction if it is free

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.configure(14, led.OUTPUT)
        led.set(14, 1)
        ...
        ```
        """

        return super(RemoteAccess, self).configure(pin, direction)

    # ----------------------------------------------------------------------
    def deconfigure(self, pin):
        """
        Deconfigure pin if it belongs to my session

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.deconfigure(14)
        ...
        ```

        """

        return super(RemoteAccess, self).deconfigure(pin)

    # ----------------------------------------------------------------------
    def login(self):
        """
        Registers to remote device

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.login()
        ...
        ```

        """

        return super(RemoteAccess, self).login()

    # ----------------------------------------------------------------------
    def logout(self):
        """
        Unregisters from remote device

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.logout()
        ...
        ```
        """

        return super(RemoteAccess, self).logout()

    # ----------------------------------------------------------------------
    def get(self, pin):
        """
        Get pin value

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.configure(14, led.OUTPUT)
        led.set(14, 1)
        print(led.get(14))
        ...
        ```

        """

        return super(RemoteAccess, self).get(pin)

    # ----------------------------------------------------------------------
    def set(self, pin, value):
        """
        Write value to pin

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.configure(14, led.OUTPUT)
        led.set(14, 1)
        print(led.get(14))
        ...
        ```

        """

        return super(RemoteAccess, self).set(pin, value)

    # ----------------------------------------------------------------------
    def reset(self, pin):
        """
        Remove pin lock forcefully

        ***Example***:
        ```python

        from htpio.bridge import RemoteAccess
        from htpio import telnetio, socketio

        remoteio = socketio.RaspberryPi('192.168.199.31')
        led = RemoteAccess(remoteio)
        led.lock(14)
        print(led.islocked(14))
        led.reset(14)
        print(led.islocked(14))
        ...
        ```

        """

        return super(RemoteAccess, self).reset(pin)
