from .http import HttpClient
from .emote import Emote
from . import utils

class Client:
	def __init__(self, token=None, *, loop=None):
		self._http = HttpClient(token=token, loop=loop)

	def _new_emote(self, data):
		return Emote(data=data, http=self._http)

	def close(self):
		return self._http.close()

	async def emote(self, name):
		return self._new_emote(await self._http.emote(name))

	async def emotes(self, author_id=None, *, allow_nsfw=True, after=None):
		if after is None:
			async for emote in self._all_emotes(author_id, allow_nsfw=allow_nsfw):
				yield emote
			return

		for emote in map(self._new_emote, await self._http.emotes(author_id, allow_nsfw=allow_nsfw, after=after)):
			yield emote

	async def _all_emotes(self, author_id=None, *, allow_nsfw=True):
		batch = await self._http.emotes(author_id, allow_nsfw=allow_nsfw)
		while batch:
			for obj in batch:
				yield self._new_emote(obj)
			batch = await self._http.emotes(author_id, allow_nsfw=allow_nsfw, after=batch[-1]['name'])

	async def search(self, query, *, allow_nsfw=True):
		return list(map(self._new_emote, await self._http.search(query, allow_nsfw=allow_nsfw)))

	async def popular(self, author_id=None, allow_nsfw=True):
		return list(map(self._new_emote, await self._http.popular(author_id, allow_nsfw=allow_nsfw)))

	async def login(self):
		"""Checks that your token is correct.

		Returns the user ID associated with your token.
		"""

		return int(await self._http.login())

	async def create(self, *, name, url=None, image=None):
		"""Create an emote. Exactly one of url or image is required.

		Raises:
			:class:`RequestEntityTooLarge`: the emote exceeded 16 MiB, or took too long to resize.
			:class:`UnsupportedMediaType`: the emote was not a PNG, GIF, or JPEG.
		"""
		return self._new_emote(await self._http.create(name=name, url=url, image=image))

	async def edit(self, name_, *, name=None, description=utils.sentinel):
		return self._new_emote(await self._http.edit(name_, name=name, description=description))

	async def delete(self, name):
		return self._new_emote(await self._http.delete(name))

	async def __aenter__(self):
		return self

	def __aexit__(self, *_):
		return self.close()
