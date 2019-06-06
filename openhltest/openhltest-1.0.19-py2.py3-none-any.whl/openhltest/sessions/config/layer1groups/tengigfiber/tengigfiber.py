from openhltest_client.base import Base


class TenGigFiber(Base):
	"""TBD
	"""
	YANG_NAME = 'ten-gig-fiber'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"AdvertiseIeee": "advertise-ieee"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(TenGigFiber, self).__init__(parent)

	@property
	def AdvertiseIeee(self):
		"""TBD

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('advertise-ieee')

	def update(self, AdvertiseIeee=None):
		"""Update the current instance of the `ten-gig-fiber` resource

		Args:
			AdvertiseIeee (boolean): TBD
		"""
		return self._update(locals())

