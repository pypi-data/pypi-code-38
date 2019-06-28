from .basic import Integer, String, Float, Bool
from ..rule import *

class UnsignedInteger(Integer, Unsigned):
    """
    无符号整数
    """
    pass


class UnsignedFloat(Float, Unsigned):
    """
    无符号浮点数
    """
    pass


class SizedString(String, MaxSized):
    """
    指定长度的字符串
    """
    pass


class Email(String, EmailRule):
    """
    邮箱
    """
    pass


class Bool(Bool):
    """
    布尔
    """
    pass


class CH(String, CHRule):
    """
    纯文字
    """
    pass


class Number(NumberRule):
    """
    正负数，小数
    """
    pass


class Positive(PositiveRule):
    """
    正数
    """
    pass


class PositiveInteger(PositiveIntegerRule):
    """
    正数
    """
    pass


class Month(MonthRule):
    """
    月份
    """
    pass


class Day(DayRule):
    """
    天数
    """
    pass


class Time(TimeRule):
    """
    时间
    """
    pass


class Username(String, UsernameRule):
    """
    长度至少为1，包含大小写字母、数字、_、-
    """
    pass


class Password(String, PasswordRule):
    """
    大小写字母或数字，长度至少6位
    """
    pass


class PasswordEasy(String, PasswordEasyRule):
    """
    6到16位的任意（除开斜线）
    """
    pass


class PasswordHardL1(String, PasswordHardL1Rule):
    """
    数字 + 字母（大写或小写） + 长度6到12位
    """
    pass


class PasswordHardL2(String, PasswordHardL2Rule):
    """
    数字 + 字母（大写和小写） + 长度6到12位
    """
    pass


class Date(DateRule):
    """
    """
    pass


class Birthday(String, BirthdayRule):
    pass


class BirthdayHard(String, BirthdayHardRule):
    pass


class Credit(String, CreditRule):
    pass


class Carcode(String, CarcodeRule):
    pass


class QQ(String, QQRule):
    pass


class Fax(String, FaxRule):
    pass


class PhoneCommon(String, PhoneCommonRule):
    pass


class Phone(String, PhoneRule):
    pass


class Mobile(String, MobileRule):
    pass


class Url(String, UrlRule):
    pass


class URL(String, URLRule):
    pass


class Ipv4Agent(String, Ipv4AgentRule):
    pass


class Ipv4(String, Ipv4Rule):
    pass


class Ipv6(String, Ipv6Rule):
    pass


class JsonHeader(JsonHeaderRule):
    pass


class RequestHeader(RequestHeaderRule):
    pass


class All(AllRule):
    pass
