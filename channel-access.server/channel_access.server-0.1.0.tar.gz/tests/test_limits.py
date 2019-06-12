import pytest

import channel_access.common as ca
import channel_access.server as cas
from . import common



@pytest.mark.parametrize("type_", common.INT_TYPES + common.FLOAT_TYPES)
def test_control_limits(server, type_):
    pv = server.createPV('CAS:Test', type_, attributes = {
        'control_limits': (-5, 10)
    })
    pv.value = 3
    assert(pv.value == 3)
    pv.value = -10
    assert(pv.value == -5)
    pv.value = 20
    assert(pv.value == 10)

def test_control_limits_enum(server):
    pv = server.createPV('CAS:Test', ca.Type.ENUM, attributes = {
        'enum_strings': ('', '', ''),
        'control_limits': (0, 2)
    })
    pv.value = 1
    assert(pv.value == 1)
    pv.value = -1
    assert(pv.value == 0)
    pv.value = 4
    assert(pv.value == 2)

@pytest.mark.parametrize("type_", common.INT_TYPES + common.FLOAT_TYPES)
def test_control_limits_array(server, type_):
    pv = server.createPV('CAS:Test', type_, count=3, attributes = {
        'control_limits': (-5, 10)
    })
    pv.value = (1, 2, 3)
    assert(pv.value == (1, 2, 3))
    pv.value = (-10, 2, 20)
    assert(pv.value == (-5, 2, 10))



@pytest.mark.parametrize("type_", common.INT_TYPES + common.FLOAT_TYPES)
def test_alarm_limits(server, type_):
    pv = server.createPV('CAS:Test', type_, attributes = {
        'warning_limits': (-5, 10),
        'alarm_limits': (-10, 15)
    })
    pv.value = -5
    assert(pv.status_severity == (ca.Status.NO_ALARM, ca.Severity.NO_ALARM))
    pv.value = -10
    assert(pv.status_severity == (ca.Status.LOW, ca.Severity.MINOR))
    pv.value = -15
    assert(pv.status_severity == (ca.Status.LOLO, ca.Severity.MAJOR))
    pv.value = 10
    assert(pv.status_severity == (ca.Status.NO_ALARM, ca.Severity.NO_ALARM))
    pv.value = 15
    assert(pv.status_severity == (ca.Status.HIGH, ca.Severity.MINOR))
    pv.value = 25
    assert(pv.status_severity == (ca.Status.HIHI, ca.Severity.MAJOR))

@pytest.mark.parametrize("type_", common.INT_TYPES + common.FLOAT_TYPES)
def test_control_limits_array(server, type_):
    pv = server.createPV('CAS:Test', type_, count=3, attributes = {
        'warning_limits': (-5, 10),
        'alarm_limits': (-10, 15)
    })
    # Simple limits
    pv.value = (1, -5, 3)
    assert(pv.status_severity == (ca.Status.NO_ALARM, ca.Severity.NO_ALARM))
    pv.value = (1, -10, 3)
    assert(pv.status_severity == (ca.Status.LOW, ca.Severity.MINOR))
    pv.value = (1, -15, 3)
    assert(pv.status_severity == (ca.Status.LOLO, ca.Severity.MAJOR))
    pv.value = (1, 10, 3)
    assert(pv.status_severity == (ca.Status.NO_ALARM, ca.Severity.NO_ALARM))
    pv.value = (1, 15, 3)
    assert(pv.status_severity == (ca.Status.HIGH, ca.Severity.MINOR))
    pv.value = (1, 25, 3)
    assert(pv.status_severity == (ca.Status.HIHI, ca.Severity.MAJOR))

    # Most severe should win
    pv.value = (1, -8, -15)
    assert(pv.status_severity == (ca.Status.LOLO, ca.Severity.MAJOR))
    pv.value = (1, 14, 25)
    assert(pv.status_severity == (ca.Status.HIHI, ca.Severity.MAJOR))
    pv.value = (1, -30, 12)
    assert(pv.status_severity == (ca.Status.LOLO, ca.Severity.MAJOR))
    pv.value = (1, -4, 20)
    assert(pv.status_severity == (ca.Status.HIHI, ca.Severity.MAJOR))

    # For violations in different directions the most
    # severe (absolute difference) should win
    pv.value = (1, -9, 11)
    assert(pv.status_severity == (ca.Status.LOW, ca.Severity.MINOR))
    pv.value = (1, -6, 14)
    assert(pv.status_severity == (ca.Status.HIGH, ca.Severity.MINOR))
    pv.value = (1, -30, 17)
    assert(pv.status_severity == (ca.Status.LOLO, ca.Severity.MAJOR))
    pv.value = (1, -12, 40)
    assert(pv.status_severity == (ca.Status.HIHI, ca.Severity.MAJOR))
