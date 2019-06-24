"""
High level implementation of a channel access client.
"""
import weakref
import threading
from datetime import datetime
import enum

import channel_access.common as ca
from . import cac



#: Exception raised when an error occurs inside a channel access function.
CaException = cac.CaException


# Can't distinguish between None value and timeout
class _EventData(object):
    """ A condition variable with an associated value. """
    def __init__(self, default=None):
        self._cond = threading.Condition()
        self._default = default
        self._value = None

    def set(self, value):
        with self._cond:
            self._value = value
            self._cond.notify()

    def get(self, timeout=None):
        result = None
        with self._cond:
            if self._value is None:
                self._cond.wait(timeout)
            result = self._value
            self._value = None
        return result


class InitData(enum.Enum):
    """ Data to initialize when a PV connects. """
    NONE = 0
    DATA = 1
    CONTROL = 2


class PV(object):
    """
    A channel access PV.

    This class gives thread-safe access to a channel access PV.

    It implements the context manager interface which makes it possible
    to use a with-statement to guarantee disconnect.

    The default parameters are such that methods will block until the
    request is fullfilled and then return the result.

    When calling methods on many PVs it is faster to use the non-blocking
    versions and at the end call :meth:`Client.flush()`.

    The following keys can occur in a data dictionary:

    value
        Data value, type depends on the native type. For integer types
        and enum types this is ``int``, for floating point types this is ``float``.
        For string types this is ``bytes`` or ``str`` depending on the
        ``encondig`` parameter.

    status
        Value status, one of :class:`Status`.

    severity
        Value severity, one of :class:`Severity`.

    timestamp
        An aware datetime representing the point in time the value was
        changed.

    enum_strings
        Tuple with the strings corresponding to the enumeration values.
        The entries are ``bytes`` or ``str`` depending on the
        ``encondig`` parameter.

    unit
        String representing the physical unit of the value. The type is
        ``bytes`` or ``str`` depending on the ``encondig`` parameter.

    precision
        Integer representing the number of relevant decimal places.

    display_limits
        A tuple ``(minimum, maximum)`` representing the range of values
        for a user interface.

    control_limits
        A tuple ``(minimum, maximum)`` representing the range of values
        accepted for a put request by the server.

    warning_limits
        A tuple ``(minimum, maximum)``. When the value lies outside of the
        range of values the status becomes :class:`Status.LOW` or :class:`Status.HIGH`.

    alarm_limits
        A tuple ``(minimum, maximum)``. When the value lies outside of the
        range of values the status becomes :class:`Status.LOLO` or :class:`Status.HIHI`.
    """
    def __init__(self, name, connect=True, monitor=True,
                 initialize=InitData.CONTROL, encoding='utf-8'):
        """
        Arguments:
            name (str): Name of the remote PV.
            connect (bool|callable):
                If ``True`` automatically call ``connect(block=False)`` after creating the PV.
                If ``False`` :meth:`connect()` must be called to use
                any channel access methods.

                If this is a callable, set it as the connection handler and
                automatically call ``connect(block=False)`` after creating the PV.
            monitor (bool|callable):
                If ``True`` automatically subscribe after :meth:`connect` is called.

                If this is a callable, set it as the monitor handler and
                automatically subscribe after :meth:`connect` is called.
            initialize (:class:`InitData`):
                If ``InitData.DATA`` automatically call ``get(block=False)``
                after a connection is etablished.

                If ``InitData.CONTROL`` automatically call ``get(block=False, control=True)``
                after a connection is etablished.

                This automatically initializes the PV data with the remote values
                as soon as a connection is etablished.
            encoding (str):
                The string encoding used for units, enum strings and string values.

                If ``None`` these values are ``bytes`` instead of ``str`` objects.
        """
        self._encoding = encoding
        self._auto_initialize = initialize
        self._auto_monitor = bool(monitor)

        self._connect_value = _EventData(False)
        self._get_value = _EventData()
        self._put_value = _EventData()
        self._subscribed = False

        self._data = {}
        self._data_lock = threading.Lock()

        self._user_connection_handler = None
        self._user_monitor_handler = None

        self._pv = cac.PV(name)
        self._pv.connection_handler = self._connection_handler
        self._pv.put_handler = self._put_handler
        self._pv.get_handler = self._get_handler
        self._pv.monitor_handler = self._monitor_handler

        if connect and not isinstance(connect, bool):
            self._user_connection_handler = connect

        if monitor and not isinstance(monitor, bool):
            self._user_monitor_handler = monitor

        if connect:
            self.connect(block=False)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.disconnect()

    def __del__(self):
        try:
            self.disconnect()
        except cac.CaException:
            pass

    def _decode(self, values):
        result = values.copy()

        if self._encoding is not None:
            if 'unit' in result:
                result['unit'] = result['unit'].decode(self._encoding)

            if 'enum_strings' in result:
                result['enum_strings'] = tuple(x.decode(self._encoding) for x in result['enum_strings'])

            value = result.get('value')
            if value is not None:
                if isinstance(value, bytes):
                    result['value'] = value.decode(self._encoding)
                elif self.count > 1 and len(value) > 1 and isinstance(value[0], bytes):
                    result['value'] = tuple( x.decode(self._encoding) for x in value )

        if 'timestamp' in result:
            result['timestamp'] = ca.epics_to_datetime(result['timestamp'])

        return result

    def _connection_handler(self, connected):
        self._connect_value.set(connected)
        if connected:
            if self._auto_initialize == InitData.DATA:
                self.get(block=False, control=False)
            elif self._auto_initialize == InitData.CONTROL:
                self.get(block=False, control=True)
                if self.is_enum:
                    self.get_enum_strings(block=False)
            if self._auto_monitor:
                self.subscribe()
            if self._auto_monitor or self._auto_initialize != InitData.NONE:
                cac.flush_io()
        if self._user_connection_handler:
            self._user_connection_handler(self, connected)

    def _put_handler(self, succeeded):
        self._put_value.set(succeeded)

    def _get_handler(self, values):
        values = self._decode(values)
        self._get_value.set(values)
        with self._data_lock:
            self._data.update(values)
        if self._user_monitor_handler:
            self._user_monitor_handler(self, values)

    def _monitor_handler(self, values):
        values = self._decode(values)
        with self._data_lock:
            self._data.update(values)
        if self._user_monitor_handler:
            self._user_monitor_handler(self, values)


    @property
    def connection_handler(self):
        """
        The connection handler.

        The handler is called when the connection status of the PV changes.

        **Signature**: ``fn(pv, connected)``

        **Parameters**:

            * **pv** (:class:`PV`): The :class:`PV` object with the
              changed connection state.
            * **connected** (bool): If ``True`` the PV is connected.
        """
        return self._user_connection_handler

    @connection_handler.setter
    def connection_handler(self, handler):
        self._user_connection_handler = handler


    @property
    def monitor_handler(self):
        """
        The monitor handler.

        The monitor handler is called when a channel access
        subscription triggers or data is received from a get request.

        **Signature**: ``fn(pv, data)``

        **Parameters**:

            * **pv** (:class:`PV`): The :class:`PV` object with the
              changed values.
            * **data** (dict): A data dictionary with the received values.
        """
        return self._user_monitor_handler

    @monitor_handler.setter
    def monitor_handler(self, handler):
        self._user_monitor_handler = handler


    def connect(self, block=True):
        """
        Create the channel and try to connect to it.

        Arguments:
            block (bool|float):
                If ``True`` block until a connection is etablished.
                If ``False`` the method returns immediatly.

                If this is a float, block for at most ``block`` seconds
                and return wether the connection is etablished or not.

        Returns:
            * ``None`` if ``block == False``.
            * ``True`` if ``block == True``.
            * If ``block > 0.0`` wether the connection is etablished.
        """
        self._pv.create_channel()

        if block is True or block > 0:
            cac.flush_io()
            return self._connect_value.get(None if block is True else block)

    def disconnect(self):
        """
        Destroy the channel.

        This also removes any active subscriptions. After this method is
        called no other channel access methods can be called.
        """
        self._pv.clear_channel()

    def ensure_connected(self, timeout=None):
        """
        Ensure that a connection is etablished.

        Arguments:
            timeout (None|float):
                If ``None`` block until a connection is etablished.

                If this is a float wait at most for ``timeout`` seconds.

        Raises:
            RuntimeError: If the connection could not be etablished.
        """
        try:
            connected = self.connected
        except cac.CaException:
            connected = False
            self.connect(block=False)
            cac.flush_io()

        if not connected:
            connected = self._connect_value.get(timeout)

        if not connected:
            raise RuntimeError("Could not ensure connection")

    def subscribe(self, trigger = ca.Events.VALUE | ca.Events.ALARM , count=None, control=False, as_string=False):
        """
        Create a channel access subscription.

        The request for the subscription is only queued. :meth:`Client.flush()`
        must be called to ensure it is send to the server.

        Arguments:
            trigger (:class:`Trigger`):
                The trigger sources for this subscription. See :class:`Trigger`.
            count (None|int):
                If ``None`` use the element count of this PV. Otherwise
                request ``count`` elements from the server.
            control (bool):
                If ``True`` request control values
                (precision, unit, limits, etc.) from the server.
            as_string (bool):
                If ``True`` request values as formatted strings from the server.
        """
        if count is None:
            count = self.count

        self._pv.subscribe(trigger, count, control, as_string)
        self._subscribed = True

    def unsubscribe(self):
        """
        Remove the channel access subscription.
        """
        self._subscribed = False
        self._pv.unsubscribe()

    def put(self, value, block=True):
        """
        Write a value into the PV.

        If ``block == False`` a request is only queued. :meth:`Client.flush()`
        must be called to ensure it is send to the server.

        Arguments:
            value: The new value. For array PVs a list must be used.
            block (bool|float):
                If ``True`` block until the value is changed on the server.
                If ``False`` the method returns immediatly.

                If this is a float, block for at most ``block`` seconds
                and return wether the value is changed on the server
                or ``None`` if the timeout occured.

        Returns:
            * ``None`` if ``block == False``.
            * ``True`` if ``block == True``.
            * If ``block > 0.0`` wether the value is changed on the server
              or ``None`` if the timeout occured.
        """
        if (isinstance(value, str) or (self.count > 1 and isinstance(value[0], str))) and self._encoding is None:
            raise TypeError("str value not allowed if no encoding is used")

        if self.count > 1 and isinstance(value[0], str):
            value = tuple(x.encode(self._encoding) for x in value)
        elif isinstance(value, str):
            value = value.encode(self._encoding)
        self._pv.put(value)

        if block is True or block > 0:
            cac.flush_io()
            return self._put_value.get(None if block is True else block)
        return None

    def get(self, block=True, count=None, control=False, as_string=False):
        """
        Read a value from the server.

        If ``block == False`` a request is only queued. :meth:`Client.flush()`
        must be called to ensure it is send to the server.

        Arguments:
            block (bool|float):
                If ``True`` block until the value arrived from the server.
                If ``False`` the method returns immediatly.

                If this is a float, block for at most ``block`` seconds
                and return the value or ``None`` if the timeout occured.
            count (None|int):
                If ``None`` use the element count of this PV. Otherwise
                request ``count`` elements from the server.
            control (bool):
                If ``True`` request control values
                (precision, unit, limits, etc.) from the server.
            as_string (bool):
                If ``True`` request values as formatted strings from the server.

        Returns:
            * ``None`` if ``block == False``.
            * The value if ``block == True``.
            * If ``block > 0.0`` the value or ``None`` if the timeout occured.
        """
        if count is None:
            count = self.count

        self._pv.get(count, control, as_string)

        if block is True or block > 0:
            cac.flush_io()
            data = self._get_value.get(None if block is True else block)
            if data is not None:
                return data.get('value')
        return None

    def get_enum_strings(self, block=True):
        """
        Read the tuple of enumeration strings form the server.

        If ``block == False`` a request is only queued. :meth:`Client.flush()`
        must be called to ensure it is send to the server.

        Arguments:
            block (bool|float):
                If ``True`` block until the value arrived from the server.
                If ``False`` the method returns immediatly.

                If this is a float, block for at most ``block`` seconds
                and return the strings or ``None`` if the timeout occured.

        Returns:
            * ``None`` if ``block == False``.
            * The strings if ``block == True``.
            * If ``block > 0.0`` the strings or ``None`` if the timeout occured.
        """
        self._pv.get_enum_strings()

        if block is True or block > 0:
            cac.flush_io()
            data = self._get_value.get(None if block is True else block)
            if data is not None:
                return data.get('enum_strings')
        return None

    @property
    def name(self):
        """
        str: The name of this PV.
        """
        return self._pv.name

    @property
    def host(self):
        """
        str: The remote host of this PV.
        """
        return self._pv.host()

    @property
    def count(self):
        """
        int: The number of elements of this PV.
        """
        return self._pv.count()

    @property
    def type(self):
        """
        :class:`FieldType`: The data type of this PV.
        """
        return self._pv.type()

    @property
    def access_rights(self):
        """
        :class:`AccessRights`: The access rights to this PV.
        """
        return self._pv.access()

    @property
    def connected(self):
        """
        bool: Wether this PV is connected or not.
        """
        return self._pv.is_connected()

    @property
    def monitored(self):
        """
        bool: Wether this PV is monitored by a :func:`subscribe` call.
        """
        return self._subscribed

    @property
    def is_enum(self):
        """
        bool: Wether this PV is of enumeration type.
        """
        return self.type == ca.Type.ENUM

    @property
    def data(self):
        """
        dict: A dictionary with the current values.
        """
        with self._data_lock:
            # We need a copy here for thread-safety. All keys and values
            # are immutable so a shallow copy is enough
            return self._data.copy()

    @property
    def timestamp(self):
        """
        datetime: The timestamp in UTC of the last received data or ``None`` if it's unknown.
        """
        with self._data_lock:
            return self._data.get('timestamp')

    @property
    def value(self):
        """
        The current value of the PV or ``None`` if it's unknown.

        This is writeable and calls ``put(value, block=False)``.
        """
        with self._data_lock:
            return self._data.get('value')

    @value.setter
    def value(self, value):
        self.put(value, block=False)

    @property
    def valid_value(self, exception=True):
        """
        Return a valid value or throw an exception.

        This property will only return a value if the pv is connected,
        it's severity is not INVALID and a value was received before.
        """
        if not self._pv.is_connected():
            raise RuntimeError("PV is not connected")
        with self._data_lock:
            value = self._data.get('value')
            severity = self._data.get('severity')
        if severity == Severity.INVALID:
            raise RuntimeError("PV value is invalid")
        if value is None:
            raise RuntimeError("PV value is unknown")
        return value

    @property
    def status(self):
        """
        :class:`Status`: The current status or ``None`` if it's unknown.
        """
        with self._data_lock:
            return self._data.get('status')

    @property
    def severity(self):
        """
        :class:`Severity`: The current severity or ``None`` if it's unknown.
        """
        with self._data_lock:
            return self._data.get('severity')

    @property
    def precision(self):
        """
        int: The current precision or ``None`` if it's unknown.
        """
        with self._data_lock:
            return self._data.get('precision')

    @property
    def unit(self):
        """
        str|bytes: The current unit or ``None`` if it's unknown.
        """
        with self._data_lock:
            return self._data.get('unit')

    @property
    def enum_strings(self):
        """
        tuple(str|bytes): The current enumeration strings or ``None`` if it's unknown.
        """
        with self._data_lock:
            return self._data.get('enum_strings')

    @property
    def display_limits(self):
        """
        tuple(float, float): The current display limits or ``None`` if they are unknown.
        """
        with self._data_lock:
            return self._data.get('display_limits')

    @property
    def control_limits(self):
        """
        tuple(float, float): The control display limits or ``None`` if they are unknown.
        """
        with self._data_lock:
            return self._data.get('control_limits')

    @property
    def warning_limits(self):
        """
        tuple(float, float): The warning display limits or ``None`` if they are unknown.
        """
        with self._data_lock:
            return self._data.get('warning_limits')

    @property
    def alarm_limits(self):
        """
        tuple(float, float): The alarm display limits or ``None`` if they are unknown.
        """
        with self._data_lock:
            return self._data.get('alarm_limits')


class Client(object):
    """
    Channel Access client.

    This class manages the process wide channel access context.
    An instance of this class must be created before any PV can be created.
    It must also be :meth:`shutdown()` before the process ends.

    It implements the context manager interface which makes it possible
    to use a with-statement to guarantee shutdown.

    A preemptive context is used so no polling functions have to be called.
    Depending on the use case :meth:`flush` has to be called.
    """
    def __init__(self):
        super().__init__()
        self._pvs = weakref.WeakValueDictionary()

        cac.initialize(True)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.shutdown()

    def flush(self, timeout=None):
        """
        Flush any outstanding server requests.

        When the non-blocking methods of the :class:`PV` class are used,
        requests are only queued but not necessarily send to the server.
        Calling this funtions flushes the send queue.

        Arguments:
            timeout (float): If ``None`` don't block, otherwise block
                             for ``timeout`` seconds.
        """
        if timeout is not None:
            cac.pend_event(timeout)
        else:
            cac.flush_io()

    def shutdown(self):
        """
        Shutdown the channel access client.

        Destroy the process wide channel access context and
        disconnect all active PV objects.
        """
        for pv in self._pvs.values():
            pv.disconnect()
        cac.pend_event(0.1)
        cac.finalize()

    def createPV(self, name, *args, **kwargs):
        """
        Create a new channel access PV.

        All arguments are forwarded to the :class:`PV` class.

        The client does not hold a reference to the returned PV so it
        can be collected if it is no longer used. It is the  responsibility
        of the user to keep the PV objects alive as long as they are needed.

        PV objects are cached. Calling this function multiple times
        with the same name will return the same object if it is not
        garbage collected between the calls.

        Returns:
            :class:`PV`: A new PV object.
        """
        pv = self._pvs.get(name)
        if pv is None:
            pv = PV(name, *args, **kwargs)
            self._pvs[name] = pv
        return pv
