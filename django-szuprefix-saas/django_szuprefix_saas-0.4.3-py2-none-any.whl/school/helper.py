# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime
import unidecode
from django.db.models import NOT_PROVIDED, ForeignKey
from django_szuprefix.utils import dateutils
from . import choices, models
import re


def gen_default_grades(school):
    gs = choices.MAP_SCHOOL_TYPE_GRADES.get(school.type)
    if not gs:
        return
    for number, name in gs:
        school.grades.create(name=name, number=number)


def gen_default_session(school, offset=0):
    today = dateutils.format_the_date()
    year = today.month >= 8 and today.year or today.year - 1
    year -= offset
    return school.sessions.get_or_create(
        number=year,
        defaults=dict(
            name="%s届" % year,
            begin_date="%s-09-01" % year,
            end_date="%s-07-01" % (year + 1))
    )


RE_CLAZZ_GRADE_NAME = re.compile(r"^(\d{4}|\d{2})[级届]*")


def normalize_clazz_name(clazz_name, grade=None):
    """
    In [18]: a=helper.normalize_clazz_name(u"2000级计算机A班"); print a[0],a[1],a[2]
    2000级计算机A班 计算机A班 2000级

    In [19]: a=helper.normalize_clazz_name(u"92级计算机A班"); print a[0],a[1],a[2]
    1992级计算机A班 计算机A班 1992级

    In [20]: a=helper.normalize_clazz_name(u"28级计算机A班"); print a[0],a[1],a[2]
    2028级计算机A班 计算机A班 2028级

    In [21]: a=helper.normalize_clazz_name(u"28级计算机A班",u"92级"); print a[0],a[1],a[2]
    92级计算机A班 计算机A班 92级
    """

    m = RE_CLAZZ_GRADE_NAME.search(clazz_name)
    if m:
        g = m.group(0)
        clazz_name = clazz_name[m.pos + len(g):]
        if not clazz_name:
            clazz_name = g[2:]
            g = g[:2]
        g = "%s级" % grade_name_to_number(g)
        if not grade:
            grade = g
        grade = normalize_grade_name(grade, g)
    else:
        grade = normalize_grade_name(grade)
    if not clazz_name.endswith("班"):
        clazz_name = "%s班" % clazz_name
    return "%s%s" % (grade, clazz_name), clazz_name, grade


def clazz_name_to_number(clazz_name):
    RE_CLAZZ_NUMBER = re.compile(r"([0-9一二三四五六七八九]+)班")
    m = RE_CLAZZ_NUMBER.search(clazz_name)
    if m:
        from django_szuprefix.utils.datautils import cn2digits
        return cn2digits(m.groups()[0])


def normalize_grade_name(grade, default=None):
    """
    In [56]: print helper.normalize_grade_name(u"98届")
    1998级

    In [57]: print helper.normalize_grade_name(u"00届")
    2000级

    In [58]: print helper.normalize_grade_name(u"2010届")
    2010级

    In [60]: print helper.normalize_grade_name(u"2099届",u"2019级")
    2019级

    """

    if not grade:
        return default
    no = short_year_to_full_year(grade_name_to_number(grade))
    from datetime import datetime
    if no > datetime.now().year:
        grade = default
    else:
        grade = "%d级" % no
    if grade[-1] != "级":
        grade += "级"
    return grade


RE_MAJOR = re.compile(r"([^\(\)]*)(\(([^\(\)]*)\)|)")


def normalize_major_name(major):
    major = major.replace(" ", "").replace("（", "(").replace("）", ")")
    m = RE_MAJOR.search(major)
    if m:
        return m.group(1), m.group(3)
    return major, None


RE_GRADE = re.compile(r"(\d+)[级届]*")
RE_GRADE2 = re.compile(r"(\d+)[年级]*")


def short_year_to_full_year(no):
    """
    In [33]: helper.short_year_to_full_year(49)
    Out[33]: 2049

    In [34]: helper.short_year_to_full_year(50)
    Out[34]: 1950

    In [35]: helper.short_year_to_full_year(99)
    Out[35]: 1999

    In [36]: helper.short_year_to_full_year(100)
    Out[36]: 100

    In [37]: helper.short_year_to_full_year(1)
    Out[37]: 2001

    In [38]: helper.short_year_to_full_year(2010)
    Out[38]: 2010
    """
    assert no >= 0, "不能小于0"
    return no < 50 and no + 2000 or no < 100 and no + 1900 or no


def grade_name_to_number(grade_name):
    """
    In [43]: helper.grade_name_to_number(u"98届")
    Out[43]: 1998

    In [44]: helper.grade_name_to_number(u"98级")
    Out[44]: 1998

    In [45]: helper.grade_name_to_number(u"12级")
    Out[45]: 2012

    In [46]: helper.grade_name_to_number(u"23级")
    Out[46]: 2023

    In [47]: helper.grade_name_to_number(u"1923级")
    Out[47]: 1923
    """
    m = RE_GRADE.search(grade_name)
    if m:
        sno = m.group(1)
        return short_year_to_full_year(int(sno))


def cur_grade_number(grade_name, today=None):
    """
     when today is 2016.9.10

     cur_grade_number("14级")
     3
     cur_grade_number("2015级")
     2
     cur_grade_number("2016级")
     1
     cur_grade_number("98级")
     19
     cur_grade_number("17级")
     0
     cur_grade_number("18级")
     -1
    """
    gno = grade_name_to_number(grade_name)
    if not gno:
        return
    today = today or datetime.date.today()
    num = today.year - gno
    if today.month >= 8:
        num += 1
    return num


def cur_grade_year(grade_num, today=None):
    today = today or datetime.date.today()
    year = today.year - grade_num
    if today.month >= 8:
        year += 1
    return year


def cur_grade_name(grade_num, today=None):
    return "%s级" % cur_grade_year(grade_num, today)


def get_cur_term(corp):
    from django_szuprefix.utils.dateutils import format_the_date
    today = format_the_date()
    year = today.month >= 8 and today.year or today.year - 1
    month = today.month
    day = today.day
    part = (month * 100 + day < 215 or month >= 8) and 1 or 2
    name = "%s-%s学年第%s学期" % (year, year + 1, part == 1 and "一" or "二")
    start_date = datetime.date(today.year, part == 1 and 9 or 3, 1)
    term, created = corp.school_terms.get_or_create(year=year,
                                                    part=part,
                                                    defaults=dict(name=name,
                                                                  start_date=start_date))
    return term


def init_student(worker):
    profile = worker.profile
    party = worker.party
    school = party.as_school

    def get_field_value_from_profile(profile, fs):
        r = {}
        for f in fs:
            if isinstance(f, (ForeignKey)):
                fo, created = f.related_model.objects.get_or_create(school=school, name=profile.get(f.verbose_name))
                r[f.name] = fo
            else:
                r[f.name] = profile.get(f.verbose_name, f.default != NOT_PROVIDED and f.default or None)
        return r

    fns = "number,name".split(",")
    fs = [f for f in models.Student._meta.local_fields if f.name in fns]
    ps = get_field_value_from_profile(profile, fs)

    grade_name = profile.get('年级')
    grade_number = cur_grade_number(grade_name)
    grade, created = school.grades.get_or_create(number=grade_number)
    ps['grade'] = grade

    session_number = grade_name_to_number(grade_name)
    session, created = school.sessions.get_or_create(number=session_number)
    ps['entrance_session'] = session

    clazz_name = profile.get('班级')
    clazz, created = school.clazzs.get_or_create(
        name=clazz_name,
        defaults=dict(
            entrance_session=session,
            grade=grade
        )
    )
    ps['clazz'] = clazz
    ps['user'] = worker.user

    student, created = school.students.update_or_create(
        number=worker.number,
        defaults=ps)
    major_name = profile.get("专业")
    if major_name:
        student.majors = school.majors.filter(name__in=major_name.split(","))
    return student, created


#
# def binding_check(name, number, mobile, the_id=None):
#     qset = models.Student.objects.filter(number=number, name=name)
#     ss= []
#     for s in qset:
#         user = s.user
#         if hasattr(user,'as_person') and getattr(user, 'as_person').mobile == mobile:
#             if not the_id or s.id == the_id:
#                 ss.append(s)
#     if not ss:
#         raise Exception("相关账号不存在, 可能查询信息不正确, 或者还未录入系统")
#     elif len(ss) == 1:
#         user = ss[0].user
#         if user.has_usable_password():
#             raise Exception("该帐号已绑定过,不能重复绑定")
#     return ss


# def binding(name, number, mobile, oldUser):
#     students = binding_check(name, number, mobile)
#     if len(students)>1:
#         raise Exception("检验不通过,无法绑定")

def bind(student, old_user):
    user = student.user
    from django_szuprefix.auth.signals import to_bind_user
    from django.db import transaction
    with transaction.atomic():
        to_bind_user.send(student._meta.model, old_user=old_user, new_user=user)
        # user.set_password(student.number)
        # user.save()
        student.is_bind = True
        student.save()
    from django_szuprefix.common.signals import to_add_event
    to_add_event.send_robust(sender=student._meta.model, instance=student, name='bind')

def unbind(student):
    user = student.user
    from django.db import transaction
    with transaction.atomic():
        if hasattr(user, 'as_wechat_user'):
            user.as_wechat_user.delete()
        user.set_unusable_password()
        user.save()
        student.is_bind = False
        student.save()
