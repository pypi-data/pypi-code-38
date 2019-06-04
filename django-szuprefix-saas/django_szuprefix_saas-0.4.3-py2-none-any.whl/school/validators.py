# -*- coding:utf-8 -*- 
__author__ = 'denishuang'

from ..saas.validators import *


class StudentNumberValidator(RegexValidator):
    message = u"学号格式不对"
    regex = u"^\w{6,32}$"


valid_student_number = StudentNumberValidator()


class GradeValidator(RegexValidator):
    message = u"年级格式不对"
    regex = u"^(\d{2}|\d{4})级$"


valid_grade = GradeValidator()


class StudentNumberField(BaseField):
    name = u"学号"
    default_synonyms = [u"学生编号"]
    default_validators = [valid_student_number]
    default_formaters = [format_not_float, format_banjiao]
    no_duplicate = True


field_student_number = StudentNumberField()

class WorkerNumberValidator(RegexValidator):
    message = u"工号格式不对"
    regex = u"^\w{4,12}$"


valid_worker_number = WorkerNumberValidator()


class WorkerNumberField(BaseField):
    name = u"工号"
    default_validators = [valid_worker_number]
    default_formaters = [format_not_float, format_banjiao]
    ignore_invalid = True
    no_duplicate = True


field_worker_number = WorkerNumberField()


class CollegeField(BaseField):
    name = u"院系"
    default_synonyms = [u"学院", u"教研室", u"系别", u"系部"]


field_college = CollegeField()


class MajorField(BaseField):
    name = u"专业"
    default_synonyms = [u"专业方向"]
    default_formaters = [format_banjiao]


field_major = MajorField()

def format_grade(v):
    if not v:
        return None
    if isinstance(v, int) or not v.endswith(u"级"):
        return u"%s级" % v
    return v

class GradeField(BaseField):
    name = u"年级"
    default_validators = [valid_grade]
    default_formaters = [format_not_float, format_half_year, format_banjiao, format_str_without_space, format_grade]

field_grade = GradeField()


class ClassField(BaseField):
    name = u"班级"
    default_synonyms = [u"班"]
    default_formaters = [format_not_float, unicode, format_banjiao, format_str_without_space]

field_class = ClassField()

class SessionField(BaseField):
    name = u"届别"
    default_synonyms = [u"届"]
    default_formaters = [format_not_float, unicode, format_banjiao, format_str_without_space]

field_session = SessionField()


class InstructorField(BaseField):
    name = u"辅导员"
    default_synonyms = [u"辅导老师"]

field_instructor = InstructorField()


class IsInstructorField(BaseField):
    name = u"辅导员"
    default_synonyms = [u"辅导老师"]

field_is_instructor = IsInstructorField()


class CounsellorField(BaseField):
    name = u"实习指导老师"
    default_synonyms = [u"指导老师"]

field_counsellor = CounsellorField()


class IsCounsellorField(BaseField):
    name = u"实习指导老师"
    default_synonyms = [u"指导老师"]

field_is_counsellor = IsCounsellorField()

class DepartmentField(BaseField):
    name = u"部门"
    default_synonyms = [u"所在部门"]

field_department = DepartmentField()
