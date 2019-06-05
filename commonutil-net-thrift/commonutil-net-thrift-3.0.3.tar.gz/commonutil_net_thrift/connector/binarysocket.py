# -*- coding: utf-8 -*-
"""
Connector for socket transport with binary protocol
"""

import logging

from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol

from commonutil_net_thrift.client.types import ClientSetup
from commonutil_net_thrift.connector.exceptions import ClientCheckException

_log = logging.getLogger(__name__)


def _close_transport(transport):
	try:
		transport.close()
	except Exception:
		pass


def binary_socket_connector(client_setup: ClientSetup, host: str, port: int, timeout_seconds: float = 3):
	"""
	Connector callable for making connection with Binary Protocol over Socket.
	"""
	transport = TSocket.TSocket(host, port)
	if timeout_seconds:
		transport.setTimeout(timeout_seconds * 1000.0)
	protocol = TBinaryProtocol.TBinaryProtocol(transport)
	client = client_setup.client_class(protocol)
	transport.open()  # connect
	if client_setup.check_callable:
		try:
			if not client_setup.check_callable(client):
				_log.error("failed on check connected client: host=%r, port=%r", host, port)
				raise ClientCheckException()
		except Exception as e:
			_close_transport(transport)
			_log.exception("caught exception on check connected client: host=%r, port=%r, exception=%r", host, port, e)
			raise
	if client_setup.prepare_callable:
		try:
			client_setup.prepare_callable(client)
		except Exception as e:
			_close_transport(transport)
			_log.exception("caught exception on preparing connected client for use: host=%r, port=%r, exception=%r", host, port, e)
			raise
	return (client, transport)
