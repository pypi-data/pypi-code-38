# -*- coding: utf-8 -*-
"""
numerical utilities

@author: Jussi (jnu@iki.fi)
"""

import datetime


def check_hetu(hetu):
    """ This checks validity of a Finnish social security number (hetu) """
    if len(hetu) != 11 or hetu[6] not in '+-A':
        return False
    try:
        dd, mm = int(hetu[:2]), int(hetu[2:4])
    except ValueError:
        return False
    if not (0 <= dd <= 31 and 1 <= mm <= 12):
        return False
    # check 'checksum'
    chrs = "0123456789ABCDEFHJKLMNPRSTUVWXY"
    chk = chrs[(int(hetu[:6] + hetu[7:10])) % 31]
    if hetu[-1] != chk:
        return False
    return True


def age_from_hetu(hetu, d1=None):
    """ Return age at date d1 (datetime.date object) from hetu. If d1 is None,
    it is taken from current system time. """
    if not hetu:
        return None
    if not check_hetu(hetu):
        raise ValueError('Invalid hetu')
    if d1 is None:
        d1 = datetime.date.today()
    day, month, yr = int(hetu[:2]), int(hetu[2:4]), int(hetu[4:6])
    yr += {'+': 1800, '-': 1900, 'A': 2000}[hetu[6]]
    d0 = datetime.date(yr, month, day)
    return d1.year - d0.year - ((d1.month, d1.day) < (d0.month, d0.day))

