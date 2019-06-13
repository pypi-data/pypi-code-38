from . import utils

class BaseEmote:
	def __new__(cls, *, data):
		self = super().__new__(cls)

		for key, value in data.items():
			if key in {'id', 'author'}:
				value = int(value)

			if key in {'created', 'modified'} and value is not None:
				value = utils.epoch_time(value)

			setattr(self, '_' + key, value)

		return self

	_fields = (
		'_name',
		'_id',
		'_author',
		'_animated',
		'_created',
		'_modified',
		'_preserve',
		'_description',
		'_usage',
		'_nsfw',
	)

	for field in _fields:
		def getter(self, field=field):
			return getattr(self, field)

		public_name = field[1:]
		getter.__name__ = public_name
		vars()[public_name] = property(getter)

	del field, getter, public_name

	@property
	def usage(self):
		return getattr(self, '_usage', None)

	@property
	def url(self):
		return 'https://cdn.discordapp.com/emojis/{0.id}.{ext}?v=1'.format(
			self,
			ext='gif' if self.animated else 'png')

	@property
	def _a(self):
		return 'a' if self.animated else ''

	@property
	def is_nsfw(self):
		return self.nsfw != 'SFW'

	@property
	def as_reaction(self):
		return '{0._a}:{0.name}:{0.id}'.format(self)

	def __str__(self):
		return '<{0._a}:{0.name}:{0.id}>'.format(self)

	def __repr__(self):
		return (
			'{0.__module__}.{0.__class__.__qualname__}'
			'<name={0.name!r}, id={0.id}, animated={0.animated}>'.format(self))

class Emote(BaseEmote):
	__slots__ = frozenset(('_http',))

	def __new__(cls, *, data, http):
		self = super().__new__(cls, data=data)
		self._http = http

		return self

	def _new_emote(self, data):
		return type(self)(http=self._http, data=data)

	async def delete(self):
		return self._new_emote(await self._http.delete(self.name))

	async def edit(self, *, name=None, description=utils.sentinel):
		return self._new_emote(await self._http.edit(self.name, name=name, description=description))
