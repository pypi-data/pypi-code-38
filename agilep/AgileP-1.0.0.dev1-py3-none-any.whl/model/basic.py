from ..rule import Typed


class Integer(Typed):
    """
    整型
    """
    expected_type = int


class Float(Typed):
    """
    浮点数
    """
    expected_type = float


class String(Typed):
    """
    字符串
    """
    expected_type = str


class Bool(Typed):
    """
    bool
    """
    expected_type = bool