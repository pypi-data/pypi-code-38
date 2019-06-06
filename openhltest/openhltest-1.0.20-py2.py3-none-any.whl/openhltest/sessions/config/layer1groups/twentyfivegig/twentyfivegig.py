from openhltest_client.base import Base


class TwentyFiveGig(Base):
	"""TBD
	"""
	YANG_NAME = 'twenty-five-gig'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"AdvertiseIeee": "advertise-ieee"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(TwentyFiveGig, self).__init__(parent)

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
		"""Update the current instance of the `twenty-five-gig` resource

		Args:
			AdvertiseIeee (boolean): TBD
		"""
		return self._update(locals())

