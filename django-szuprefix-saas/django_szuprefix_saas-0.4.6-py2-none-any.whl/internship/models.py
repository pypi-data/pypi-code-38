#!/usr/bin/env python   
# -*- coding:utf-8 -*-   
# Author: denishuang
from __future__ import unicode_literals

import logging
import datetime
from . import choices
from django.contrib.auth.models import User
from django.db import models

from django_szuprefix_saas.school.models import School, Teacher, Student, Session
from django_szuprefix.utils import modelutils
from django.contrib.contenttypes.fields import GenericRelation

log = logging.getLogger("django")


class InstructorCounsellorMixin(object):
    def __unicode__(self):
        return self.name

    def trainees_count(self):
        return self.trainees.count()

    trainees_count.short_description = "学生数"

    def trainee_class_names(self):
        return ",".join([c or '未知' for c in self.trainee_class_list()])

    trainee_class_names.short_description = "所有班级"

    def trainee_college_names(self):
        return ",".join([c or '未知' for c in self.trainee_colleges_list()])

    trainee_college_names.short_description = "所有院系"

    def traineeclass_list(self, college=None):
        trainees = self.trainees
        if college and not college.startswith("全部"):
            trainees = trainees.filter(college=college)
        return modelutils.group_by(trainees, "clazz")

    def trainee_majors_list(self, college=None):
        trainees = self.trainees
        if college and not college.startswith("全部"):
            trainees = trainees.filter(college=college)
        return modelutils.group_by(trainees, "major")

    def trainee_colleges_list(self, trainee_type=None):
        return modelutils.group_by(self.get_trainees(trainee_type), "college")

    def save(self, **kwargs):
        if not self.name:
            self.name = self.teacher.name
        if not self.school:
            self.school = self.teacher.school
        return super(InstructorCounsellorMixin, self).save(**kwargs)


class Counsellor(InstructorCounsellorMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "指导老师"
        permissions = ()
        ordering = ("school", "name")

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_counsellors",
                               on_delete=models.PROTECT)
    teacher = models.OneToOneField(Teacher, verbose_name=Teacher._meta.verbose_name, null=True,
                                   related_name="as_internship_counsellor")
    name = models.CharField("姓名", max_length=32, db_index=True, null=True, blank=True)
    department = models.CharField("部门", max_length=64, null=True, blank=True)
    is_active = models.BooleanField("在职", blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)


class Instructor(InstructorCounsellorMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "辅导员"
        permissions = ()
        ordering = ("school", "name")

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_instructors",
                               on_delete=models.PROTECT)
    teacher = models.OneToOneField(Teacher, verbose_name=Teacher._meta.verbose_name, null=True,
                                   related_name="as_internship_instructor")
    name = models.CharField("姓名", max_length=32, db_index=True, null=True, blank=True)
    department = models.CharField("部门", max_length=64, null=True, blank=True)
    is_active = models.BooleanField("在职", blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)


class Trainee(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "实习生"
        # ordering = (,)

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_trainees",
                               on_delete=models.PROTECT)
    student = models.OneToOneField(Student, verbose_name=Student._meta.verbose_name, null=True,
                                related_name="as_internship_trainee",
                                on_delete=models.PROTECT)
    instructor = models.ForeignKey(Instructor, verbose_name=Instructor._meta.verbose_name, related_name="trainees",
                                   null=True,
                                   blank=True, on_delete=models.PROTECT)
    counsellor = models.ForeignKey(Counsellor, verbose_name=Counsellor._meta.verbose_name, related_name="trainees",
                                   null=True,
                                   blank=True, on_delete=models.PROTECT)
    name = models.CharField("姓名", max_length=64, null=True, blank=True)
    status = models.PositiveSmallIntegerField("实习状态",  default=choices.STATUS_WEISHIXI,
                                              choices=choices.CHOICES_STATUS, db_index=True)
    status_update_time = models.DateTimeField("实习状态修改时间", null=True, blank=True, default=None)
    last_institution = models.ForeignKey("Institution", verbose_name="最近工作单位", null=True, blank=True, related_name='trainees')
    current_institution = models.ForeignKey("Institution", verbose_name="当前工作单位", null=True, blank=True, related_name='current_trainees')
    last_signin_time = models.DateTimeField(verbose_name="最近签到时间", null=True, blank=True)
    last_feedback_time = models.DateTimeField(verbose_name="最近反馈时间", null=True, blank=True)
    last_recommend_time = models.DateTimeField("最近推荐校企职位时间", null=True, blank=True)
    last_browse_theme_time = models.DateTimeField("最近浏览帖子时间", blank=True, null=True, default=None)
    last_score_time = models.DateTimeField("最近评分时间", blank=True, null=True, default=None)
    score = models.PositiveSmallIntegerField("评分", blank=True, default=0)
    comment = models.TextField("备注", null=True, blank=True)
    ethnic_code = models.PositiveSmallIntegerField("民族代码", null=True, blank=True)
    admission_ticket = models.CharField("准考证", max_length=128, null=True, blank=True)
    leave_party_status = models.CharField("离校情况", max_length=128, null=True, blank=True)
    payment_status = models.CharField("缴费情况", max_length=128, null=True, blank=True)
    insurance_status = models.CharField("保险情况", max_length=128, null=True, blank=True)
    internship_report = models.CharField("实习报告", max_length=128, null=True, blank=True)
    internship_begin = models.DateField("实习期开始", blank=True, null=True)
    internship_end = models.DateField("实习期结束", blank=True, null=True)
    is_working = models.BooleanField("工作中", default=False)
    is_active = models.BooleanField("有效", default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)

    def not_working_days(self):
        if not self.is_working and self.status_update_time:
            return datetime.date.today() - self.status_update_time
        return 0

    def __unicode__(self):
        return self.name

    def as_user(self):
        return self.student.as_user()

    def save(self, **kwargs):
        if not self.name:
            self.name = self.student.name
        self.school = self.student.school
        self.is_working = self.status in choices.WORKING_STATUS_LIST
        return super(Student, self).save(**kwargs)


class Institution(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "单位"
        ordering = ('-starting_date', '-id')

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="internship_institutions",
                              on_delete=models.PROTECT)
    trainee = models.ForeignKey(Trainee, verbose_name=Trainee._meta.verbose_name, related_name="institutions",
                                on_delete=models.PROTECT)
    internship_type = models.PositiveSmallIntegerField("实习种类", default=1, null=True,
                                                       choices=choices.CHOICES_TYPE, blank=True)
    name = models.CharField("单位名称", max_length=128, null=True)
    oibc = models.CharField("组织机构代码", max_length=128, null=True, blank=True)
    city = models.CharField("单位地址", max_length=255, null=True)
    place = models.CharField("单位详细地址", max_length=255, null=True, blank=True)
    starting_date = models.DateField("上岗时间", null=True)
    finish_date = models.DateField("结束时间", null=True, blank=True)
    position = models.CharField("工作岗位", max_length=128, null=True, blank=True)
    salary = models.PositiveIntegerField("月薪", null=True)
    property = models.PositiveSmallIntegerField("单位性质", null=True, blank=True, choices=(
        (None, "请选择"), (1, "民营企业"), (2, "国营企业"), (3, "合资"), (4, "其他"),))
    contacts = models.CharField("单位联系人", max_length=128, null=True)
    contact_number = models.CharField("单位联系电话", max_length=128, null=True)
    contact_email = models.CharField("单位联系邮箱", max_length=128, null=True, blank=True)
    party_recommend = models.PositiveSmallIntegerField("学校推荐种类", choices=choices.CHOICES_SCHOOL_RECOMMEND, null=True,
                                                       blank=True)
    is_party_recommend = models.NullBooleanField("是否学校推荐", choices=((None, "请选择"), (True, "是"), (False, "否")),
                                                 default=None)
    comment = models.TextField("备注", null=True, blank=True)
    match_status = models.PositiveSmallIntegerField("专业对口", default=0, null=True, blank=True,
                                                    choices=choices.CHOICES_MATCH,
                                                    db_index=True)
    status = models.PositiveSmallIntegerField("实习状态", null=True, blank=False,
                                              choices=choices.CHOICES_STATUS,
                                              db_index=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    # 额外字段
    graduate_goes = models.PositiveSmallIntegerField("毕业去向", null=True, blank=True,
                                                     choices=choices.CHOICES_GRADUATE_GOES,
                                                     db_index=True)
    institution_type = models.CharField("单位类型", max_length=8, null=True, blank=True,
                                        choices=choices.INSTITUTION_TYPE_CHOICES,
                                        db_index=True)
    institution_industry = models.CharField("单位所属行业", max_length=8, null=True, blank=True,
                                            choices=choices.INSTITUTION_INDUSTRY_CHOICES,
                                            db_index=True)
    behavior_intention = models.PositiveSmallIntegerField("使用意图", null=True, blank=True,
                                                          choices=choices.CHOICES_BEHAVIOR_INTENTION,
                                                          db_index=True)
    job_type = models.CharField("职业类型", max_length=8, null=True, blank=True, choices=choices.JOB_TYPE_CHOICES,
                                db_index=True)
    # contract_time = （上岗时间？）
    is_employed_hard = models.BooleanField("是否就业困难", blank=True, default=False,
                                           choices=( (True, "是"), (False, "否")))
    dispatch_nature = models.PositiveSmallIntegerField("派遣性质", null=True, blank=True,
                                                       choices=choices.CHOICES_DISPATCH_NATURE,
                                                       db_index=True)
    difficult_student_type = models.CharField("困难生类别", max_length=255, null=True, blank=True)

    #  difficult_student_type = models.PositiveSmallIntegerField("困难生类别",  null=True, blank=True, choices=GOVERNING_BODY_CHOICES,
    #                                           db_index=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.school = self.student.school
        it = self.internship_type
        if it in [choices.TYPE_WANGDIAN, choices.TYPE_JIAJIAO, choices.TYPE_SHENGXUE, choices.TYPE_CANJUN]:
            self.is_party_recommend = False
        if not self.position:
            self.position = choices.DEFAULTS_POSITION.get(it, self.get_internship_type_display())
        if not self.graduate_goes:
            self.graduate_goes = choices.DEFAULTS_GRADUATE_GOES.get(it, choices.QITAQINGKUANG)
        if not self.institution_type:
            self.institution_type = choices.DEFAULTS_INSTITUTION_TYPE.get(it, "")
        if not self.institution_industry:
            self.institution_industry = choices.DEFAULTS_INSTITUTION_INDUSTRY.get(it, "")
        if not self.behavior_intention:
            self.behavior_intention = choices.DEFAULTS_BEHAVIOR_INTENTION.get(it, choices.QITA)
        return super(Institution, self).save(**kwargs)




class Feedback(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "反馈"
        ordering = ('-create_time',)

    school = models.ForeignKey(School,verbose_name=School._meta.verbose_name,related_name="internship_feedbacks",on_delete=models.PROTECT)
    student = models.ForeignKey(Student, verbose_name=Student._meta.verbose_name, related_name="feedbacks",on_delete=models.PROTECT)
    institution = models.ForeignKey(Institution, verbose_name="单位", null=True, blank=True,on_delete=models.PROTECT)
    content = models.TextField("反馈", null=True)
    status = models.PositiveSmallIntegerField("实习状态", null=True, blank=True, choices=choices.CHOICES_STATUS, db_index=True)
    verify_status = models.PositiveSmallIntegerField("审核状态", default=0, null=True, blank=True, choices=choices.VERIFY_CHOICES,
                                                     db_index=True)
    teacher_remark = models.TextField("辅导员反馈", null=True, blank=True)
    teacher_score = models.PositiveIntegerField("辅导员打分", null=True, blank=True)
    create_time = models.DateTimeField("创建时间", db_index=True)
    images = GenericRelation("common.Image")

    def __unicode__(self):
        return "%s %s feedback @%s" % (self.create_time.isoformat(),self.student,self.place)

    def save(self, **kwargs):
        self.school = self.student.school
        if not self.institution:
            self.institution = self.student.current_institution
        if not self.status:
            self.status = self.student.status
        return super(Feedback, self).save(**kwargs)

