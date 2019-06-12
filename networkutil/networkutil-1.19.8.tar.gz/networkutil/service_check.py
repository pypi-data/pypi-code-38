# encoding: utf-8

import socket
import logging_helper

logging = logging_helper.setup_logging()


def _check_service_availability(host,
                                port,
                                alt_ports=None):

    """ Checks the availability of a specific service
        by attempting to connect a socket to the services known port(s).

    :param host:        (string)        The hostname/ip where the service is hosted.
    :param port:        (int)           The primary port for the service.
    :param alt_ports:   (list of ints)  Any known alternate ports to probe if the primary fails.
    :return:            (int, None)     First port successfully connected to, if not connection then None.
    """

    # result param
    result = None

    # Ensure alt ports is a list and setup last_port
    if alt_ports is None:
        alt_ports = []
        last_port = None

    else:
        last_port = alt_ports[-1]

    # Create socket to be used for testing connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set timeout of the
    s.settimeout(0.25)

    try:
        # Attempt connection
        s.connect((host, port))
        result = port

    except socket.error as err:
        logging.debug(u'Failed to connect to port {p}: {e}'.format(p=port,
                                                                   e=err))

        # if we still have ports to check attempt next connection
        if last_port is not None and port is not last_port and alt_ports:
            logging.debug(u'Attempting connection on alternate port ({port})'.format(port=alt_ports[0]))

            connect_kwargs = {
                u'host': host,
                u'port': alt_ports[0],
            }

            if len(alt_ports) > 1:
                connect_kwargs[u'alt_ports'] = alt_ports[1:]

            result = _check_service_availability(**connect_kwargs)

    finally:
        s.close()

    return result


def check_service_availability(host,
                               port,
                               alt_ports=None):

    """ Checks the availability of a specific service
        by attempting to connect a socket to the services known port(s).

    :param host:        (string)        The hostname/ip where the service is hosted.
    :param port:        (int)           The primary port for the service.
    :param alt_ports:   (list of ints)  Any known alternate ports to probe if the primary fails.
    :return:            (int, None)     First port successfully connected to, if not connection then None.
    """

    primary_port = port
    secondary_ports = alt_ports

    # Check availability
    result = _check_service_availability(host=host,
                                         port=port,
                                         alt_ports=alt_ports)

    if result is None:
        logging.error(u'Failed to connect to any ports '
                      u'(Primary: {p}; Alternate: {a})'.format(p=primary_port,
                                                               a=secondary_ports))

    return result
