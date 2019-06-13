import asyncio
import functools
import json
import sys
from urllib.parse import quote

import aiohttp

from .errors import (
	EmoteDescriptionTooLongError,

	HttpException,
	Forbidden,
	LoginFailure,
	NotFound,
	EmoteExists,
	RequestEntityTooLarge,
	UnsupportedMediaType)
from .utils import sentinel
from . import __version__

# Using code provided by Rapptz
# Copyright © 2015–2017 Rapptz
# https://github.com/Rapptz/discord.py/blob/4aecdea0524e7b481f9750166bf9e9be287ec445/discord/http.py

# by default, quote doesn't quote /, which we don't want.
# quote_plus does, but it also encodes " " as "+", which we don't want.
uriquote = functools.partial(quote, safe='')
del quote

async def json_or_text(response):
	text = await response.text(encoding='utf-8')
	if response.content_type == 'application/json':
		return json.loads(text)
	return text

class Route:
	BASE = 'https://emote-collector.python-for.life/api/v0'

	def __init__(self, method, path, **parameters):
		self.path = path
		self.method = method
		url = self.BASE + self.path
		if parameters:
			self.url = url.format(**{k: uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
		else:
			self.url = url

class HttpClient:
	def __init__(self, token=None, *, loop=None):
		self.token = token
		self.loop = loop or asyncio.get_event_loop()
		user_agent = 'aioec (https://github.com/EmoteCollector/aioec) {0} aiohttp/{1} Python/{2[0]}.{2[1]}'
		self.user_agent = user_agent.format(__version__, aiohttp.__version__, sys.version_info)

		headers = {'User-Agent': self.user_agent}
		if self.token is not None:
			headers['Authorization'] = self.token

		self._session = aiohttp.ClientSession(headers=headers, loop=self.loop)

	def close(self):
		return self._session.close()

	_response_errors = {
		401: lambda response, data: LoginFailure,
		403: Forbidden,
		404: NotFound,
		409: lambda response, data: EmoteExists(response, data['name']),  # HTTP Conflict
		413: lambda response, data: RequestEntityTooLarge(response, data.get('max_size'), data.get('actual_size')),
		415: lambda response, data: UnsupportedMediaType(response)}

	async def request(self, route, **kwargs):
		method = route.method
		url = route.url

		async with self._session.request(method, url, **kwargs) as response:
			data = await json_or_text(response)
			if response.status in range(200, 300):
				return data
			raise self._response_errors.get(response.status, HttpException)(response, data)

	def emotes(self, author_id=None, *, allow_nsfw=True, after=None):
		params = dict(allow_nsfw=_marshal_bool(allow_nsfw))
		if after is not None:
			params['after'] = after

		if author_id is not None:
			return self.request(Route('GET', '/emotes/{author}', author=author_id), params=params)
		return self.request(Route('GET', '/emotes'), params=params)

	def emote(self, name):
		return self.request(Route('GET', '/emote/{name}', name=name))

	def login(self):
		return self.request(Route('GET', '/login'))

	async def create(self, *, name, url=None, image: bytes = None):
		if bool(url) == bool(image):
			raise InvalidArgument('exactly one of url or image is required')

		if url:
			return await self.request(Route('PUT', '/emote/{name}/{url}', name=name, url=url))

		if image:
			return await self.request(Route('PUT', '/emote/{name}', name=name), data=image)

	async def edit(self, name_, *, name=None, description=sentinel):
		data = {}

		# we perform this dance so that the caller can run it like edit_emote('foo', name='bar')
		new_name = name
		name = name_

		if new_name is not None:
			data['name'] = new_name
		if description is not sentinel:  # None is an allowed value for description
			data['description'] = description

		try:
			return await self.request(Route('PATCH', '/emote/{name}', name=name), json=data)
		except RequestEntityTooLarge as exception:
			raise EmoteDescriptionTooLongError(
				max_length=exception.max_size,
				actual_length=exception.actual_size) from None

	def delete(self, name):
		return self.request(Route('DELETE', '/emote/{name}', name=name))

	def search(self, query, *, allow_nsfw=True):
		params = dict(allow_nsfw=_marshal_bool(allow_nsfw))
		return self.request(Route('GET', '/search/{query}', query=query), params=params)

	def popular(self, author_id=None, *, allow_nsfw=True):
		params = dict(allow_nsfw=_marshal_bool(allow_nsfw))
		if author_id is not None:
			return self.request(Route('GET', '/popular/{author}', author=author_id), params=params)
		return self.request(Route('GET', '/popular'), params=params)

_marshal_bool = lambda x: 'true' if x else 'false'
