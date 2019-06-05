# -*- coding: utf-8 -*-
"""
Round-robin client
"""

from contextlib import closing
from threading import Lock
from typing import Any, Callable, Sequence, Tuple
import logging

from thrift.transport.TTransport import TTransportBase

from commonutil_net_thrift.client.types import ClientSetup

_log = logging.getLogger(__name__)


class RoundRobinClient:
	"""
	RoundRobinClient wraps given client class to provide auto re-connect in
	round robin manner.
	"""

	__slots__ = (
			"_client_setup",
			"_connector_callable",
			"_server_locations",
			"_connect_kwds",
			"_expose_exceptions",
			"_next_server_index",
			"_client_callables",
			"_client_lock",
			"_client",
			"_transport",
	)

	def __init__(
			self,
			client_setup: ClientSetup,
			connector_callable: Callable[..., Tuple[Any, TTransportBase]],
			server_locations: Sequence[Any],
			timeout_seconds: float = 3,
			*args,
			**kwds,
	):
		super().__init__(*args, **kwds)
		self._client_setup = client_setup
		self._connector_callable = connector_callable
		self._server_locations = server_locations
		self._connect_kwds = {
				"timeout_seconds": timeout_seconds,
		}
		self._expose_exceptions = client_setup.expose_exceptions
		self._next_server_index = 0
		self._client_callables = ()
		self._client_lock = Lock()
		self._client = None
		self._transport = None

	def __enter__(self):
		return self

	def __exit__(self, *exc_info):
		self.close()

	def open(self):
		return closing(self)

	def close(self):
		try:
			self._transport.close()
		except Exception:
			pass
		self._client = None
		self._transport = None
		self._client_callables = ()

	def _reconnect(self):
		self.close()
		remain_count = len(self._server_locations)
		srv_loc = None
		while remain_count > 0:
			remain_count = remain_count - 1
			try:
				srv_loc = self._server_locations[self._next_server_index]
				self._next_server_index = (self._next_server_index + 1) % len(self._server_locations)
				self._client, self._transport = self._connector_callable(self._client_setup, *srv_loc, **self._connect_kwds)
				return
			except Exception as e:
				_log.exception("failed on connecting to %r: %r", srv_loc, e)

	def _invoke_with(self, invoke_impl_callable: Callable, method_ref: Any, *args, **kwds):
		remain_count = len(self._server_locations)
		while remain_count > 0:
			remain_count = remain_count - 1
			try:
				with self._client_lock:
					return invoke_impl_callable(method_ref, *args, **kwds)
			except Exception as e:
				if self._expose_exceptions and isinstance(e, self._expose_exceptions):
					raise
				_log.error("invoke (ref=%r) failed (remain-attempt=%r): %r", method_ref, remain_count, e)
				self._reconnect()
		with self._client_lock:
			return invoke_impl_callable(method_ref, *args, **kwds)

	def _invoke_by_name_impl(self, method_name, *args, **kwds):
		if not self._client:
			self._reconnect()
		client_callable = getattr(self._client, method_name)
		return client_callable(*args, **kwds)

	def _invoke_by_name(self, method_name: str, *args, **kwds):
		"""
		(protected) _invoke_by_name call client method via lookuping up client
		method callable with `getattr()`.
		"""
		return self._invoke_with(self._invoke_by_name_impl, method_name, *args, **kwds)

	def _invoke_by_index_impl(self, callable_index, *args, **kwds):
		if not self._client:
			self._reconnect()
		client_callable = self._client_callables[callable_index]
		return client_callable(*args, **kwds)

	def _invoke_by_index(self, callable_index: int, *args, **kwds):
		"""
		(protected) _invoke_by_index call client method via cached client
		callables.

		The client callables must cached into `_client_callables` property
		with `ClientSetup.prepare_callable`.
		"""
		return self._invoke_with(self._invoke_by_index_impl, callable_index, *args, **kwds)
