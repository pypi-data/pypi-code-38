# -*- coding:utf-8 -*-
SCHOOL_TYPE_KINDERGARTEN = 0
SCHOOL_TYPE_PRIMARY = 1
SCHOOL_TYPE_MIDDLE = 2
SCHOOL_TYPE_UNIVERSITY = 3
SCHOOL_TYPE_VOCATIONAL = 4
CHOICES_SCHOOL_TYPE = (
    (SCHOOL_TYPE_KINDERGARTEN, u'幼儿园'),
    (SCHOOL_TYPE_PRIMARY, u'小学'),
    (SCHOOL_TYPE_MIDDLE, u'中学'),
    (SCHOOL_TYPE_UNIVERSITY, u'大学'),
    (SCHOOL_TYPE_VOCATIONAL, u'职校')
)

CHOICES_GRADE_KINDERGARTEN = (
    (1, u"小班"),
    (2, u"中班"),
    (3, u"大班"),
)

CHOICES_GRADE_PRIMARY = (
    (1, u"一年级"),
    (2, u"二年级"),
    (3, u"三年级"),
    (4, u"四年级"),
    (5, u"五年级"),
    (6, u"六年级"),
)

CHOICES_GRADE_PRIMARY9 = CHOICES_GRADE_PRIMARY + (
    (7, u"七年级"),
    (8, u"八年级"),
    (9, u"九年级"),
)

CHOICES_GRADE_MIDDLE = (
    (1, u"初一"),
    (2, u"初二"),
    (3, u"初三"),
    (11, u"高一"),
    (12, u"高二"),
    (13, u"高三"),
)

CHOICES_GRADE_UNIVERSITY = CHOICES_GRADE_VOCATIONAL = (
    (1, u"大一"),
    (2, u"大二"),
    (3, u"大三"),
    (4, u"大四"),
    (11, u"硕一"),
    (12, u"硕二"),
    (13, u"硕三"),
)


MAP_SCHOOL_TYPE_GRADES = {
    SCHOOL_TYPE_KINDERGARTEN: CHOICES_GRADE_KINDERGARTEN,
    SCHOOL_TYPE_PRIMARY: CHOICES_GRADE_PRIMARY,
    SCHOOL_TYPE_MIDDLE: CHOICES_GRADE_MIDDLE,
    SCHOOL_TYPE_UNIVERSITY: CHOICES_GRADE_UNIVERSITY,
    SCHOOL_TYPE_VOCATIONAL: CHOICES_GRADE_VOCATIONAL,
}
