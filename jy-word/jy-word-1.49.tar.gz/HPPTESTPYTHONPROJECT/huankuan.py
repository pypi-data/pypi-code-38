# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/6/12 0012
__author__ = 'huohuo'
mounts = 130000-12000
year = 12
month = year * 12
day = year * 365
pay = 2500


# first month
print u'总金额%s' % mounts
zaijies = [0, 9833.33+1416-2500]
for m in range(1, month):
    # m = 1
    y = m / 12 + 1
    m1 = m % 12
    mounts += zaijies[m]
    benjin = mounts / 12.0
    lixi = mounts * 0.04 * 0.01 * m * 30
    zaijies.append(max(benjin + lixi - pay, 0))

    mounts = mounts - lixi + pay
    print u'第%s年，第%s个月，本金%.2f，利息%.2f, 再借%.2f, 总债务%.2f' % (y, m1, benjin, lixi, zaijies[m], mounts)
    if mounts <= 0:
        break


# for i in range(month):
#     lixi = mounts * 0.04 * 0.01 * i * 30
#     # 30 day
#     print lixi
#     mounts = mounts + lixi - pay
#     if mounts <= 0:
#         break
#     print i, lixi, mounts


if __name__ == "__main__":
    pass
    

