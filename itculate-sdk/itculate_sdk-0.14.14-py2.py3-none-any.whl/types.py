#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

#######################################################################################################################
# Base classes
#######################################################################################################################


class Importance(object):
    KPI_USER = 500  # For user KPI, use 0-999
    KPI_SYSTEM = 1500  # System KPIs will use the range 1000-1999
    IMPORTANT_USER = 2500  # For user 'important' metrics, use 2000-2999
    IMPORTANT_SYSTEM = 3500  # System 'important' metrics will use 3000-3999
    OTHER_USER = 4500  # For any other user metric, use 4000-4999
    OTHER_SYSTEM = 5500  # Other system metrics will use 5000-5999
    DEFAULT = 6000  # Default importance


class Bases(object):
    BASE_10 = 10.0
    BASE_1000 = 1000.0
    BASE_1024 = 1024.0


class Units(object):
    PERCENT = "%"

    BYTES = "Bytes"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"

    BYTES_PER_SEC = "Bytes/s"
    KB_PER_SEC = "KB/s"
    MB_PER_SEC = "MB/s"
    GB_PER_SEC = "GB/s"
    TB_PER_SEC = "TB/s"

    IO = "IO"
    IO_PER_SEC = "IO/s"
    QUERY_PER_SEC = "Query/s"

    US = "us"
    MS = "ms"
    SEC = "sec"

    HZ = "Hz"
    KHZ = "KHz"
    MHZ = "MHz"
    GHZ = "GHz"

    HOURLY = "Hourly"
    DAILY = "Daily"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"


class ResamplingMethods(object):
    LAST = "last"
    DIFF = "diff"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    AVG = "avg"
    PCT_95 = "pct_95"


class Methods(object):
    LAST = "last"
    DIFF = "diff"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    AVG = "avg"
    PCT_75 = "pct_75"
    PCT_95 = "pct_95"


class DataType(object):
    """
    Base class for defining a data type.

    A data type is an arbitrary structure with meta-data describing this value. This type will be registered in the
    dictionary for later display and aggregation purposes.
    """

    default_importance = Importance.DEFAULT
    default_visible = True

    default_label = None
    default_description = None
    default_resampling_method = Methods.LAST
    default_aggregation_method = Methods.MAX

    # should be used for contribution algorithm
    default_contribution = False

    # should be used for contribution algorithm
    default_correlation = False

    def __init__(self, **kwargs):
        """
        :param str label: Short label
        :param str description: Full description (documentation) for this type
        :param bool visible: If True, this type will be visible by default
        :param bool importance: indicator (can be used by the UI) 0 most important
        :param bool resampling_method: method of when resampling this counter over time period
        :param bool aggregation_method: method of when aggregation this counter cross objects it the same timestamp
        """
        self._label = kwargs.get("label", self.default_label)
        self._importance = kwargs.get("importance", self.default_importance)
        self._description = kwargs.get("description", self.default_description)
        self._visible = kwargs.get("visible", self.default_visible)
        self._resampling_method = kwargs.get("resampling_method", self.default_resampling_method)
        self._aggregation_method = kwargs.get("aggregation_method", self.default_aggregation_method)
        self._contribution = kwargs.get("contribution", self.default_contribution)
        self._correlation = kwargs.get("correlation", self.default_correlation)

    @classmethod
    def get_type(cls):
        assert cls.__name__.endswith("DataType"), "Wrong class name (must end with 'DataType'): {}".format(cls.__name__)
        return cls.__name__[:-8]

    @classmethod
    def get_full_class_name(cls):
        return "{}.{}".format(cls.__module__, cls.__name__)

    @property
    def type(self):
        return self.__class__.get_type()

    @property
    def full_class_name(self):
        return self.__class__.get_full_class_name()

    @property
    def label(self):
        """
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def importance(self):
        """
        :rtype: int
        """
        return self._importance

    @importance.setter
    def importance(self, value):
        self._importance = value

    @property
    def description(self):
        """
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def visible(self):
        """
        :rtype: bool
        """
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    @property
    def contribution(self):
        """
        :rtype: bool
        """
        return self._contribution

    @contribution.setter
    def contribution(self, value):
        self._contribution = value

    @property
    def correlation(self):
        """
        :rtype: bool
        """
        return self._correlation

    @correlation.setter
    def correlation(self, value):
        self._correlation = value

    @property
    def resampling_method(self):
        return self._resampling_method

    @property
    def aggregation_method(self):
        return self._aggregation_method

    @property
    def meta_data(self):
        """
        Given a meta data dict for this field, include additional information available about this type

        :rtype: dict
        """

        # Use the attribute names as keys in the meta-data dict as well as properties to look up 'self'
        props = ("type",
                 "label",
                 "description",
                 "importance",
                 "visible",
                 "resampling_method",
                 "aggregation_method",
                 "contribution",
                 "correlation")
        return {p: getattr(self, p) for p in props if getattr(self, p, None) is not None}

    def __repr__(self):
        return "{} (label={})".format(self.type, self.label)

    def __eq__(self, other):
        return type(self) == type(other)


class DataTypeWithUnit(DataType):
    """
    A data type with unit. This class adds the concepts of unit conversions, including support for different bases
    (e.g. 1000, 1024).

    All deriving class MUST define the following two class based attributes:

    1. Units_def: Defines which units are available for this type
    The first element in the tuple is a dict of unit to unit_exp. The second defines the most basic unit
    exponent for this type (e.g. 0: Bytes for capacity)

    2. Bases_def: A set of all possible bases for the unit calculation.
    """
    units_def = None
    bases_def = None
    default_unit = None
    default_base = None

    UNIT = "unit"
    BASE = "base"

    def __init__(self, **kwargs):
        super(DataTypeWithUnit, self).__init__(**kwargs)

        assert self.__class__.units_def, "Child Class must override units_def"
        assert self.__class__.bases_def, "Child Class must override bases_def"

        # Validate unit and base...
        # The class must have two attributes (two tuples): units_def and bases_def. Both define how to calculate and
        # convert values of this type
        units = self.__class__.units_def
        bases = self.__class__.bases_def

        unit = kwargs.get("unit") or self.default_unit or self.__class__.units_def[0]
        assert unit is not None and unit in units, \
            "{} - Invalid unit {}, can only be one of {}".format(self.type, unit, units)

        base = kwargs.get("base") or self.default_base or self.__class__.bases_def[0]
        assert base and base in bases, "{} - Invalid base {}, can only be one of {}".format(self.type, base, bases)

        # Save the unit and base as they were given - so we can do conversions later
        self._unit = unit
        self._base = base

    @property
    def units(self):
        """
        :rtype: tuple[str]
        """
        return self.__class__.units_def

    @property
    def bases(self):
        """
        :rtype: tuple[str]
        """
        return self.__class__.bases_def

    @property
    def unit(self):
        """
        :rtype: str
        """
        return self._unit

    @property
    def base(self):
        """
        :rtype: str
        """
        return self._base

    def __repr__(self):
        return "{}(label={}, unit={}, base={})".format(self.type, self.label, self.unit, self.base)

    def convert(self, value, from_unit=None, from_base=None, to_unit=None, to_base=None):
        """
        Return the value of this type converted to the required unit (and optional base)

        :param float value: Value to convert
        :param str|None from_unit: Unit to convert from (if none, self.unit will be used)
        :param float|None from_base: Base to convert from (optional - if missing, the self.base will be used)
        :param str to_unit: Unit to convert to (if none, self.unit will be used)
        :param float|None to_base: Base to convert to (optional - if missing, self.base will be used)

        :return: the converted value
        :rtype: float
        """

        assert from_unit or from_base or to_unit or to_base, "Some conversion action is expected..."

        # The class must have two attributes (two tuples): units_def and bases_def. Both define how to calculate and
        # convert values of this type

        units = self.__class__.units_def
        bases = self.__class__.bases_def

        from_unit = from_unit or self.unit
        assert from_unit in units, "Invalid from_unit {}, can only be one of {}".format(from_unit, units)

        to_unit = to_unit or self.unit
        assert to_unit in units, "Invalid to_unit {}, can only be one of {}".format(to_unit, units)

        from_base = from_base or self.base
        assert from_base in bases, "Invalid from_base {}, can only be one of {}".format(from_base, bases)

        to_base = to_base or self.base
        assert to_base in bases, "Invalid to_base {}, can only be one of {}".format(to_base, bases)

        ratio = from_base / to_base
        value *= ratio

        exp_diff = units.index(from_unit) - units.index(to_unit)
        value *= to_base ** exp_diff

        return value

    @property
    def meta_data(self):
        """
        :rtype: dict
        """
        meta = super(DataTypeWithUnit, self).meta_data

        meta.update({
            "units": list(self.units),  # Used by GUI - to allow a selection box
            "bases": list(self.bases),  # Used by GUI - to allow a selection box
            "unit": self.unit,
            "base": self.base,
        })

        return meta

    @classmethod
    def value(cls, value, unit=None, base=None, **kwargs):
        """
        A shortcut method to create a 'real-typed-value' for this specific data type.

        :param float value: Value to set
        :param str unit: Unit (if None, default_unit will be taken)
        :param float base: Base (if None, default_base will be taken)

        :rtype: RealTypedValueWithUnit
        """
        # Create the appropriate data type
        data_type = cls(**kwargs)
        return RealTypedValueWithUnit(data_type=data_type, value=value, unit=unit, base=base)


class TypedValue(object):
    """
    Value associated with a data type.
    """

    def __init__(self, value, data_type):
        """
        :type data_type: DataType
        """
        assert isinstance(data_type, DataType), "Expecting data_type to be a subclass of DataType"

        self._value = value
        self._data_type = data_type

    @property
    def value(self):
        return self._value

    @property
    def data_type(self):
        """
        :rtype: DataType
        """
        return self._data_type

    @property
    def meta_data(self):
        """
        :rtype: dict
        """
        return self._data_type.meta_data

    def __eq__(self, other):
        if not isinstance(other, TypedValue) or self.data_type != other.data_type:
            return False
        return self.value == other.value

    def __gt__(self, other):
        assert isinstance(other, TypedValue) and self.data_type == other.data_type, "Bad types {} <> {}".format(
            self.data_type,
            other.data_type)

        return self.value > other.value

    def __ge__(self, other):
        assert isinstance(other, TypedValue) and self.data_type == other.data_type, "Bad types {} <> {}".format(
            self.data_type,
            other.data_type)

        return self.value >= other.value

    def __lt__(self, other):
        assert isinstance(other, TypedValue) and self.data_type == other.data_type, "Bad types {} <> {}".format(
            self.data_type,
            other.data_type)

        return self.value < other.value

    def __le__(self, other):
        assert isinstance(other, TypedValue) and self.data_type == other.data_type, "Bad types {} <> {}".format(
            self.data_type,
            other.data_type)

        return self.value <= other.value

    def __str__(self):
        return "{}={}".format(self.data_type, self.value)

    def __unicode__(self):
        return u"{}={}".format(self.data_type, self.value)


class RealTypedValue(TypedValue):
    def __init__(self, value, data_type):
        """
        :type value: float
        :type data_type: DataType
        """
        try:
            super(RealTypedValue, self).__init__(float(value), data_type)
            assert isinstance(data_type, DataType), "{} is not a subclass of DataType".format(data_type)
        except TypeError:
            raise TypeError("{} bad value {} for float() argument, must be a string or a number.".format(data_type,
                                                                                                         value))

    def __add__(self, other):
        if isinstance(other, TypedValue):
            assert self.data_type == other.data_type
            value_to_add = other.value
        else:
            value_to_add = float(other)

        return RealTypedValue(self.value + value_to_add, self.data_type)

    def __sub__(self, other):
        if isinstance(other, TypedValue):
            assert self.data_type == other.data_type
            value_to_sub = other.value
        else:
            value_to_sub = float(other)

        return TypedValue(self.value - value_to_sub, self.data_type)

    def __mul__(self, other):
        if isinstance(other, TypedValue):
            assert self.data_type == other.data_type
            value_to_mul = other.value
        else:
            value_to_mul = float(other)

        return TypedValue(self.value * value_to_mul, self.data_type)

    def __div__(self, other):
        if isinstance(other, TypedValue):
            assert self.data_type == other.data_type
            value_to_div = other.value
        else:
            value_to_div = float(other)

        return TypedValue(self.value / value_to_div, self.data_type)


class RealTypedValueWithUnit(RealTypedValue):
    """
    A value with a data type and a unit.
    """

    def __div__(self, other):
        return RealTypedValueWithUnit(self.data_type, value=super(RealTypedValueWithUnit, self).__div__(other).value)

    def __mul__(self, other):
        return RealTypedValueWithUnit(self.data_type, value=super(RealTypedValueWithUnit, self).__mul__(other).value)

    def __sub__(self, other):
        return RealTypedValueWithUnit(self.data_type, value=super(RealTypedValueWithUnit, self).__sub__(other).value)

    def __add__(self, other):
        return RealTypedValueWithUnit(self.data_type, value=super(RealTypedValueWithUnit, self).__add__(other).value)

    def __init__(self, data_type, value, unit=None, base=None):
        """
        :type value: float|tuple[float]
        :param str unit: Unit for this value. If None, the DataType's normal unit is used
        :param float base: Bast for this value. If None, the DataType's normal base is used
        :type data_type: DataTypeWithUnit
        """
        super(RealTypedValueWithUnit, self).__init__(value, data_type)

        assert isinstance(data_type, DataTypeWithUnit), "Expecting data_type to be a subclass of DataTypeWithUnit"
        assert unit is None or unit in data_type.units, "unit {} must one of {}".format(unit, data_type.units)
        assert base is None or base in data_type.bases, "base {} must one of {}".format(base, data_type.bases)

        if unit and (unit != data_type.unit or base != data_type.base):
            self._value = data_type.convert(self._value, from_unit=unit, from_base=base)

    @property
    def data_type(self):
        """
        :rtype: DataTypeWithUnit
        """
        return super(RealTypedValueWithUnit, self).data_type

    # noinspection PyUnresolvedReferences
    def convert(self, to_unit, to_base=None):
        """
        Shortcut method to convert the value to another unit

        :rtype: float
        """
        return self.data_type.convert(value=self.value, to_unit=to_unit, to_base=to_base)


#######################################################################################################################
# Primitive / Basic data types
#
# These types define primitives (in terms of units) supported by the system
#######################################################################################################################

class CountDataType(DataTypeWithUnit):
    units_def = ("count",)
    bases_def = (Bases.BASE_10,)
    default_importance = Importance.OTHER_SYSTEM
    resampling_method = Methods.SUM
    aggregation_method = Methods.SUM


def count_value(value, **kwargs):
    return CountDataType.value(value, **kwargs)


class RequestCountDataType(CountDataType):
    default_importance = Importance.OTHER_SYSTEM


def request_count_value(value, **kwargs):
    return RequestCountDataType.value(value, **kwargs)


class ObjectCountDataType(CountDataType):
    resampling_method = Methods.MAX
    aggregation_method = Methods.SUM
    default_importance = Importance.OTHER_SYSTEM


def object_count_value(value, **kwargs):
    return ObjectCountDataType.value(value, **kwargs)


class ErrorCountDataType(CountDataType):
    default_importance = Importance.OTHER_SYSTEM


def error_count_value(value, **kwargs):
    return ErrorCountDataType.value(value, **kwargs)


class ExceptionCountDataType(CountDataType):
    default_importance = Importance.OTHER_SYSTEM


def exception_count_value(value, **kwargs):
    return ExceptionCountDataType.value(value, **kwargs)


class QueueSizeDataType(CountDataType):
    default_importance = Importance.OTHER_SYSTEM
    resampling_method = Methods.MAX
    aggregation_method = Methods.MAX


def queue_size_value(value, **kwargs):
    return ObjectCountDataType.value(value, **kwargs)


class RateDataType(DataTypeWithUnit):
    units_def = ("unit/s",)  # Typically these are over written by implementing classes (with more specific units)
    bases_def = (Bases.BASE_10,)
    default_importance = Importance.OTHER_SYSTEM
    resampling_method = Methods.AVG
    aggregation_method = Methods.SUM


def rate_value(value, **kwargs):
    return RateDataType.value(value, **kwargs)


class RequestRateDataType(RateDataType):
    units_def = ("requests/s",)
    bases_def = (Bases.BASE_10,)
    default_importance = Importance.OTHER_SYSTEM


def request_rate_value(value, **kwargs):
    return RequestRateDataType.value(value, **kwargs)


class ObjectRateDataType(RateDataType):
    units_def = ("objects/s",)
    bases_def = (Bases.BASE_10,)
    default_importance = Importance.OTHER_SYSTEM


def object_rate_value(value, **kwargs):
    return ObjectRateDataType.value(value, **kwargs)


class TimePeriodDataType(DataTypeWithUnit):
    units_def = (Units.US, Units.MS, Units.SEC,)
    bases_def = (Bases.BASE_1000,)
    default_unit = Units.MS
    default_importance = Importance.OTHER_SYSTEM
    default_correlation = True


def time_period_value(value, unit=None, **kwargs):
    return PricePerPeriodDataType.value(value, unit=unit, **kwargs)


class PercentDataType(DataTypeWithUnit):
    units_def = (Units.PERCENT,)
    bases_def = (Bases.BASE_10,)
    default_importance = Importance.OTHER_SYSTEM
    resampling_method = Methods.MAX
    aggregation_method = Methods.AVG


def percent_value(value, unit=None, **kwargs):
    return PercentDataType.value(value, unit=unit, **kwargs)


class UtilizationDataType(PercentDataType):
    default_importance = Importance.OTHER_SYSTEM


def utilization_value(value, unit=None, **kwargs):
    return UtilizationDataType.value(value, unit=unit, **kwargs)


class CapacityUtilizationDataType(PercentDataType):
    default_importance = Importance.OTHER_SYSTEM


def capacity_utilization_value(value, unit=None, **kwargs):
    return CapacityUtilizationDataType.value(value, unit=unit, **kwargs)


class ErrorPercentDataType(PercentDataType):
    default_importance = Importance.OTHER_SYSTEM


def error_percent_value(value, **kwargs):
    return ErrorPercentDataType.value(value, **kwargs)


class HealthyCountDataType(ObjectCountDataType):
    default_importance = Importance.OTHER_SYSTEM
    pass


def healthy_count_value(value, **kwargs):
    return HealthyCountDataType.value(value, **kwargs)


class UnhealthyCountDataType(ObjectCountDataType):
    default_importance = Importance.OTHER_SYSTEM
    pass


def unhealthy_count_value(value, **kwargs):
    return UnhealthyCountDataType.value(value, **kwargs)


class UnhealthyPercentDataType(PercentDataType):
    default_importance = Importance.OTHER_SYSTEM


def unhealthy_percent_value(value, **kwargs):
    return UnhealthyPercentDataType.value(value, **kwargs)


class LatencyDataType(TimePeriodDataType):
    default_importance = Importance.IMPORTANT_SYSTEM
    default_unit = Units.MS
    resampling_method = Methods.MAX
    aggregation_method = Methods.MAX


def latency_value(value, unit=None, **kwargs):
    return LatencyDataType.value(value, unit=unit, **kwargs)


class DurationDataType(TimePeriodDataType):
    default_importance = Importance.OTHER_SYSTEM
    default_unit = Units.MS
    resampling_method = Methods.MAX
    aggregation_method = Methods.MAX


def duration_value(value, unit=None, **kwargs):
    return DurationDataType.value(value, unit=unit, **kwargs)


class PricePerPeriodDataType(DataTypeWithUnit):
    units_def = (Units.HOURLY, Units.DAILY, Units.MONTHLY, Units.YEARLY)
    bases_def = (Bases.BASE_10,)  # there are in average 730 hours in 1 month
    default_unit = Units.MONTHLY
    default_importance = Importance.OTHER_SYSTEM
    resampling_method = Methods.AVG
    aggregation_method = Methods.SUM

    def convert(self, value, from_unit=None, from_base=None, to_unit=None, to_base=None):
        """
        Implement convert differently since time is not in decimal base
        """

        units = self.__class__.units_def

        from_unit = from_unit or self.unit
        assert from_unit in units, "Invalid from_unit {}, can only be one of {}".format(from_unit, units)

        to_unit = to_unit or self.default_unit
        assert to_unit in units, "Invalid from_unit {}, can only be one of {}".format(from_unit, units)

        if from_unit == to_unit:
            return value

        # Convert to hours
        if from_unit == Units.DAILY:
            # there 24 hours in 1 day
            hour_value = value / 24.0
        elif from_unit == Units.MONTHLY:
            # there 730 hours in 1 month in average
            hour_value = value / 730.0
        elif from_unit == Units.YEARLY:
            # there 8760 hours in a year
            hour_value = value / 8760.0
        else:
            assert from_unit == Units.HOURLY, "Unsupported unit '{}'".format(from_unit)
            hour_value = value

        if to_unit == Units.DAILY:
            # there 730 hours in 1 month in average
            new_value = hour_value * 24.0
        elif to_unit == Units.MONTHLY:
            new_value = hour_value * 730.0
        elif to_unit == Units.YEARLY:
            # there 730 hours in 1 month in average
            new_value = hour_value * 8760.0
        else:
            assert to_unit == Units.HOURLY, "Unsupported unit '{}'".format(from_unit)
            new_value = hour_value

        return new_value


def price_value(value, unit=None, **kwargs):
    return PricePerPeriodDataType.value(value, unit=unit, **kwargs)


class UnixDateDataType(DataTypeWithUnit):
    """
    Represents a data (Unix timestamp - secs since epoch)
    """
    units_def = (Units.SEC,)
    bases_def = (Bases.BASE_10,)  # there are in average 730 hours in 1 month
    default_unit = Units.SEC


def unix_date_value(value, **kwargs):
    return PricePerPeriodDataType.value(value, **kwargs)


class CapacityDataType(DataTypeWithUnit):
    units_def = (Units.BYTES, Units.KB, Units.MB, Units.GB, Units.TB,)
    bases_def = (Bases.BASE_1000, Bases.BASE_1024,)
    default_unit = Units.GB
    default_base = Bases.BASE_1024
    resampling_method = Methods.LAST
    aggregation_method = Methods.SUM


def capacity_value(value, unit=None, base=None, **kwargs):
    return CapacityDataType.value(value, unit=unit, base=base, **kwargs)


class ThroughputDataType(RateDataType):
    units_def = (Units.BYTES_PER_SEC, Units.KB_PER_SEC, Units.MB_PER_SEC, Units.GB_PER_SEC, Units.TB_PER_SEC,)
    bases_def = (Bases.BASE_1000, Bases.BASE_1024,)
    default_unit = Units.MB_PER_SEC
    default_base = Bases.BASE_1024
    default_importance = Importance.OTHER_SYSTEM
    default_contribution = True


def throughput_value(value, unit=None, **kwargs):
    return ThroughputDataType.value(value, unit=unit, **kwargs)


class NetworkThroughputDataType(ThroughputDataType):
    default_unit = Units.MB_PER_SEC


def network_throughput_value(value, unit=None, **kwargs):
    return NetworkThroughputDataType.value(value, unit=unit, **kwargs)


class FrequencyDataType(DataTypeWithUnit):
    units_def = (Units.HZ, Units.KHZ, Units.MHZ, Units.GHZ,)
    bases_def = (Bases.BASE_1000,)
    default_unit = Units.MHZ
    resampling_method = Methods.AVG
    aggregation_method = Methods.SUM


class IOpsDataType(RateDataType):
    units_def = (Units.IO_PER_SEC,)
    bases_def = (Bases.BASE_10,)
    default_importance = Importance.IMPORTANT_SYSTEM
    default_contribution = True


def iops_value(value, **kwargs):
    return IOpsDataType.value(value, **kwargs)


class MemoryDataType(CapacityDataType):
    default_importance = Importance.OTHER_SYSTEM
    default_unit = Units.GB
    resampling_method = Methods.LAST
    aggregation_method = Methods.SUM


def memory_value(value, unit=None, **kwargs):
    return MemoryDataType.value(value, unit=unit, **kwargs)


class CPUPercentDataType(PercentDataType):
    default_importance = Importance.IMPORTANT_SYSTEM


def cpu_percent_value(value, **kwargs):
    return CPUPercentDataType.value(value, **kwargs)


class NetworkPercentDataType(PercentDataType):
    default_importance = Importance.IMPORTANT_SYSTEM


def network_percent_value(value, **kwargs):
    return NetworkPercentDataType.value(value, **kwargs)


class MemoryPercentDataType(PercentDataType):
    default_importance = Importance.IMPORTANT_SYSTEM


def memory_percent_value(value, **kwargs):
    return MemoryPercentDataType.value(value, **kwargs)
