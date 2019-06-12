import threading
import weakref
import math
from datetime import datetime, timedelta

import channel_access.common as ca
from . import cas
from .cas import ExistsResponse, AttachResponse



def default_attributes(type, count):
    """
    Return the default attributes dictionary for new PVs.

    Args:
        type (:class:`channel_access.common.Type`): Type of the PV.
        count (int): Number of elements of the PV.

    Returns:
        dict: Attributes dictionary.
    """
    result = {
        'status': ca.Status.UDF,
        'severity': ca.Severity.INVALID,
        'timestamp': datetime.utcnow()
    }

    if type == ca.Type.STRING:
        result['value'] = ''
    else:
        result['value'] = 0 if count == 1 else (0,) * count
        result['unit'] = ''
        result['control_limits'] = (0, 0)
        result['display_limits'] = (0, 0)
        result['alarm_limits'] = (0, 0)
        result['warning_limits'] = (0, 0)
        if type == ca.Type.FLOAT or type == ca.Type.DOUBLE:
            result['precision'] = 0
        if type == ca.Type.ENUM:
            result['enum_strings'] = ('',)

    return result


class PV(object):
    """
    A channel access PV.

    This class gives thread-safe access to a channel access PV.
    Always create PV objects through :meth:`Server.createPV()`.

    The following keys can occur in an attributes dictionary:

    value
        Data value, type depends on the PV type. For integer types
        and enum types this is ``int``, for floating point types
        this is ``float``. For string types this is ``bytes`` or ``str``
        depending on the ``encondig`` parameter.
        For arrays this is a sequence of the corresponding values.

    status
        Value status, one of :class:`channel_access.common.Status`.

    severity
        Value severity, one of :class:`channel_access.common.Severity`.

    timestamp
        An aware datetime representing the point in time the value was
        changed.

    enum_strings
        Tuple with the strings corresponding to the enumeration values.
        The length of the tuple must be equal to :data:`PV.count`.
        The entries are ``bytes`` or ``str`` depending on the
        ``encondig`` parameter.
        This is only used for enum PVs.

    unit
        String representing the physical unit of the value. The type is
        ``bytes`` or ``str`` depending on the ``encondig`` parameter.
        This is only used for numerical PVs.

    precision
        Integer representing the number of relevant decimal places.
        This is only used for floating point PVs.

    display_limits
        A tuple ``(minimum, maximum)`` representing the range of values
        for a user interface.
        This is only used for numerical PVs.

    control_limits
        A tuple ``(minimum, maximum)`` representing the range of values
        accepted for a put request by the server.
        This is only used for numerical PVs.

    warning_limits
        A tuple ``(minimum, maximum)``. When any value lies outside of the
        range the status becomes :class:`channel_access.common.Status.LOW` or :class:`channel_access.common.Status.HIGH`.
        This is only used for numerical types.

    alarm_limits
        A tuple ``(minimum, maximum)``. When any value lies outside of the
        range the status becomes :class:`channel_access.common.Status.LOLO` or :class:`channel_access.common.Status.HIHI`.
        This is only used for numerical PVs.
    """
    def __init__(self, name, type, count=1, attributes=None, value_deadband=0, archive_deadband=0, encoding='utf-8'):
        """
        Args:
            name (str|bytes): Name of the PV.
                If ``encoding`` is ``None`` this must be raw bytes.
            type (:class:`channel_access.common.Type`): The PV type.
            attributes (dict): Attributes dictionary with the initial attributes.
                These will override the default attributes.
            value_deadband (int|float): If any value changes more than this
                deadband a value event is fired.
                This is only used for numerical PVs.
            archive_deadband (int|float): If any value changes more than this
                deadband an archive event is fired.
                This is only used for numerical PVs.
            encoding (str): The encoding used for the PV name and string
                attributes. If ``None`` these values must be bytes.
        """
        super().__init__()
        self._name = name
        self._pv = _PV(name, type, count, attributes, value_deadband, archive_deadband, encoding)

    @property
    def name(self):
        """
        str: The name of this PV.
        """
        return self._name

    @property
    def count(self):
        """
        int: The number of elements of this PV.
        """
        return self._pv.count()

    @property
    def type(self):
        """
        :class:`channel_access.common.Type`: The type of this PV.
        """
        return self._pv.type()

    @property
    def is_enum(self):
        """
        bool: Wether this PV is of enumeration type.
        """
        return self._pv.type == ca.Type.ENUM

    @property
    def attributes(self):
        """
        dict: The current attributes dictionary

        This is writeable and updates the attributes dictionary
        """
        with self._pv._attributes_lock:
            # We need a copy here for thread-safety. All keys and values
            # are immutable so a shallow copy is enough
            return self._pv._attributes.copy()

    @attributes.setter
    def attributes(self, attributes):
        with self._pv._attributes_lock:
            self._pv._update_attributes(attributes)

    @property
    def timestamp(self):
        """
        datetime: The timestamp in UTC of the last time value has changed.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('timestamp')

    @property
    def value(self):
        """
        The current value of the PV.

        This is writeable and updates the value and timestamp.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('value')

    @value.setter
    def value(self, value):
        pv = self._pv
        with pv._attributes_lock:
            pv._update_value(value)
            pv._update_meta('timestamp', datetime.utcnow())
            pv._publish()

    @property
    def status(self):
        """
        :class:`channel_access.common.Status`: The current status.

        This is writeable and updates the status.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('status')

    @status.setter
    def status(self, value):
        pv = self._pv
        with pv._attributes_lock:
            pv._update_status_severity(value, pv._attributes.get('severity'))
            pv._publish()

    @property
    def severity(self):
        """
        :class:`channel_access.common.Severity`: The current severity.

        This is writeable and updates the severity.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('severity')

    @severity.setter
    def severity(self, value):
        pv = self._pv
        with pv._attributes_lock:
            pv._update_status_severity(pv._attributes.get('status'), value)
            pv._publish()

    @property
    def status_severity(self):
        """
        tuple(:class:`channel_access.common.Status`, :class:`channel_access.common.Severity`): The current status and severity.

        This is writeable and updates the status and severity at
        the same time.
        """
        with self._pv._attributes_lock:
            return (self._pv._attributes.get('status'), self._pv._attributes.get('severity'))

    @status_severity.setter
    def status_severity(self, value):
        pv = self._pv
        with pv._attributes_lock:
            pv._update_status_severity(value[0], value[1])
            pv._publish()

    @property
    def precision(self):
        """
        int: The current precision.

        This is writeable and update the precision.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('precision')

    @precision.setter
    def precision(self, value):
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('precision', value)
            pv._publish()

    @property
    def unit(self):
        """
        str|bytes: The current unit.

        The type depends on the ``encoding`` parameter.

        This is writeable and updates the unit.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('unit')

    @unit.setter
    def unit(self, value):
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('unit', value)
            pv._publish()

    @property
    def enum_strings(self):
        """
        tuple(str|bytes): The current enumeration strings.

        The type depends on the ``encoding`` parameter.

        This is writeable and updates the enumeration strings. The length
        of the tuple must be equal to the ``count`` parameter.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('enum_strings')

    @enum_strings.setter
    def enum_strings(self, value):
        assert(len(value) >= self.count)
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('enum_strings', value)
            pv._publish()

    @property
    def display_limits(self):
        """
        tuple(int|float, int|float): The current display limits.

        This is writeable and updates the display limits:
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('display_limits')

    @display_limits.setter
    def display_limits(self, value):
        assert(len(value) >= 2)
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('display_limits', value)
            pv._publish()

    @property
    def control_limits(self):
        """
        tuple(int|float, int|float): The control display limits.

        This is writeable and updates the control display limits.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('control_limits')

    @control_limits.setter
    def control_limits(self, value):
        assert(len(value) >= 2)
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('control_limits', value)
            pv._publish()

    @property
    def warning_limits(self):
        """
        tuple(int|float, int|float): The warning display limits.

        This is writeable and updates the warning limits.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('warning_limits')

    @warning_limits.setter
    def warning_limits(self, value):
        assert(len(value) >= 2)
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('warning_limits', value)
            pv._publish()

    @property
    def alarm_limits(self):
        """
        tuple(int|float, int|float): The alarm display limits.

        This is writeable and updates the alarm limits.
        """
        with self._pv._attributes_lock:
            return self._pv._attributes.get('alarm_limits')

    @alarm_limits.setter
    def alarm_limits(self, value):
        assert(len(value) >= 2)
        pv = self._pv
        with pv._attributes_lock:
            pv._update_meta('alarm_limits', value)
            pv._publish()


class _PV(cas.PV):
    """
    PV implementation.

    This class handles all requests from the underlying binding class.
    """
    def __init__(self, name, type, count, attributes, value_deadband, archive_deadband, encoding):
        if encoding is not None:
            name = name.encode(encoding)
        super().__init__(name)
        self._type = type
        self._count = count
        self._encoding = encoding
        self._value_deadband = value_deadband
        self._archive_deadband = archive_deadband

        self._attributes_lock = threading.Lock()
        self._outstanding_events = ca.Events.NONE
        self._publish_events = False
        self._attributes = default_attributes(type, count)
        if attributes is not None:
            self._update_attributes(attributes)

    def _encode(self, attributes):
        """ Convert a high-level attributes dictionary to a low-level one. """
        result = attributes.copy()

        if self._encoding is not None:
            if 'unit' in result:
                result['unit'] = result['unit'].encode(self._encoding)

            if 'enum_strings' in result:
                result['enum_strings'] = tuple(x.encode(self._encoding) for x in result['enum_strings'])

            if 'value' in result and self._type == ca.Type.STRING:
                result['value'] = result['value'].encode(self._encoding)

        if 'timestamp' in result:
            result['timestamp'] = ca.datetime_to_epics(result['timestamp'])

        return result

    def _decode(self, value, timestamp=None):
        """ Convert a low-level value and timestamp to high-level ones. """
        if self._encoding is not None and self._type == ca.Type.STRING:
            value = value.decode(self._encoding)

        if timestamp is not None:
            timestamp = ca.epics_to_datetime(timestamp)

        return value, timestamp

    # only call with attributes lock held
    def _update_status_severity(self, status, severity):
        """ Update the status and serverity. """
        changed = False
        if status != self._attributes.get('status'):
            self._attributes['status'] = status
            changed = True
        if severity != self._attributes.get('severity'):
            self._attributes['severity'] = severity
            changed = True
        if changed:
            self._outstanding_events |= ca.Events.ALARM

    # only call with attributes lock held
    def _constrain_value(self, value):
        """ Constrain a value to the control limits range. """
        if self._type != ca.Type.STRING:
            ctrl_limits = self._attributes.get('control_limits')

            if ctrl_limits is not None and ctrl_limits[0] < ctrl_limits[1]:
                clamp = lambda v: max(min(v, ctrl_limits[1]), ctrl_limits[0])
                if self._count == 1:
                    return clamp(value)
                else:
                    return tuple(map(clamp, value))
        return value

    # only call with attributes lock held
    def _calculate_status_severity(self, value):
        """ Calculate status and severity values using warning and alarm limits. """
        status = ca.Status.NO_ALARM
        severity = ca.Severity.NO_ALARM
        if self._type != ca.Type.STRING:
            alarm_limits = self._attributes.get('alarm_limits')
            warn_limits = self._attributes.get('warning_limits')

            if self._count == 1:
                lowest = value
                highest = value
            else:
                # For arrays use the extreme values
                lowest = min(value)
                highest = max(value)

            if warn_limits is not None and warn_limits[0] < warn_limits[1]:
                if lowest < warn_limits[0] and highest > warn_limits[1]:
                    # If both limits are violated (can happen in arrays)
                    # the violation with the highest absolute difference
                    # is used
                    if abs(lowest - warn_limits[0]) > abs(highest - warn_limits[1]):
                        severity = ca.Severity.MINOR
                        status = ca.Status.LOW
                    else:
                        severity = ca.Severity.MINOR
                        status = ca.Status.HIGH
                elif lowest < warn_limits[0]:
                    severity = ca.Severity.MINOR
                    status = ca.Status.LOW
                elif highest > warn_limits[1]:
                    severity = ca.Severity.MINOR
                    status = ca.Status.HIGH

            if alarm_limits is not None and alarm_limits[0] < alarm_limits[1]:
                if lowest < alarm_limits[0] and highest > alarm_limits[1]:
                    # If both limits are violated (can happen in arrays)
                    # the violation with the highest absolute difference
                    # is used
                    if abs(lowest - alarm_limits[0]) > abs(highest - alarm_limits[1]):
                        severity = ca.Severity.MAJOR
                        status = ca.Status.LOLO
                    else:
                        severity = ca.Severity.MAJOR
                        status = ca.Status.HIHI
                elif lowest < alarm_limits[0]:
                    severity = ca.Severity.MAJOR
                    status = ca.Status.LOLO
                elif highest > alarm_limits[1]:
                    severity = ca.Severity.MAJOR
                    status = ca.Status.HIHI
        return status, severity

    # only call with attributes lock held
    def _update_value(self, value):
        """ Update the value and depending on it the status and severity. """
        value = self._constrain_value(value)
        status, severity = self._calculate_status_severity(value)

        old_value = self._attributes.get('value')
        if value != old_value:
            self._attributes['value'] = value
            if self._type not in (ca.Type.STRING, ca.Type.ENUM):
                if self._count == 1:
                    diff = abs(value - old_value)
                else:
                    # Look at the maximum difference between the old values
                    # and the new ones.
                    diff = max(map(lambda x: abs(x[0] - x[1]), zip(value, old_value)))
                if diff >= self._value_deadband:
                    self._outstanding_events |= ca.Events.VALUE
                if diff >= self._archive_deadband:
                    self._outstanding_events |= ca.Events.ARCHIVE
            else:
                self._outstanding_events |= ca.Events.VALUE | ca.Events.ARCHIVE
        self._update_status_severity(status, severity)

    # only call with attributes lock held
    def _update_meta(self, key, value):
        """ Update the meta data attributes. """
        if value != self._attributes.get(key):
            self._attributes[key] = value
            self._outstanding_events |= ca.Events.PROPERTY
        if key.endswith('_limits'):
            # If the limits change we might need to change the value accordingly
            self._update_value(self._attributes.get('value'))

    # only call with attributes lock held
    def _update_attributes(self, attributes):
        """ Update attributes using an attributes dictionary. """
        limits_changed = False
        for key in ['precision', 'enum_strings', 'unit', 'control_limits', 'display_limits', 'alarm_limits', 'warning_limits']:
            if key in attributes and attributes[key] != self._attributes.get(key):
                self._attributes[key] = attributes[key]
                self._outstanding_events |= ca.Events.PROPERTY
                if key.endswith('_limits'):
                    limits_changed = True

        # Change status and serverity first beacuse a value change might
        # override them
        if 'status' in attributes or 'severity' in attributes:
            if 'status' in attributes:
                status = attributes['status']
            else:
                status = self._attributes.get('status')
            if 'severity' in attributes:
                severity = attributes['severity']
            else:
                severity = self._attributes.get('severity')
            self._update_status_severity(status, severity)

        if 'value' in attributes:
            self._update_value(attributes['value'])
        elif limits_changed:
            # If the limits change we might need to change the value accordingly
            self._update_value(self._attributes.get('value'))

    # only call with attributes lock held
    def _publish(self):
        """ Post events if necessary. """
        events = self._outstanding_events
        self._outstanding_events = ca.Events.NONE
        if self._publish_events and events != ca.Events.NONE:
            self.postEvent(events, self._encode(self._attributes))

    def count(self):
        return self._count

    def type(self):
        return self._type

    def read(self):
        with self._attributes_lock:
            return self._encode(self._attributes)

    def write(self, value, timestamp=None):
        value, timestamp = self._decode(value, timestamp)
        with self._attributes_lock:
            self._update_value(value)
            self._update_meta('timestamp', timestamp)
            self._publish()
            return True
        return False

    def interestRegister(self):
        with self._attributes_lock:
            self._publish_events = True
        return True

    def interestDelete(self):
        with self._attributes_lock:
            self._publish_events = False


class Server(object):
    """
    Threaded channel access server.

    On creation this class creates a server thread which processes
    channel access messages.

    The :meth:`shutdown()` method must be called to stop the server.

    This class implements the context manager protocol. This automatically
    shuts the server down at the end of the with-statement::

        with cas.Server() as server:
            pass
    """
    def __init__(self):
        super().__init__()
        self._server = _Server()
        self._thread = _ServerThread()

        self._thread.start()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.shutdown()

    def shutdown(self):
        """
        Shutdown the channel access server.

        After this is called no other methods can be called.
        """
        self._thread.stop()
        self._thread.join()
        self._server = None

    def createPV(self, *args, **kwargs):
        """
        Create a new channel access PV.

        All arguments are forwarded to the :class:`PV` class.

        The server does not hold a reference to the returned PV so it
        can be collected if it is no longer used. It is the  responsibility
        of the user to keep the PV objects alive as long as they are needed.

        If a PV with an already existing name is created the server will
        use the new PV and ignore the other one. Connections made to the
        old PV remain active and use the old PV object.

        Returns:
            :class:`PV`: A new PV object.
        """
        return self._server.createPV(*args, **kwargs)


class _Server(cas.Server):
    """
    Server implementation.

    This stores the created PVs in a weak dictionary and answers
    the requests using it.
    """
    def __init__(self):
        super().__init__()
        self._pvs = weakref.WeakValueDictionary()

    def pvExistTest(self, client, pv_name):
        if pv_name in self._pvs:
            return ExistsResponse.EXISTS_HERE
        return ExistsResponse.NOT_EXISTS_HERE

    def pvAttach(self, pv_name):
        pv = self._pvs.get(pv_name)
        if pv is None:
            return AttachResponse.NOT_FOUND
        return pv._pv

    def createPV(self, *args, **kwargs):
        pv = PV(*args, **kwargs)
        # Store the raw bytes name in the dictionary
        self._pvs[pv._pv.name()] = pv
        return pv


class _ServerThread(threading.Thread):
    """
    A thread calling cas.process() until :meth:`stop()` is called.
    """
    def __init__(self):
        super().__init__()
        self._should_stop = threading.Event()

    def run(self):
        while not self._should_stop.is_set():
            cas.process(0.1)

    def stop(self):
        self._should_stop.set()
