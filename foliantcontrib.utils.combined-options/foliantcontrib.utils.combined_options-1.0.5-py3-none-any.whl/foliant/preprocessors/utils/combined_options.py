import yaml
from pathlib import Path, PosixPath


class ValidationError(Exception):
    '''Error for validations when validation is failed'''
    pass


class Options:
    '''
    Helper class which imitates dictionary with options but has some
    handy methods like option validation and conversion.
    '''

    def __init__(self,
                 options: dict,
                 defaults: dict = {},
                 convertors: dict = {},
                 validators: dict = {}):
        '''
        options (dict)    — options dictionary,
        defaults (dict)   — dictionary with default values (needed only for
                            is_default to work),
        convertors (dict) — dictionary with key = option name, value = function
                            which will be applied to the value of this option
                            before storing in class.
        validators (dict) — dictionary with key = option name, value = function
                            which will be applied to the value of this option.
                            Function should check for validity and raise
                            ValidationError if the check fails.
        '''
        self.defaults = defaults
        self._options = options
        self._validators = validators
        self._convertors = convertors
        self.validate()
        self._convert()

    @property
    def options(self):
        '''Actual options dictionary'''
        return self._options

    def validate(self):
        '''
        Validate all options with supplied validators.
        Raises ValidationError if any of checks fails.
        '''
        if not self._validators:
            return

        for key in self._validators:
            if key in self.options:
                try:
                    self._validators[key](self.options[key])
                except ValidationError as e:
                    raise ValidationError(f'Error in option "{key}": {e}')

    def _convert(self):
        '''
        Convert all options with supplied convertors and replace values in
        options dictionary in place.
        '''
        if not self._convertors:
            return

        for key in self._convertors:
            if key in self.options:
                convertor = self._convertors[key]
                self.options[key] = convertor(self.options[key])

    def is_default(self, option):
        '''return True if option value is same as default'''
        if option in self.defaults:
            return self.options[option] == self.defaults[option]
        return False

    def __str__(self):
        return f'<{self.__class__.__name__}{self.options}>'

    def __getitem__(self, ind: str):
        return self.options[ind]

    def __contains__(self, ind: str):
        return ind in self.options

    def __iter__(self):
        return iter(self.options.keys())

    def get(self, key, default=None):
        return self.options.get(key, default)

    def keys(self):
        return self.options.keys()

    def items(self):
        return self.options.items()

    def values(self):
        return self.options.values()


class CombinedOptions(Options):
    '''
    Helper class which combines several Options objects into one. If options
    interlap the one to be returned is defined by 'priority'.
    Apart from that it is a normal Options object.
    '''

    def __init__(self,
                 options: dict,
                 priority: str = None,
                 defaults: dict = {},
                 convertors: dict = {},
                 validators: dict = {}):
        '''
        options (dict) — dictionary where key = priority,
                         value = option dictionary.
        priority (str) — initial priority (if not set = first key from
                         options dict).
        other parameters are same as in parent
        '''
        self._options_dict = options
        self._validators = validators
        self._convertors = convertors
        self.defaults = defaults
        self.priority = priority or next(iter(options.keys()))

    @property
    def priority(self):
        '''returns current priority'''
        return self._priority

    @priority.setter
    def priority(self, val: str):
        '''sets new priority and updates active options dictionary'''
        if val not in self._options_dict:
            raise ValueError('Priority must be one of: '
                             f'{", ".join(self._options_dict.keys())}. '
                             f'Value received: {val}')
        self._priority = val
        self.set_options()

    def set_options(self):
        '''
        Sets new active options dict with options combined from all options
        dicts with priority according to self.priority.
        '''

        self._options = {}
        priority_dict = self._options_dict[self.priority]

        for key in self._options_dict:
            if key != self.priority:
                self._options.update(self._options_dict[key])
        self._options.update(priority_dict)

        self.validate()
        self._convert()


def validate_in(supported, msg=None):
    '''
    Simple validator factory. Resulting function checks if option value
    is contained in supported collection.

    `supported` may be any collection-like object with __contains__ method.
    Raises ValueError otherwise.

    msg is message given to the ValiadtionError.

    Returns a validator function.'''

    DEFAULT_MSG = 'Unsupported option value {val}. Should be one '\
                  'of: {supported}'

    def validate(val):
        if val not in supported:
            raise ValidationError(message.format(val=val, supported=', '.join(supported)))

    if not hasattr(supported, '__contains__'):
        raise ValueError('`supported` should be a collection')

    message = msg if msg else DEFAULT_MSG

    return validate


def path_convertor(option: str or PosixPath):
    '''convert string to Path'''
    if type(option) is str:
        return Path(yaml.load(option, yaml.Loader))
    else:
        return option


def yaml_to_dict_convertor(option: str or dict):
    '''convert yaml string or dict to dict'''

    if type(option) is dict:
        return option
    elif type(option) is str:
        return yaml.load(option, yaml.Loader)


def boolean_convertor(option):
    '''
    convert option to bool if necessary.

    Accepts True\False, 'tRuE' \ 'falSE', 1\0, Y \ n, yes \ no
    "other str" = True
    '''
    str_dict = {
        '1': True,
        '0': False,
        'y': True,
        'n': False,
        'yes': True,
        'no': False,
        'true': True,
        'false': False
    }
    if type(option) == bool:
        return option
    elif type(option) == int:
        return bool(int)
    elif type(option) == str:
        return str_dict.get(option.lower().strip(), True)
