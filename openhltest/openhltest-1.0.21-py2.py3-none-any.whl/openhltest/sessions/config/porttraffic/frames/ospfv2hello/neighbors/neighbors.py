from openhltest_client.base import Base


class Neighbors(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/port-traffic/frames/ospfv2-hello/neighbors resource.
	"""
	YANG_NAME = 'neighbors'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Neighbors, self).__init__(parent)

	@property
	def NeighborsId(self):
		"""Neighbor ID

		Get an instance of the NeighborsId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.neighbors.neighborsid.neighborsid.NeighborsId)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.neighbors.neighborsid.neighborsid import NeighborsId
		return NeighborsId(self)._read()

	@property
	def Name(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `neighbors` resource(s). Returns all `neighbors` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `neighbors` resource

		Args:
			Name (string): TBD
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `neighbors` resource

		"""
		return self._delete()

