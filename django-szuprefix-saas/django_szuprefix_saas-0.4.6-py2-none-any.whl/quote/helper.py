# -*- coding:utf-8 -*- 
__author__ = 'denishuang'


def split_delivery_days(ds):
    def get_days(s, default_unit='D'):
        u = s[-1]
        if u in ['D', 'W', 'M']:
            a = int(s[:-1])
        else:
            u = default_unit
            a = int(s)
        t = u == 'W' and 7 or u == 'M' and 30 or 1
        return a, u, a * t

    ps = ds.split("-")
    if len(ps) == 1:
        ps = ps * 2
    a2, u2, d2 = get_days(ps[1])
    a1, u1, d1 = get_days(ps[0], default_unit=u2)
    return d1, d2
