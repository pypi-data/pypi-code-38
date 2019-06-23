# -*- coding: utf-8 -*-
# Created by crazyX on 2018/7/7
from ojcrawler.crawlers.poj import POJ
from ojcrawler.crawlers.hdu import HDU
from ojcrawler.crawlers.codeforces import Codeforces

supports = {
    'poj': POJ,
    'hdu': HDU,
    'codeforces': Codeforces,
}
