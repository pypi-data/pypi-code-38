"""
Business logic of the main module.
"""

"""
Generic library imports
"""
from pprint import pprint
"""
Class imports
"""
from pyshellwrapper.parser import Parser
"""
Functional imports
"""
import pyshellwrapper.defs as defs

class PyShellWrapper:
	def __init__(self, blueprint, lib=None, **kwargs):
		"""
		Each blueprint can contain multiple libraries so further
		distinguishing needs to take place in form of lib_name providing
		actual name
		"""
		self.blueprint_name = blueprint
		self.lib_name = lib
		"""
		Library life cycle can altered to resetting after
		each call of 'construct' method
		"""
		try:
			self.reset_after_construct = kwargs['reset_after_construct']
		except KeyError:
			self.reset_after_construct = True
		"""
		Internal structure for storing flags
		"""
		self.structure = {
			'fixed'		: {
				'already_set'	: [],
				'transformed'	: []
			},
			'variable'	: {},
			'aux': []
		}

		"""
		TODO: this variable is not needed for multiple variable 
		flags but this version only support 1
		"""
		self.is_variable_set = False

		"""
		Fetch correct blueprint for command 
		"""
		self._get_blueprint()

	"""
	PUBLIC methods
	"""
	def list_flags(self):
		"""
		Info for user which flags are ready to be used
		"""
		return list(self.flags_match_table.keys())

	def construct(self):
		"""
		Transform abstract data structure to list used by subprocess 
		"""
		output_buffer = []
		"""
		Add command
		"""
		output_buffer += [self.lib_name if self.lib_name else self.blueprint_name]
		"""
		Add fixed
		"""
		output_buffer += self.structure['fixed']['transformed']
		aux = self.structure['aux']
		"""
		Add variable
		"""
		variables = self._add_variable()
		if len(variables):
			for var in variables:
				yield output_buffer + var + aux
		else:
			yield output_buffer + aux
		"""
		Cleanup after construction
		"""
		if self.reset_after_construct:
			self.structure['fixed']['already_set'] = []
			self.structure['fixed']['transformed'] = []
		

	def set_from_routine(self, routine_file):
		parser = Parser('routine', routine_file)

		pass

	def set_fixed(self, **kwargs):
		for flag, opts in kwargs.items():
			"""
			Setting a flag is only allowed once
			"""
			already_set = self.structure['fixed']['already_set']
			if flag in already_set:
				raise ValueError('Flag \'{}\' is already set, fixed flags can only be set once.'.format(flag))
			else:
				already_set.append(flag)
			"""
			Find corresponding partition of the blueprint and 
			transform flag accordingly 
			"""
			flag_blueprint = self._match_flag(flag)
			self.structure['fixed']['transformed'] += self._transform_flag(flag_blueprint, opts)


	def set_variable(self, **kwargs):
		for flag, opts in kwargs.items():
			"""
			Support only for one variable flag
			"""
			if not self.is_variable_set or self.is_variable_set == flag:

				self.is_variable_set = 'tiles'
				"""
				Check if flag is defined
				"""
				self._match_flag(flag)
				"""
				Store flag opts
				"""
				try:
					self._store_variable(flag, opts)
				except KeyError:
					self.structure['variable'][flag] = []
					self._store_variable(flag, opts)
			else:
				raise IndexError('This version only support one variable flag.')

	def set_auxiliary(self, *args):
		for arg in args:
			if self._is_array(arg):
				for a in arg:
					self.structure['aux'].append(a)
			else:
				self.structure['aux'].append(arg)

	"""
	PRIVATE methods
	"""
	def _store_variable(self, flag, payload):
		flag_store = self.structure['variable'][flag]

		if isinstance(payload, list):
			flag_store += payload
		else:
			flag_store.append(payload)

	def _add_variable(self):
		ret_opts = []
		for flag, opts_list in self.structure['variable'].items():
			flag_blueprint = self._match_flag(flag)

			for opts in opts_list:
				ret_opts.append(self._transform_flag(flag_blueprint, opts))

		return ret_opts


	def _set_variable_single(self, flag_blueprint, opts):
		flag_blueprint = self._match_flag(flag)
		"""
		First thing to decide is whenever single or more values
		were supplied
		"""
		items_count = flag_blueprint['format']['number']

		"""
		Check for easiest case, only one primitive value 
		"""
		if self._is_primitive(opts):
			self._transform_flag(flag_blueprint, opts)
		else:
			"""
			Array is single value, list means more expansion.
			But arrays can be nested.
			"""
			if self._is_array(opts):
				"""
				Nested array, flag with list option
				"""
				if type(opts[0]) == self._is_array(opts):
					"""
					TODO: address list in next version
					"""
					pass
				else:
					self._transform_flag(flag_blueprint, opts)
			else:
				for opt in opts:
					self._transform_flag(flag_blueprint, opt)


		if items_count > 1:
				"""
				Multiple values, can be in nested list
				"""
				pass
				#print('multiple')

		else:
			"""
			Value is primitive data type, assign can take place
			"""
			pass
			#print(opts)
			#print(self._transform_flag(flag_blueprint, opts))
			#print('single')


	def _get_blueprint(self):
		parser = Parser('blueprint', self.blueprint_name, self.lib_name)
		if not parser.parse():
			return False
		"""
		If there are multiple libraries in blueprint correct index of 
		library must be found to later enable addressing of flag opts
		"""
		self.program_indexes = parser.get_libraries()
		if not self.program_indexes:
			self.blueprint_index = 0
		else:
			self.blueprint_index = self.program_indexes.index(self.lib_name)
		"""
		Get all flags/opts from file
		"""
		self.flags_match_table = parser.get_flags()
		if not self.flags_match_table:
			raise ValueError()

		return True

	def _transform_flag(self, flag_blueprint, opts):
		"""
		Take input flag and transform it to the desired format
		described in blueprint
		"""
		transform_buffer 		= []
		"""
		Mandatory parts of blueprint as local variable for 
		more readable code
		"""
		flag 		= flag_blueprint['flag']
		unifier 	= flag_blueprint['unifier']
		opt_format 	= flag_blueprint['format']
		"""
		Opts are the most important part of the transformation because
		they need to put into the right format or even concatenated to
		a list hence they are first to address
		"""
		if 'list' in flag_blueprint['format']:
			transformed_opt = None
		else:
			transformed_opt = self._transform_opts(flag_blueprint['format'], opts)


		if transformed_opt:
			"""
			Handle unifier
			"""		
			if unifier:
				transform_buffer.append('{}{}{}'.format(flag, unifier, transformed_opt))
			else:
				"""
				Handle flag
				"""
				if flag:
					transform_buffer.append(flag)
				transform_buffer.append(transformed_opt)
		
		return transform_buffer


	def _transform_opts(self, opts_blueprint, opts):
		opts_preset = opts_blueprint['preset']
		opts_preset_type = type(opts_preset)

		
		if opts_preset_type == str:
			"""
			String means matching of predefined presets
			"""
			if opts_preset == '1':
				return opts
			else:
				return defs.FORMAT_OPTIONS[opts_preset].format(opts[0], opts[1])
		elif opts_preset_type == dict:
			"""
			Custom formating is also enabled, setting divider/left & right side of expression
			"""
			print(opts_preset)
			return '{}{}{}{}{}'.format(opts_preset['left'], opts[0], opts_preset['divider'], opts[1], opts_preset['right'])


		# print(opts_blueprint)
		# print(opts)

	def _transform_opts_list(self, opts_blueprint, opts):
		pass

	def _match_flag(self, flag):
		"""
		Find correct flag options in blueprint
		"""
		try:
			return self.flags_match_table[flag][self.blueprint_index]
		except KeyError:
			raise KeyError('flag \'{}\' is not available in current blueprint. You can either try different blueprint or create new one'.format(flag))

	def _is_array(self, item):
		accepted_types = [list, tuple]
		for accepted_type in accepted_types:
			if isinstance(item, accepted_type):
				return True
		return False

	def _is_primitive(self, item):
		rejected_types = [list, tuple, set, dict]
		for rejected_type in rejected_types:
			if isinstance(item, rejected_type):
				return False
		return True