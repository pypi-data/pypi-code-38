# Using code provided by Rapptz
# Copyright © 2015–2017 Rapptz
# https://github.com/Rapptz/discord.py/blob/f25091efe1281aebe70189c61f9cac405b21a72f/discord/errors.py

class AioEcError(Exception):
	"""
	Base exception type for the library.
	Can be used to catch any exception raised by this library.
	"""
	pass

class ClientException(AioEcError):
	"""Exception that's thrown when an operation in the :class:`Client` fails.

	These are usually for exceptions that happened due to user input.
	"""
	pass

class LoginFailure(ClientException):
	"""Improper or incorrect token has been passed"""
	def __init__(self):
		super().__init__('Invalid or incorrect token has been passed.')

class InvalidArgument(ClientException, ValueError, TypeError):
	"""Exception that’s thrown when an argument to a function is invalid some way
	(e.g. wrong value or wrong type)."""
	pass

class EmoteDescriptionTooLongError(InvalidArgument):
	"""Exception that's thrown when the emote description passed exceeds the limit."""
	def __init__(self, *, max_length, actual_length):
		self.max_length = max_length
		self.actual_length = actual_length
		super().__init__(
			'Emote description too long: max={}, got {}'.format(self.max_length, self.actual_length))

class HttpException(AioEcError):
	"""Exception that's thrown when an HTTP request operation fails.

	Attributes
	------------
	response: aiohttp.ClientResponse
		The response of the failed HTTP request. This is an
		instance of `aiohttp.ClientResponse`__. In some cases
		this could also be a ``requests.Response``.

		__ http://aiohttp.readthedocs.org/en/stable/client_reference.html#aiohttp.ClientResponse

	text: :class:`str`
		The text of the error. Could be an empty string.
	status: :class:`int`
		The status code of the HTTP request.
	code: :class:`int`
		The Discord specific error code for the failure.
	"""

	def __init__(self, response, message):
		self.response = response
		self.status = response.status
		if isinstance(message, dict):
			self.text = message.get('message')
		else:
			self.text = message

		fmt = '{0.reason} (status code: {0.status})'
		if self.text:
			fmt = fmt + ': {1}'

		super().__init__(fmt.format(self.response, self.text))

class Forbidden(HttpException):
	"""Exception that's thrown for when status code 403 occurs.

	Subclass of :exc:`HttpException`
	"""
	pass

class NotFound(HttpException):
	"""Exception that's thrown for when status code 404 occurs.

	Subclass of :exc:`HttpException`
	"""
	pass

class EmoteExists(HttpException):
	"""Exception that's thrown for when status code 409 occurs.
	This happens when an emote already exists with the given name and you tried to create a new one
	with that name.

	Subclass of :exc:`HttpException`
	"""
	def __init__(self, response, name):
		self.name = name
		super().__init__(response, 'An emote called {} already exists'.format(name))

class RequestEntityTooLarge(HttpException):
	"""Exception that's thrown for when status code 413 occurs.
	This happens when an image that is passed is too big, a URL is passed that refers to an image
	that's too big, or a description was passed that's too long.

	Subclass of :exc:`HttpException`
	"""
	def __init__(self, response, max_size=None, actual_size=None):
		self.max_size = max_size
		self.actual_size = actual_size
		if max_size and actual_size:
			super().__init__(
				response,
				'Data exceeded maximum size ({}), actual size {}'.format(max_size, actual_size))
		elif max_size:
			super().__init__(
				response,
				'Data exceeded maximum size ({})'.format(max_size))
		elif actual_size:
			super().__init__(
				response,
				'Data exceeded maximum size, actual size {}'.format(actual_size))

class UnsupportedMediaType(HttpException):
	"""Exception that's thrown for when status code 419 occurs.
	This happens when an image that's passed is of an invalid format,
	or a URL is passed which refers to an image that is of an invalid format.

	Valid formats are JPEG, GIF, and PNG.

	Subclass of :exc:`HttpException`
	"""
	def __init__(self, response):
		super().__init__(response, 'The emote image passed is not a JPEG, GIF, or PNG.')
