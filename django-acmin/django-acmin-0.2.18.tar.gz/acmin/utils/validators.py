import ipaddress
import re

from django.core.exceptions import ValidationError

EVENT_ID_RE = re.compile(r'^[a-fA-F0-9]{32}$')


def validate_mac_address(value):
    if not re.match(r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$", value):
        raise ValidationError('输入一个有效的 MAC 地址。')


def validate_ip_address(value):
    if not re.match(r"^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*$", value):
        raise ValidationError('输入一个有效的 IPv4 地址。')


def validate_ip(value, required=True):
    if not required and not value:
        return

    # will raise a ValueError
    ipaddress.ip_network(str(value), strict=False)
    return value


def is_float(var):
    try:
        float(var)
    except (TypeError, ValueError):
        return False
    return True


def is_event_id(value):
    try:
        return bool(EVENT_ID_RE.match(value))
    except TypeError:
        return False
