from decimal import Decimal
import math

S_IDX = 0
P_IDX = 1
A_IDX = 2


def f2d(val):
    return Decimal(str(val))


class CoinNum(Decimal):
    uni_dec = 18

    def __init__(self, dec=18, prec=18):
        self.dec = dec
        self.prec = prec

    def set(self, dec=None, prec=None):
        if dec is not None:
            self.dec = dec
        if prec is not None:
            self.prec = prec
        return self

    def amount(self):
        return round(self)

    def precise(self):
        """
        精确小数
        :return: 字符串
        """
        return format(self / 10 ** self.dec, '.{}f'.format(self.dec))

    def simple(self, mode=None):
        """
        方便阅读的，待有效数字的小数
        :return: 字符串
        """
        if mode == 'up':
            delta = self.dec - self.prec
            up = f2d(math.ceil(self / 10 ** delta) * 10 ** delta)
            return format(up / 10 ** self.dec, '.{}f'.format(self.prec))
        elif mode == 'low':
            delta = self.dec - self.prec
            low = f2d(math.floor(self / 10 ** delta) * 10 ** delta)
            return format(low / 10 ** self.dec, '.{}f'.format(self.prec))
        else:
            return format(self / 10 ** self.dec, '.{}f'.format(self.prec))

    def uninum(self):
        """
        内部统一精度整数
        :return: int
        """
        return round(self * 10 ** (self.uni_dec - self.dec))

    def group(self, mode=None):
        return self.simple(mode), self.precise(), self.amount()

    @staticmethod
    def f2c(f_val, dec, prec):
        """
        将易读数字（浮点值或字符串）转为CoinNum对象
        :param f_val:
        :param dec: 小数点位数
        :param prec: 有效位数
        :return: CoinNum
        """
        return CoinNum(round(Decimal(str(f_val)) * 10 ** dec)).set(dec, prec)

    @staticmethod
    def u2c(uninum, dec, prec):
        """
        将统一精度数字转为CoinNum对象
        :param uninum:
        :param dec: 小数点位数
        :param prec: 有效位数
        :return: CoinNum
        """
        return CoinNum(round(uninum / 10 ** (CoinNum.uni_dec - dec))).set(dec, prec)

    @staticmethod
    def points(f_val):
        """
        获取小数后位数
        :param f_val: 浮点值或字符串
        :return: 小数位数
        """
        return abs(Decimal(str(f_val)).as_tuple().exponent)
