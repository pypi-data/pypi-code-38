# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import


class PingParameters(object):
    """Recollect parameters to be used to format ping command line

    PingParameters class is a data model recollecting parameters used to
    create a ping command line. It provides the feature of copying default
    values from another instance of PingParameters passed using constructor
    parameter 'default'.
    """

    def __init__(self, host=None, count=None, deadline=None,
                 fragmentation=None, interval=None, is_cirros_image=None,
                 ip_version=None, payload_size=None, packet_size=None,
                 source=None, timeout=None):
        self.count = count
        self.deadline = deadline
        self.host = host
        self.fragmentation = fragmentation
        self.interval = interval
        self.ip_version = ip_version
        self.is_cirros_image = is_cirros_image
        self.packet_size = packet_size
        self.payload_size = payload_size
        self.source = source
        self.timeout = timeout

    def __repr__(self):
        return "PingParameters({!s})".format(
            ", ".join("{!s}={!r}".format(k, v)
                      for k, v in self.__dict__.items()))


def get_ping_parameters(default=None, **ping_params):
    """Get ping parameters eventually merging them with given extra parameters

    The only difference with init_parameters function is that in case
    default parameter is not None not any extra parameters is given, then
    it simply return given default instance, without performing any validation.
    """
    if default and not ping_params:
        return default
    else:
        return ping_parameters(default=default, **ping_params)


def ping_parameters(default=None, count=None, deadline=None,
                    fragmentation=None, host=None, interval=None,
                    is_cirros_image=None, ip_version=None, packet_size=None,
                    payload_size=None, source=None, timeout=None):
    """Validate parameters and initialize a new PingParameters instance

    :param default: (PingParameters or None) instance from where to take
    default values when other value is not provided. If None (that is the
    default value) it will copy default parameters from
    DEFAULT_PING_PARAMETERS

    :param count: (int or None) number of ping ICMP message expecting to be
    received before having a success. Default value can be configured using
    'count' option in [ping] config section.

    :param host: (str or None) IP address or host name to send ICMP
    messages to. It is required to format a valid ping command, therefore
    no default value exists for this parameter.

    :param deadline: (int or None) positive number representing the maximum
    number of seconds ping command can send ICMP messages before stop
    executing. Default value can be configured using 'deadline' option
    in [ping] config section.

    :param fragmentation: (bool or None) when False this would tell ping
    to forbid ICMP messages fragmentation. Default value can be configured
    using 'fragmentation' option in [ping] config section.

    :param interval: (int or None) interval of time before sending following
    ICMP message. Default value can be configured using 'interval' option
    in [ping] config section.

    :param is_cirros_image: (bool or None) when True means that ping command
    has to be formated for being executed on a CirrOS based guess instance.

    :param ip_version: (4, 6 or None) If not None it makes sure it will
    use specified IP version for sending ICMP packages.

    :param packet_size: ICMP message size. Default value can be configured
    using 'package_size' option in [ping] config section.

    :param payload_size: (int or None) if not None, it specifies ICMP message
    size minus ICMP and IP header size.

    :param source: (str or None) IP address or interface name from where
    to send ICMP message.

    :param timeout: (int or None) time in seconds after which ping operation
    would raise PingFailed exception.

    :raises TypeError: in case some parameter cannot be converted to right
    expected type

    :raises ValueError: in case some parameter has an unexpected value
    """

    if packet_size:
        if payload_size:
            msg = ("Can't set 'package_size' and 'payload_size' parameters "
                   "at the same time: package_size={!r}, payload_size={!r}"
                   ).format(packet_size, payload_size)
            raise ValueError(msg)

    count = count or 1
    if count < 1:
        msg = ("Count is not positive: count={!r}").format(count)
        raise ValueError(msg)

    if default is not False:
        default = default or default_ping_parameters()
        # Copy default parameters
        count = count or default.count
        if deadline is None:
            deadline = default.deadline
        host = host or default.host
        if fragmentation is None:
            fragmentation = default.fragmentation
        interval = interval or default.interval
        ip_version = ip_version or default.ip_version
        packet_size = packet_size or default.packet_size
        payload_size = payload_size or default.payload_size
        source = source or default.source
        timeout = timeout or default.timeout

    count = int(count)
    if count < 1:
        msg = "'count' parameter cannot be smaller than 1"
        raise ValueError(msg)

    deadline = int(deadline)
    if deadline < 0:
        msg = ("'deadline' parameter cannot be smaller than 0 "
               "(deadline={!r})").format(deadline)
        raise ValueError(msg)

    interval = int(interval)
    if interval < 1:
        msg = ("'interval' parameter cannot be smaller than 1 "
               "(interval={!r})").format(interval)
        raise ValueError(msg)

    timeout = int(timeout)
    if timeout < 1:
        msg = ("'timeout' parameter cannot be smaller than 1 "
               "(timeout={!r})").format(timeout)
        raise ValueError(msg)

    if is_cirros_image:
        if fragmentation is False:
            msg = ("'fragmentation' parameter cannot be False when "
                   "pinging from a CirrOS image (is_cirros_image={!r})"
                   ).format(is_cirros_image)
            raise ValueError(msg)

        if interval != 1:
            msg = ("Cannot specify 'interval' parameter when pinging from a "
                   "CirrOS image (interval={!r}, is_cirros_image={!r})"
                   ).format(interval, is_cirros_image)
            raise ValueError(msg)

    return PingParameters(count=count, host=host,
                          deadline=deadline, fragmentation=fragmentation,
                          interval=interval, is_cirros_image=is_cirros_image,
                          ip_version=ip_version, packet_size=packet_size,
                          payload_size=payload_size, source=source,
                          timeout=timeout)


def default_ping_parameters():
    from tobiko import config
    CONF = config.CONF
    return ping_parameters(
        default=False,
        count=CONF.tobiko.ping.count,
        deadline=CONF.tobiko.ping.deadline,
        fragmentation=CONF.tobiko.ping.fragmentation,
        interval=CONF.tobiko.ping.interval,
        packet_size=CONF.tobiko.ping.packet_size,
        timeout=CONF.tobiko.ping.timeout)
