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

import time

import netaddr
from neutron_lib import constants
from oslo_log import log

from tobiko.shell import sh
from tobiko.shell.ping import _exception
from tobiko.shell.ping import _parameters
from tobiko.shell.ping import _statistics


LOG = log.getLogger(__name__)


TRANSMITTED = 'transmitted'
DELIVERED = 'delivered'
UNDELIVERED = 'undelivered'
RECEIVED = 'received'
UNRECEIVED = 'unreceived'


def ping(host, until=TRANSMITTED, check=True, **ping_params):
    """Send ICMP messages to host address until timeout

    :param host: destination host address
    :param **ping_params: parameters to be forwarded to get_statistics()
        function
    :returns: PingStatistics
    """
    return get_statistics(host=host, until=until, check=check, **ping_params)


def ping_until_delivered(host, **ping_params):
    """Send 'count' ICMP messages

    Send 'count' ICMP messages

    ICMP messages are considered delivered when they have been
    transmitted without being counted as errors.

    :param host: destination host address
    :param **ping_params: parameters to be forwarded to get_statistics()
        function
    :returns: PingStatistics
    :raises: PingFailed in case timeout expires before delivering all
        expected count messages
    """
    return ping(host=host, until=DELIVERED, **ping_params)


def ping_until_undelivered(host, **ping_params):
    """Send ICMP messages until it fails to deliver messages

    Send ICMP messages until it fails to deliver 'count' messages

    ICMP messages are considered undelivered when they have been
    transmitted and they have been counted as error in ping statistics (for
    example because of errors into the route to remote address).

    :param host: destination host address
    :param **ping_params: parameters to be forwarded to get_statistics()
        function
    :returns: PingStatistics
    :raises: PingFailed in case timeout expires before failing delivering
        expected 'count' of messages
    """
    return ping(host=host, until=UNDELIVERED, **ping_params)


def ping_until_received(host, **ping_params):
    """Send ICMP messages until it receives messages back

    Send ICMP messages until it receives 'count' messages back

    ICMP messages are considered received when they have been
    transmitted without any routing errors and they are received back

    :param host: destination host address
    :param **ping_params: parameters to be forwarded to get_statistics()
        function
    :returns: PingStatistics
    :raises: PingFailed in case timeout expires before receiving all
        expected 'count' of messages
    """
    return ping(host=host, until=RECEIVED, **ping_params)


def ping_until_unreceived(host, **ping_params):
    """Send ICMP messages until it fails to receive messages

    Send ICMP messages until it fails to receive 'count' messages back.

    ICMP messages are considered unreceived when they have been
    transmitted without any routing error but they failed to be received
    back (for example because of network filtering).

    :param host: destination host address
    :param **ping_params: parameters to be forwarded to get_statistics()
        function
    :returns: PingStatistics
    :raises: PingFailed in case timeout expires before failed receiving
        expected 'count' of messages
    """
    return ping(host=host, until=UNRECEIVED, **ping_params)


def get_statistics(parameters=None, ssh_client=None, until=None, check=True,
                   **ping_params):
    parameters = _parameters.get_ping_parameters(default=parameters,
                                                 **ping_params)
    statistics = _statistics.PingStatistics()
    for partial_statistics in iter_statistics(parameters=parameters,
                                              ssh_client=ssh_client,
                                              until=until, check=check):
        statistics += partial_statistics
        LOG.debug("%r", statistics)

    return statistics


def iter_statistics(parameters=None, ssh_client=None, until=None, check=True,
                    **ping_params):
    parameters = _parameters.get_ping_parameters(default=parameters,
                                                 **ping_params)
    now = time.time()
    end_of_time = now + parameters.timeout
    deadline = parameters.deadline
    transmitted = 0
    received = 0
    undelivered = 0
    count = 0

    while deadline > 0 and count < parameters.count:
        # splitting total timeout interval into smaller deadline intervals will
        # cause ping command to be executed more times allowing to handle
        # temporary packets routing problems
        if until == RECEIVED:
            execute_parameters = _parameters.get_ping_parameters(
                default=parameters,
                deadline=deadline,
                count=(parameters.count - count))
        else:
            # Deadline ping parameter cause ping to be executed until count
            # messages are received or deadline is expired
            # Therefore to count messages not of received type we have to
            # simulate deadline parameter limiting the maximum number of
            # transmitted messages
            execute_parameters = _parameters.get_ping_parameters(
                default=parameters,
                deadline=deadline,
                count=min(parameters.count - count,
                          parameters.interval * deadline))

        # Command timeout would typically give ping command additional seconds
        # to safely reach deadline before shell command timeout expires, while
        # in the same time adding an extra verification to forbid using more
        # time than expected considering the time required to make SSH
        # connection and running a remote shell
        try:
            result = execute_ping(parameters=execute_parameters,
                                  ssh_client=ssh_client,
                                  timeout=end_of_time - now,
                                  check=check)
        except sh.ShellError as ex:
            LOG.exception("Error executing ping command")
            output = str(ex.stdout)

        else:
            output = str(result.stdout)

        if output:
            statistics = _statistics.parse_ping_statistics(
                output=output, begin_interval=now,
                end_interval=time.time())

            yield statistics

            transmitted += statistics.transmitted
            received += statistics.received
            undelivered += statistics.undelivered
            count = {None: 0,
                     TRANSMITTED: transmitted,
                     DELIVERED: transmitted - undelivered,
                     UNDELIVERED: undelivered,
                     RECEIVED: received,
                     UNRECEIVED: transmitted - received}[until]

        now = time.time()
        deadline = min(int(end_of_time - now), parameters.deadline)

    if until and count < parameters.count:
        raise _exception.PingFailed(count=count,
                                    expected_count=parameters.count,
                                    timeout=parameters.timeout,
                                    message_type=until)


def execute_ping(parameters, ssh_client=None, check=True, **params):
    if not ssh_client:
        is_cirros_image = params.setdefault('is_cirros_image', False)
        if is_cirros_image:
            raise ValueError("'ssh_client' parameter is required when "
                             "to execute ping on a CirrOS image.")

    command = get_ping_command(parameters)
    result = sh.execute(command=command, ssh_client=ssh_client,
                        timeout=parameters.timeout, check=False, wait=True)

    if check and result.exit_status and result.stderr:
        handle_ping_command_error(error=str(result.stderr))
    return result


def get_ping_command(parameters):
    options = []

    ip_version = parameters.ip_version
    host = parameters.host
    if host:
        try:
            host = netaddr.IPAddress(host)
        except netaddr.core.AddrFormatError:
            # NOTE: host could be an host name not an IP address so
            # this is fine
            LOG.debug("Unable to obtain IP version from host address: %r",
                      host)
        else:
            if ip_version != host.version:
                if ip_version:
                    raise ValueError("Mismatching destination IP version.")
                else:
                    ip_version = host.version
    else:
        raise ValueError("Ping host destination hasn't been specified")

    source = parameters.source
    if source:
        try:
            source = netaddr.IPAddress(source)
        except netaddr.core.AddrFormatError:
            # NOTE: source could be a device name and not an IP address
            # so this is fine
            LOG.debug("Unable to obtain IP version from source address: "
                      "%r", source)
        else:
            if ip_version != source.version:
                if ip_version:
                    raise ValueError("Mismatching source IP version.")
                else:
                    ip_version = source.version
        options += ['-I', source]

    is_cirros_image = parameters.is_cirros_image
    ping_command = 'ping'
    if not ip_version:
        LOG.warning("Unable to obtain IP version from neither source "
                    "or destination IP addresses: assuming IPv4")
        ip_version = constants.IP_VERSION_4

    elif ip_version == constants.IP_VERSION_6:
        if is_cirros_image:
            options += ['-6']
        else:
            ping_command = 'ping6'

    deadline = parameters.deadline
    if deadline > 0:
        options += ['-w', deadline]
        options += ['-W', deadline]

    count = parameters.count
    if count > 0:
        options += ['-c', int(count)]

    payload_size = parameters.payload_size
    packet_size = parameters.packet_size
    if not payload_size and packet_size:
        payload_size = get_icmp_payload_size(package_size=int(packet_size),
                                             ip_version=ip_version)

    if payload_size:
        options += ['-s', int(payload_size)]

    interval = parameters.interval
    if interval > 1:
        options += ['-i', int(interval)]

    fragmentation = parameters.fragmentation
    if fragmentation is False:
        if is_cirros_image:
            msg = ("'is_cirros_image' parameter must be set to False"
                   " when 'fragmention' parameter is False "
                   "(is_cirros_image={!r})").format(is_cirros_image)
            raise ValueError(msg)
        options += ['-M', 'do']

    return [ping_command] + options + [host]


def handle_ping_command_error(error):
    for error in error.splitlines():
        error = error.strip()
        if error:
            prefix = 'ping: '
            if error.startswith('ping: '):
                text = error[len(prefix):]

                prefix = 'bad address '
                if text.startswith(prefix):
                    address = text[len(prefix):].replace("'", '').strip()
                    raise _exception.BadAddressPingError(address=address)

                prefix = 'local error: '
                if text.startswith(prefix):
                    details = text[len(prefix):].strip()
                    raise _exception.LocalPingError(details=details)

                prefix = 'sendto: '
                if text.startswith(prefix):
                    details = text[len(prefix):].strip()
                    raise _exception.SendToPingError(details=details)

                prefix = 'unknown host '
                if text.startswith(prefix):
                    details = text[len(prefix):].strip()
                    raise _exception.UnknowHostError(details=details)

                suffix = ': Name or service not known'
                if text.endswith(suffix):
                    details = text[:-len(suffix)].strip()
                    raise _exception.UnknowHostError(details=details)

                suffix = ': No route to host'
                if text.endswith(suffix):
                    details = text[:-len(suffix)].strip()
                    raise _exception.UnknowHostError(details=details)

                raise _exception.PingError(details=text)


IP_HEADER_SIZE = {4: 20, 6: 40}
ICMP_HEADER_SIZE = {4: 8, 6: 4}


def get_icmp_payload_size(package_size, ip_version):
    """Return the maximum size of ping payload that will fit into MTU."""
    header_size = IP_HEADER_SIZE[ip_version] + ICMP_HEADER_SIZE[ip_version]
    if package_size < header_size:
        message = ("package size {package_size!s} is smaller than package "
                   "header size {header_size!s}").format(
                       package_size=package_size,
                       header_size=header_size)
        raise ValueError(message)
    return package_size - header_size
