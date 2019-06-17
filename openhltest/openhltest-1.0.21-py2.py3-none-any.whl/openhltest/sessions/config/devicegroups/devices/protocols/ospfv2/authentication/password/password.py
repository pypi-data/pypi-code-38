from openhltest_client.base import Base


class Password(Base):
	"""Authentication password.
	"""
	YANG_NAME = 'password'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"ValueList": "value-list", "Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "String": "string"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Password, self).__init__(parent)

	@property
	def PatternFormat(self):
		"""Refine this leaf value with a regex

		Getter Returns:
			string
		"""
		return self._get_value('pattern-format')

	@property
	def PatternType(self):
		"""TBD

		Getter Returns:
			SINGLE | STRING | VALUE_LIST

		Setter Allows:
			SINGLE | STRING | VALUE_LIST

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('pattern-type')

	@property
	def Single(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('single')

	@property
	def String(self):
		"""Vendor specific string patterns

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('string')

	@property
	def ValueList(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('value-list')

	def update(self, PatternFormat=None, PatternType=None, Single=None, String=None, ValueList=None):
		"""Update the current instance of the `password` resource

		Args:
			PatternFormat (string): Refine this leaf value with a regex
			PatternType (enumeration): TBD
			Single (string): TBD
			String (string): Vendor specific string patterns
			ValueList (string): TBD
		"""
		return self._update(locals())

