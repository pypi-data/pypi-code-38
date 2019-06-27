# -*- coding: utf-8 -*-
'''
Module: num2word_FA.py
Requires: num2word_EU.py
Version: 1.2

Author:
   Taro Ogawa (tso@users.sourceforge.org)
   
Copyright:
    Copyright (c) 2003, Taro Ogawa.  All Rights Reserved.

Licence:
    This module is distributed under the Lesser General Public Licence.
    http://www.opensource.org/licenses/lgpl-license.php

Data from:
    http://www.uni-bonn.de/~manfear/large.php
    
Usage:
    from num2word_FA import n2w, to_card, to_ord, to_ordnum
    to_card(1234567890)
    n2w.is_title = True
    to_card(1234567890)
    to_ord(1234567890)
    to_ordnum(1234567890)
    to_year(1976)
    to_currency(dollars*100 + cents, longval=False)
    to_currency((dollars, cents))
    

History:
    1.2: to_ordinal_num() made shorter and simpler (but slower)
         strings in merge() now interpolated
         to_year() and to_currency() added
         
    1.1: to_ordinal_num() fixed for 11,12,13   
'''

from . import num2word_EU


class Num2Word_FA(num2word_EU.Num2Word_EU):
    def set_high_numwords(self, high):
        max = 3 + 3 * len(high)
        for word, n in zip(high, list(range(max, 3, -3))):
            self.cards[10 ** n] = word + "میلیون"

    def set_high_numwords_str(self, high):
        max = 3 + 3 * len(high)
        for word, n in zip(high, list(range(max, 3, -3))):
            self.cards_str[10 ** n] = word + "میلیون"

    def setup(self):
        self.negword = "منفی "
        self.pointword = "نقطه"
        self.errmsg_nonnum = "تنها اعداد می توانند به حروف تبدیل شوند."
        self.exclude_title = ["و", "نقطه", "منفی"]

        self.mid_numwords_str = [(1000, "هزار"), (900, "نهصد"), (800, "هشتصد"), (700, "هفتصد"), (600, "ششصد"),
                                 (500, "پانصد"), (400, "چهارصد"), (300, "سیصد"), (200, "دویست"), (100, "یکصد"),
                                 (90, "نود"), (80, "هشتاد"), (70, "هفتاد"),
                                 (60, "شصت"), (50, "پنجاه"), (40, "چهل"),
                                 (30, "سی"), (20, "بیست"), (10, "ده")]
        self.mid_numwords = [(1000, "هزار"), (900, "نهصد"), (800, "هشتصد"), (700, "هفتصد"), (600, "ششصد"),
                             (500, "پانصد"), (400, "چهارصد"), (300, "سیصد"), (200, "دویست"), (100, "صد"), (90, "نود"),
                             (80, "هشتاد"), (70, "هفتاد"), (60, "شصت"), (50, "پنجاه"), (40, "40"), (30, "30"),
                             (20, "بیست"), (10, "ده")]
        self.low_numwords_str = ["بیست", "نوزده", "هجده", "هفده",
                             "شانزده", "پانزده", "چهارده", "سیزده",
                             "دوازده", "یازده", "ده", "نه", "هشت",
                             "هفت", "شش", "پنج", "چهار", "سه", "دو",
                             "یک", "صفر"]
        self.low_numwords = ["20", "19", "18", "17",
                             "16", "15", "14", "13",
                             "12", "11", "10", "9", "8",
                             "7", "6", "5", "4", "3", "2",
                             "1", "0"]

        self.ords = {"یک": "اول",
                     "دو": "دوم",
                     "سه": "سوم",
                     "چهار": "چهارم",
                     "پنج": "پنجم",
                     "شش": "ششم",
                     "هفت": "هفتم",
                     "هشت": "هشتم",
                     "نه": "نهم",
                     "ده": "دهم",
                     "دوازده": "دوازدهم"}

    def merge(self, curr, next):
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1 and nnum < 100:
            return next
        elif 100 > cnum > nnum:
            return ("%s و %s" % (ctext, ntext), cnum + nnum)
        elif cnum >= 100 > nnum:
            return ("%s و %s" % (ctext, ntext), cnum + nnum)
        elif nnum > cnum:
            return ("%s %s" % (ctext, ntext), cnum * nnum)
        return ("%s و %s" % (ctext, ntext), cnum + nnum)

    def merge_str(self, curr, next):
        ctext, cnum, ntext, nnum = curr + next

        if cnum == 1 and nnum < 100:
            return next
        elif 100 > cnum > nnum:
            return ("%s و %s" % (ctext, ntext), cnum + nnum)
        elif cnum >= 100 > nnum:
            return ("%s و  %s" % (ctext, ntext), cnum + nnum)
        elif nnum > cnum:
            return ("%s %s" % (ctext, ntext), cnum * nnum)
        return ("%s و %s" % (ctext, ntext), cnum + nnum)

    def to_ordinal(self, value):
        self.verify_ordinal(value)
        outwords = self.to_cardinal(value).split(" ")
        lastwords = outwords[-1].split(" ")
        lastword = lastwords[-1].lower()
        try:
            lastword = self.ords[lastword]
        except KeyError:
            if lastword[-1] == "l":
                lastword = lastword[:-1] + "ie"
            lastword += "م"
        lastwords[-1] = self.title(lastword)
        outwords[-1] = " و ".join(lastwords)
        return " ".join(outwords)

    def to_ordinal_num(self, value):
        self.verify_ordinal(value)
        return "%s%s" % (value, self.to_ordinal(value)[-2:])

    def to_year(self, val, longval=True):
        if not (val // 100) % 10:
            return self.to_cardinal(val)
        return self.to_splitnum(val, hightxt="صد", jointxt="و",
                                longval=longval)

    def to_currency(self, val, longval=True):
        return self.to_splitnum(val, hightxt="تومان", lowtxt="قران",
                                jointxt="و", longval=longval)


n2w = Num2Word_FA()
to_card = n2w.to_cardinal
to_card_str = n2w.to_cardinal_str
to_ord = n2w.to_ordinal
to_ordnum = n2w.to_ordinal_num
to_year = n2w.to_year


def main():
    for val in [1, 11, 12, 21, 31, 33, 71, 80, 81, 91, 99, 100, 101, 102, 155,
                180, 300, 308, 832, 1000, 1001, 1061, 1100, 1500, 1701, 3000,
                8280, 8291, 150000, 500000, 1000000, 2000000, 2000001,
                -21212121211221211111, -2.121212, -1.0000100]:
        n2w.test(val)
    n2w.test(
        1325325436067876801768700107601001012212132143210473207540327057320957032975032975093275093275093270957329057320975093272950730)
    for val in [1, 120, 1000, 1120, 1800, 1976, 2000, 2010, 2099, 2171]:
        print((val, "هست", n2w.to_currency(val)))
        print((val, "هست", n2w.to_year(val)))


if __name__ == "__main__":
    main()
