from CrystalMatch.dls_util.config.config import Config


class ConfigItem:
    """ Represents a single option/configuration item which is essentially a name/value pair.
    This class should be sub-classed in order to handle different types of value. Objects of this
    class and sub-classes are intended for use with a Config object.
    """
    DATA_TYPE = str

    def __init__(self, tag, default):
        """ Initialize a new config item.

        Parameters
        ----------
        tag - The 'name' of this option, used as an identifier when saved to file and in the UI.
        default - the default value of this option.
        """
        self._value = None
        self._override = None
        self._tag = tag
        self._default = default
        self._comment = None
        self._acceptable_values = ""

    def value(self):
        """ Get the value of this option. """
        if self._override is not None:
            return self._override
        return self._value

    def tag(self):
        """ Get the tag (string name) of this option. """
        return self._tag

    def comment(self):
        """ Get the comment string for this item. """
        return self._comment

    def acceptable_values(self):
        """ Get a string representation of the allowable values. """
        return self._acceptable_values

    def set(self, value):
        """ Set the value of this option. """
        self._value = self._clean(value)

    def set_override(self, value):
        """ Set an override which is returned in place of the value from the configuration. """
        self._override = self._clean(value)

    def set_comment(self, comment):
        """ Set the comment string for this item. """
        self._comment = comment

    def reset(self):
        """ Set the value of this option to its default. """
        self._value = self._default

    def to_file_string(self):
        """ Creates a string representation that can be saved to and read from file. """
        comment = ""
        ok_values = "# Possible Values: {}\n".format(self._acceptable_values)
        default = "# Default: {}\n".format(self._default)
        name_value = "{}{}{}".format(self._tag, Config.DELIMITER, self._value)

        if self._comment is not None:
            comment_lines = Config.create_comment_lines(self._comment)
            comment = "".join(comment_lines)

        file_string = comment + ok_values + default + name_value

        return file_string

    def to_json(self):
        lower_underscore = self._tag.lower().replace(" ", "_").replace("(", "").replace(")", "")
        new_tag ='c_'+ lower_underscore
        return {new_tag: self.graylog_format(self._value)}

    def from_file_string(self, value_string):
        """ Read the value from its string representation. """
        pass

    def _clean(self, value):
        """ Perform any additional cleanup/processing on the value. Implement in subclass if needed. """
        return value

    def graylog_format(self, value):
        """Graylog expect string or int as an input. This function can be used to convert a value to one of the two."""
        return value


class StringItem(ConfigItem):
    """ Config item that stores a string value."""
    DATA_TYPE = str

    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)
        self._acceptable_values = "String"

    def from_file_string(self, value_string):
        self._value = value_string


class IntConfigItem(ConfigItem):
    """ Config item that stores an integer. Constructor may also take a 'units' parameter which is a
    string that represents the units of the value. This can be used in the UI.
    """
    DATA_TYPE = int

    def __init__(self, tag, default, units=""):
        ConfigItem.__init__(self, tag, default)
        self._units = units
        self._acceptable_values = "Integer"

    def units(self):
        """ The unit type of the value. """
        return self._units

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value):
        try:
            return int(value)
        except ValueError:
            return self._default


class FloatConfigItem(ConfigItem):
    """ Config item that stores a float.
    """
    DATA_TYPE = float

    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)
        self._acceptable_values = "Float"

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value):
        try:
            return float(value)
        except ValueError:
            return self._default


class RangeIntConfigItem(IntConfigItem):
    """ Config item that stores an integer with a restricted range of allowable values.
    """
    DATA_TYPE = int
    TYPE_NAME = "Integer"

    def __init__(self, tag, default, limits=[0, 100]):
        """ The range given by the limits is inclusive. For a half-open range, use None for the
        first or second value. """
        IntConfigItem.__init__(self, tag, default)
        if len(limits) != 2:
            raise ValueError("range must be a list of 2 elements")

        self._min = limits[0]
        self._max = limits[1]
        self._acceptable_values = ""

        if not self.in_range(default):
            raise ValueError("default must be between {} and {} inclusive".format(self._min, self._max))

        self._set_acceptable_values()

    def _set_acceptable_values(self):
        if self._min is None:
            self._acceptable_values = "{} <= {}".format(self.TYPE_NAME, self._max)
        elif self._max is None:
            self._acceptable_values = "{} >= {}".format(self.TYPE_NAME, self._min)
        else:
            self._acceptable_values = "{} in range [{}, {}]".format(self.TYPE_NAME, self._min, self._max)

    def min(self): return self._min

    def max(self): return self._max

    def is_closed_range(self):
        return self._max is not None and self._min is not None

    def _clean(self, value):
        try:
            val = self.DATA_TYPE(value)
        except ValueError:
            return self._default

        if self.in_range(val):
            return val
        elif self._min is not None and val < self._min:
            return self._min
        elif self._max is not None and val > self._max:
            return self._max
        else:
            return self._default

    def in_range(self, value):
        ok = True
        if self._min is not None:
            ok &= self._min <= value

        if self._max is not None:
            ok &= value <= self._max

        return ok


class RangeFloatConfigItem(RangeIntConfigItem):
    """ Config item that stores a float with a restricted range of allowable values.
    """
    DATA_TYPE = float
    TYPE_NAME = "Float"

    def __init__(self, tag, default, limits=[0.0, 1.0]):
        """ Limits must contain two ordered numbers that represent the inclusive range. Either limit
        can be set to None, if you only want to bound the float on one side. """
        RangeIntConfigItem.__init__(self, tag, default, limits)


class DirectoryConfigItem(ConfigItem):
    """ Config item that stores a directory path (can be relative or absolute). """
    DATA_TYPE = str

    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)
        self._acceptable_values = "Absolute or relative file path"

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value):
        return str(value).strip()


class BoolConfigItem(ConfigItem):
    """ Config item that stores a boolean value. """
    DATA_TYPE = bool

    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)
        self._acceptable_values = "'True' or 'False'"

    def from_file_string(self, string):
        if string.lower() in ["true", "t", "yes", "y", "ok"]:
            self._value = True
        elif string.lower() in ["false", "f", "no", "n"]:
            self._value = False
        else:
            self._value = self._default

    def graylog_format(self, value):
        return str(value).strip()

class EnumConfigItem(ConfigItem):
    """ Config item that stores an enum value. """
    DATA_TYPE = str

    def __init__(self, tag, default, enum_values):
        """ The enum_values should be a list of strings. """
        ConfigItem.__init__(self, tag, default)
        self.enum_values = enum_values
        self._acceptable_values = ", ".join(["'{}'".format(s) for s in self.enum_values])

        if default not in enum_values:
            self._default = self.enum_values[0]

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value_str):
        value_str = str(value_str).strip()
        for val in self.enum_values:
            if value_str == str(val):
                return val

        return self._default
