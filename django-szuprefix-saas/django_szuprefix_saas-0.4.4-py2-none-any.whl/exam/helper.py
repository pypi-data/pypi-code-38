# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals
import re
from django_szuprefix.utils.datautils import strQ2B
__author__ = 'denishuang'

def distrib_count(d, a):
    a = str(a)
    counts = d.setdefault('counts', {})
    percents = d.setdefault('percents', {})
    counts[a] = counts.setdefault(a, 0) + 1
    tc = sum(counts.values())
    cas = [(int(k), v) for k, v in counts.iteritems()]
    cas.sort()
    s = 0
    for k, v in cas:
        s += v
        percents[str(k)] = s / float(tc)
    d['count'] = tc
    return d

def answer_equal(standard_answer, user_answer):
    if len(standard_answer) != len(user_answer):
        return False
    l = zip(standard_answer, user_answer)
    return all([b in a.split('|') for a, b in l])

RE_MULTI_ANSWER_SPLITER = re.compile(r"[|()、]")

def split_answers(s):
    if isinstance(s, (list, tuple)):
        return s
    return RE_MULTI_ANSWER_SPLITER.split(strQ2B(s))

"""
In [36]: answer_match(['A|C','B','C','D'],['C','B'],True)
Out[36]: 0.5

In [37]: answer_match(['A','B','C','D'],['C','B'])
Out[37]: 0.5

In [38]: answer_match(['A','B','C','D'],['B'])
Out[38]: 0.25

In [39]: answer_match(['A','B','C','D'],['B'],True)
Out[39]: 0.0

In [40]: answer_match(['A','B','C','D'],['B','E'])
Out[40]: 0.0

In [41]: answer_match(['A','B','C','D'],['B','A','D','C'])
Out[41]: 1.0
"""
def answer_match(standard_answer, user_answer, one_by_one=False):
    sa = standard_answer
    ua = user_answer
    lsa = len(sa)
    lua = len(ua)
    if lua > lsa:
        return -1
    l = zip(sa[:lua], ua)
    c = 0
    for s, u in l:
        if one_by_one:
            if u in split_answers(s):
                c += 1
        else:
            if u in sa:
                c += 1
            else:
                c = 0
                break
    return c / lsa
