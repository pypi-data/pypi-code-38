import re
import typing

import netmiko

import napalm_aruba.records
import napalm_aruba.templates.reader


def get_uptime(device: netmiko.BaseConnection):
    """Fetch device uptime and return the value in seconds."""
    r = device.send_command("show uptime")

    m = re.match(r"^(?P<d>\d+):(?P<H>\d+):(?P<M>\d+):(?P<S>\d+).(?P<f>\d+)$", r)
    if not m:
        raise RuntimeError("Unexpected response from device.")

    factors = {"d": 86_400.0, "H": 3_600.0, "M": 60.0, "S": 1.0, "f": 0.1}
    return sum(factors[k] * float(v) for k, v in m.groupdict().items())


def read_mib_value(device: netmiko.BaseConnection, oid: str) -> str:
    output = device.send_command("getMIB {}".format(oid))

    if output.strip() == "{}: No such name.".format(oid):
        raise RuntimeError(output)

    return output.split(" = ")[1].strip()


def walk_mib_value(
    device: netmiko.BaseConnection, oid: str
) -> typing.Generator[str, str, None]:
    output = device.send_command("walkMIB {}".format(oid))

    if output.strip() == "{}: No such name.":
        raise RuntimeError(output)

    return (l.split(" = ") for l in output.split("\n"))


def get_interfaces(
    device: netmiko.BaseConnection
) -> typing.Sequence[napalm_aruba.records.Interface]:
    r = device.send_command("show interfaces brief")

    t = napalm_aruba.templates.reader.read_template("interfaces-brief")

    d = t.ParseText(r)
    return [napalm_aruba.records.Interface(*item) for item in d]


def get_device_manufacturer_info(device: netmiko.BaseConnection):
    r = device.send_command("display device manuinfo")

    t = napalm_aruba.templates.reader.read_template("display-device-manuinfo")

    d = t.ParseText(r)[0]
    return napalm_aruba.records.DeviceInformation(
        device_name=d[0].strip(), vendor_name=d[1].strip()
    )


def get_system_information(device: netmiko.BaseConnection):
    r = device.send_command("show system information")

    t = napalm_aruba.templates.reader.read_template("system-information")

    d = t.ParseText(r)[0]
    return napalm_aruba.records.SystemInformation(
        hostname=d[0],
        os_version=d[1],
        serial_number=d[2],
        cpu_utilization=float(d[3]) / 100,
        memory_total=int(d[4].replace(",", "")),
        memory_free=int(d[5].replace(",", "")),
    )


def get_lldp_neighbors(device: netmiko.BaseConnection):
    r = device.send_command("show lldp info remote-device detail")

    t = napalm_aruba.templates.reader.read_template("lldp-info-remote-device")

    d = t.ParseText(r)
    return [dict(zip(e[0], (a.strip() for a in e[1]))) for e in d]
