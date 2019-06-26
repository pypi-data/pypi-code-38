"""
Marshmallow Validate Extend
"""

from marshmallow.validate import Validator, ValidationError


class IP(Validator):
    """IP Validator"""

    def __init__(self, error=None):
        """
        :param error:  验证错误消息
        """
        self.error = error if error else 'Invalid IP'

    def __call__(self, value):
        """验证value值"""
        ip_values = value.split('.')
        if len(ip_values) != 4:
            raise ValidationError(self.error)

        for v in ip_values:
            try:
                v = int(v)
            except ValueError:
                raise ValidationError(self.error)
            else:
                if v > 255 or v < 0:
                    raise ValidationError(self.error)


class Coordination(Validator):
    """坐标验证器"""
    def __init__(self, error=None):
        self.error = error if error else 'Invalid coordination value'

    def __call__(self, value):
        """验证坐标值

        :param value `lan, lon` => `纬度、经度`
        """
        try:
            coordination_values = [float(x.strip()) for x in value.split(',')]
        except ValueError:
            raise ValidationError(self.error)
        else:
            if not (len(coordination_values) == 2 and
                    -90 <= coordination_values[0] <= 90 and -180 <= coordination_values[1] <= 180):
                raise ValidationError(self.error)
