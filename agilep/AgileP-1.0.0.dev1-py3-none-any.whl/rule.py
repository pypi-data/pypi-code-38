from .model.validate import *


# Base class. Uses a descriptor to set a value
class Descriptor:
    def __init__(self, name=None, **opts):
        self.name = name
        for key, value in opts.items():
            setattr(self, key, value)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class Typed(Descriptor):
    """
    类型校验
    """
    expected_type = type(None)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{value} The correct format is a {str(self.expected_type)}")
        super().__set__(instance, value)


class Unsigned(Descriptor):
    """
    值必须大于 0
    """

    def __set__(self, instance, value):
        _max_value = getattr(self, "max", None)
        _min_value = getattr(self, "min", None)

        if _max_value and value > _max_value:
            raise ValueError(f"Value must be less than {value}")

        if _min_value and value < _min_value:
            raise ValueError(f"Value must be greater than {value}")

        if value < 0:
            raise ValueError('Value must be greater than 0')
        super().__set__(instance, value)


class MaxSized(Descriptor):
    def __init__(self, name=None, **opts):
        if 'size' not in opts:
            raise TypeError('missing size option')
        super().__init__(name, **opts)

    def __set__(self, instance, value):
        if len(value) >= self.size:
            raise ValueError('size must be < ' + str(self.size))
        super().__set__(instance, value)


class EmailRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="email")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class CHRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="CH")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class NumberRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="number")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PositiveRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="positive")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PositiveIntegerRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="positive_integer")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class MonthRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="month")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class DayRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="day")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class TimeRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="time")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class UsernameRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="username")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PasswordRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="password")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PasswordEasyRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="password_easy")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PasswordHardL1Rule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="password_hard")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PasswordHardL2Rule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="password_hard1")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class DateRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="date")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class BirthdayRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="birthday")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class BirthdayHardRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="birthday_hard")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class CreditRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="credit")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class CarcodeRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="carcode")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class QQRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="qq")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class FaxRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="fax")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PhoneCommonRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="phone_common")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class PhoneRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="phone")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class MobileRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="mobile")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class UrlRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="url")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class URLRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="URL")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class Ipv4AgentRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="ipv4Agent")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class Ipv4Rule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="ipv4")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class Ipv6Rule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="ipv6")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class JsonHeaderRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="json_header")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class RequestHeaderRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="request_header")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)


class AllRule(Descriptor):
    def __set__(self, instance, value):
        _result = Validate.check(value, reg_type="all")
        if not _result:
            raise ValueError(f'{value} Incorrect format')
        super().__set__(instance, value)
