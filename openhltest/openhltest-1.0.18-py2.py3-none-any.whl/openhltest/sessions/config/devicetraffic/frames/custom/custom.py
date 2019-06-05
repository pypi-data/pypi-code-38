from openhltest_client.base import Base


class Custom(Base):
	"""TBD
	"""
	YANG_NAME = 'custom'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"PayloadType": "payload-type"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Custom, self).__init__(parent)

	@property
	def Payload(self):
		"""TBD

		Get an instance of the Payload class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.custom.payload.payload.Payload)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.custom.payload.payload import Payload
		return Payload(self)._read()

	@property
	def PayloadType(self):
		"""TBD

		Getter Returns:
			INCREMENT_BYTE | DECREMENT_BYTE | INCREMENT_WORD | DECREMENT_WORD | CRPAT | CJPAT | RANDOM | CUSTOM

		Setter Allows:
			INCREMENT_BYTE | DECREMENT_BYTE | INCREMENT_WORD | DECREMENT_WORD | CRPAT | CJPAT | RANDOM | CUSTOM

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('payload-type')

	def update(self, PayloadType=None):
		"""Update the current instance of the `custom` resource

		Args:
			PayloadType (enumeration): TBD
		"""
		return self._update(locals())

