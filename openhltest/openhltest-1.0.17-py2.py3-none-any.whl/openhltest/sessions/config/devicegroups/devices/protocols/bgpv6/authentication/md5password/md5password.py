from openhltest_client.base import Base


class Md5Password(Base):
	"""Type a value to be used as a secret MD5 Key for authentication.
	This field is available only if you select MD5 as the type of Authentication.
	"""
	YANG_NAME = 'md5-password'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"ValueList": "value-list", "Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "String": "string"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Md5Password, self).__init__(parent)

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
		"""Update the current instance of the `md5-password` resource

		Args:
			PatternFormat (string): Refine this leaf value with a regex
			PatternType (enumeration): TBD
			Single (string): TBD
			String (string): Vendor specific string patterns
			ValueList (string): TBD
		"""
		return self._update(locals())

