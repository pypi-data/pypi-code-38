import pandas


class DataReader:
	def __init__(self, default_values_path):
		self.process = None

		self.input_data = {}
		self.input_data_processed = {}
		self.suppress_calculation = False

		self.warnings = []
		self.errors = []

		# default values --------------------------------------------------------------------------
		self.variables_set_to_default = []
		with open(default_values_path, 'r') as f:
			self.default_values = {k: v for (k, v) in [x.replace('\n', '').split(',') for x in f.readlines()[1:]]}

		for variable, default_value in self.default_values.items():
			try:
				new_default_value = float(default_value)
			except ValueError:
				pass
			else:
				if int(new_default_value) == new_default_value:
					new_default_value = int(new_default_value)
				self.default_values.update({variable: new_default_value})

	def message_key_error(self, error: KeyError, additional_message: str = '') -> str:
		return 'KeyError ({}): missing key {} in input_data dict. Setting default value.{}'.format(self.process, error, additional_message)

	def message_key_error_crucial(self, error: KeyError) -> str:
		return 'KeyError ({}): missing crucial key {} in input_data dict. Calculation suppressed.'.format(self.process, error)

	def message_value_error(self, variable: str, wrong_value, additional_message: str = '') -> str:
		return 'ValueError ({}): wrong value \'{}\' for variable \'{}\'. Setting default value. {}'.format(self.process, wrong_value, variable, additional_message)

	def message_type_error(self, variable: str, wrong_value, additional_message: str = '') -> str:
		return 'TypeError ({}): wrong type \'{}\' for variable \'{}\'. Setting default value. {}'.format(self.process, type(wrong_value), variable, additional_message)

	def message_choice_error(self, variable, wrong_value, additional_message: str = ''):
		return 'ChoiceError ({}): value \'{}\' not found in possible choices for variable \'{}\'. Setting default value. {}'.format(self.process, wrong_value, variable, additional_message)

	def message_attribute_error(self, variable, error, additional_message: str = ''):
		return 'AttributeError ({}): {}. Variable \'{}\'. Setting default value. {}'.format(self.process, error, variable, additional_message)

	def handle_exceptions(self, exceptions_handler: list, variable: str, error: Exception, wrong_value, additional_message: str = None):
		if isinstance(error, ValueError):
			exceptions_handler.append(self.message_value_error(variable=variable, wrong_value=wrong_value, additional_message=additional_message))
		elif isinstance(error, TypeError):
			exceptions_handler.append(self.message_type_error(variable=variable, wrong_value=wrong_value, additional_message=additional_message))
		else:
			exceptions_handler.append('Unhandled exception thrown: {}'.format(error))

	def get_value(self, variable: str, exceptions_handler: list, is_crucial: bool = False, get_error: bool = False, new_name=None, set_default=True):
		name = variable if new_name is None else new_name
		is_error = False
		value = None

		try:
			value = self.input_data[variable]
		except KeyError as kE:
			is_error = True

			if is_crucial:
				exceptions_handler.append(self.message_key_error_crucial(error=kE))
				self.suppress_calculation = True
			else:
				if set_default:
					value = self.set_default_value(name)
				exceptions_handler.append(self.message_key_error(error=kE))

		if get_error:
			return value, is_error
		else:
			return value

	def get_str(self, variable: str, exceptions_handler: list, new_name: str = None, set_lowercase: bool = False, is_crucial: bool = False):
		name = variable if new_name is None else new_name
		value, is_error = self.get_value(variable=variable, exceptions_handler=exceptions_handler, is_crucial=is_crucial, get_error=True, new_name=new_name)

		if not is_error:
			try:
				value = str(value)
			except (ValueError, TypeError) as error:
				self.handle_exceptions(exceptions_handler=exceptions_handler, variable=variable, error=error, wrong_value=value)

				if is_crucial:
					value = None
					self.suppress_calculation = True
				else:
					value = self.set_default_value(name)
			else:
				if set_lowercase:
					value = value.lower()

		return value

	def set_str(self, variable: str, exceptions_handler: list, new_name: str = None, set_lowercase: bool = False, is_crucial: bool = False):
		name = variable if new_name is None else new_name
		value = self.get_str(variable, exceptions_handler, new_name, set_lowercase, is_crucial)
		self.input_data_processed.update({name: value})

	def get_categorical(self, variable: str, choices: list, exceptions_handler: list, force_type=None, new_name: str = None, set_lowercase: bool = False, is_crucial: bool = False):
		name = variable if new_name is None else new_name
		value, is_error = self.get_value(variable=variable, exceptions_handler=exceptions_handler, is_crucial=is_crucial, get_error=True, new_name=new_name)

		if not is_error:
			try:
				if set_lowercase:
					value = str(value).lower()
				if force_type is not None:
					value = force_type(value)
			except ValueError:
				is_error = True
				exceptions_handler.append('ValueError ({}): impossible to force type {} on {}. Setting default value {}'.format(self.process, force_type, self.input_data[variable], value))
			if value not in choices:
				is_error = True
				exceptions_handler.append(self.message_choice_error(variable=name, wrong_value=value))

			if is_error:
				if is_crucial:
					value = None
					self.suppress_calculation = True
				else:
					value = self.set_default_value(name)

		return value

	def set_categorical(self, variable: str, choices: list, exceptions_handler: list, force_type=None, new_name: str = None, set_lowercase: bool = False, is_crucial: bool = False):
		name = variable if new_name is None else new_name
		value = self.get_categorical(variable, choices, exceptions_handler, force_type, new_name, set_lowercase, is_crucial)
		self.input_data_processed.update({name: value})

	def get_numeric(self, variable: str, exceptions_handler: list, numeric_type: type = int, min_value: int = None, max_value: int = None, bucket: int = None, new_name: str = None, is_crucial=False):
		name = variable if new_name is None else new_name
		value, is_error = self.get_value(variable=variable, exceptions_handler=exceptions_handler, is_crucial=is_crucial, get_error=True, new_name=new_name)

		if not is_error:
			try:
				value = numeric_type(value)
			except (ValueError, TypeError) as error:
				is_error = True
				self.handle_exceptions(exceptions_handler=exceptions_handler, variable=name, error=error, wrong_value=value)
			else:
				if value != bucket:
					if min_value is not None:
						value = max(min_value, value)
					if max_value is not None:
						value = min(max_value, value)
			if is_error:
				if is_crucial:
					value = None
					self.suppress_calculation = True
				else:
					value = self.set_default_value(name)

		return value

	def set_numeric(self, variable: str, exceptions_handler: list, numeric_type: type = int, min_value: int = None, max_value: int = None, bucket: int = None, new_name: str = None, is_crucial=False):
		name = variable if new_name is None else new_name
		value = self.get_numeric(variable, exceptions_handler, numeric_type, min_value, max_value, bucket, new_name, is_crucial)
		self.input_data_processed.update({name: value})

	def get_date(self, variable: str, exceptions_handler: list, new_name: str=None, is_crucial: bool=False, timezone: str='Europe/London'):
		name = variable if new_name is None else new_name
		date, is_error = self.get_value(variable=variable, exceptions_handler=exceptions_handler, is_crucial=is_crucial, get_error=True, new_name=new_name)

		if not is_error:
			try:
				date = pandas.to_datetime(date)
				if date is None:
					raise ValueError
			except (ValueError, AttributeError) as error:
				is_error = True
				if isinstance(error, ValueError):
					self.warnings.append(self.message_value_error(variable=name, wrong_value=date))
				if isinstance(error, AttributeError):
					self.warnings.append(self.message_attribute_error(variable=name, error=date))

			if is_error:
				if is_crucial:
					date = None
					self.suppress_calculation = True
				else:
					date = self.set_default_value(name)
			else:
				date = date.tz_convert(timezone)

		return date

	def set_date(self, variable: str, exceptions_handler: list, new_name: str = None, is_crucial=False, timezone: str='Europe/London'):
		name = variable if new_name is None else new_name
		date = self.get_date(variable=variable, exceptions_handler=exceptions_handler, new_name=new_name, is_crucial=is_crucial, timezone=timezone)
		self.input_data_processed.update({name: date})

	def set_default_value(self, variable):
		try:
			default_value = self.default_values[variable]
		except KeyError:
			raise KeyError('Missing default value for variable {}'.format(variable))
		else:
			self.variables_set_to_default.append(variable)

		return default_value

	def reset(self):
		self.process = None

		self.input_data = {}
		self.input_data_processed = {}
		self.variables_set_to_default = []

		self.warnings = []
		self.errors = []

		self.suppress_calculation = False
