#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os, random
from django.dispatch import receiver
from django.db.models.signals import post_save
from .signals import ucs_passed


# Create your models here.



# 课程
class Course(models.Model):
    name = models.CharField(max_length=180, verbose_name='课程名字')  # 名字
    subtitle = models.CharField(max_length=180, null=True, verbose_name='课程副标题', blank=True)  # 副标题
    level = models.IntegerField(default=0, verbose_name='课程的level', blank=True)  # 课程的level
    is_del = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name='授课老师')
    image = models.ImageField(null=True, blank=True, verbose_name='配图', upload_to='course/face')
    status = models.IntegerField(verbose_name='状态', default=0)  # 0 不显示，1 显示在列表

    class Meta:
        db_table = 'bee_django_course_course'
        app_label = 'bee_django_course'
        ordering = ["-id"]
        verbose_name = 'course课程'
        permissions = (
            ('can_manage_course', '可以进入课程管理页'),
            ('view_all_courses', '可以查看所有课程'),
            ('can_choose_course', 'can choose course'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_course:course_detail', kwargs={'pk': self.pk})

    def is_my_course(self, user):
        user_course = UserCourse.objects.filter(user=user, course=self)
        if user_course.exists():
            return user_course.first()
        else:
            return None


class Section(models.Model):
    name = models.CharField(max_length=180, verbose_name='课件名字')  # 名字
    info = models.TextField(null=True, blank=True, verbose_name='正文')
    videos = models.ManyToManyField("bee_django_course.Video")
    has_textwork = models.BooleanField(verbose_name='是否需要文字作业', default=False)
    textwork_info = models.TextField(verbose_name='作业说明', null=True, blank=True)
    has_videowork = models.BooleanField(verbose_name='是否需要视频录制', default=True)
    has_imagework = models.BooleanField(verbose_name='是否需要上传图片', default=False)
    has_questionwork = models.BooleanField(verbose_name='是否需要回答问题', default=False)
    question_passed_at = models.DateTimeField(verbose_name='问答通过时间', null=True, blank=True)
    video_length_req = models.IntegerField(verbose_name='要求录制时长(分钟)', default=0)
    image_count_req = models.IntegerField(verbose_name='要求提交图片数量', default=0)

    created_at = models.DateTimeField(default=timezone.now)
    auto_pass = models.BooleanField(default=False, verbose_name='是否自动通过')  # 课件是否自动通过
    type = models.IntegerField(default=0)  # 0 普通课件，1 预备课件

    image = models.ImageField(null=True, blank=True, verbose_name='配图', upload_to='section/face')

    class Meta:
        db_table = 'bee_django_course_section'
        app_label = 'bee_django_course'
        ordering = ["-id"]
        verbose_name = 'course课件'
        permissions = (
            ('view_all_sections', '可以查看所有课件'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_course:section_detail', kwargs={'pk': self.pk})

    def get_auto_pass_text(self):
        if self.auto_pass:
            return '是'
        else:
            return '否'

    def get_questions(self):
        return self.sectionquestion_set.all()

    # 添加问题
    def add_question(self, question_type):
        question = SectionQuestion()
        question.section = self
        question.question_type = question_type
        question.question = '新建问题'
        question.save()
        return question


# 课件的用户笔记
class UserSectionNote(models.Model):
    section = models.ForeignKey(Section)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    note = models.TextField(verbose_name='学习笔记')
    is_open = models.BooleanField(default=True, verbose_name='公开笔记')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_stick = models.BooleanField(default=False, verbose_name='是否置顶')
    is_digest = models.BooleanField(default=False, verbose_name='是否精华')


# 课件的附件
class SectionAttach(models.Model):
    name = models.CharField(max_length=180, verbose_name='附件名称', null=True, blank=True)
    section = models.ForeignKey(Section)
    file = models.FileField(verbose_name='附件', upload_to='sections/%Y/%m/%d/')
    upload_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_section_attach'

    def file_name(self):
        if self.name:
            return self.name
        else:
            return os.path.basename(self.file.name)


# 课程课件中间件
class CourseSectionMid(models.Model):
    course = models.ForeignKey("bee_django_course.Course", verbose_name='课程')  # 课程
    section = models.ForeignKey("bee_django_course.Section", verbose_name="课件")  # 课程包
    points = models.IntegerField(default=0, verbose_name='通过后获得的M币')
    order_by = models.IntegerField(default=0, verbose_name="顺序")  # 顺序
    mins = models.IntegerField(null=True, blank=True, verbose_name='达标分钟数')  # 达标分钟数
    pre_name = models.CharField(max_length=180, verbose_name='前缀标题', null=True, blank=True)

    class Meta:
        db_table = 'bee_django_course_section_mid'
        app_label = 'bee_django_course'
        ordering = ['order_by']

    def __unicode__(self):
        return ("CourseSectionMid->course:" + self.course.name)


class Video(models.Model):
    video_id = models.CharField(max_length=180, null=True)  # 视频 id，16位 hex 字符串
    status = models.CharField(max_length=180, null=True)  # 视频状态。”OK”表示视频处理成功，”FAIL”表示视频处理失败。
    duration = models.CharField(max_length=180, null=True)  # 片长（单位:秒）
    image = models.CharField(max_length=180, null=True)  # 视频截图地址
    # ===========
    title = models.CharField(max_length=180, null=True, verbose_name='标题')  # 视频标题
    file_name = models.CharField(max_length=180, null=True, blank=True, verbose_name='视频文件名')
    info = models.TextField(verbose_name='说明', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey("users.User", related_name='cc_video_user', null=True)  # 由谁上传
    # video_status = models.IntegerField(default=1, null=True)  # 状态 1-正常，2-正常（删除视频）

    class Meta:
        db_table = 'bee_django_course_video'
        app_label = 'bee_django_course'
        ordering = ['-created_at']
        verbose_name = 'course视频'
        permissions = (
            ('view_all_videos', '可以查看所有视频'),
        )

    def __unicode__(self):
        return ("视频:" + self.title)

    def get_absolute_url(self):
        # return reverse('bee_django_course:video_detail', kwargs={'pk': self.pk})
        return reverse('bee_django_course:video_list')


class SectionVideo(models.Model):
    section = models.ForeignKey(Section, verbose_name='关联的课件')
    video = models.ForeignKey(Video, verbose_name='关联的视频')
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0, verbose_name='在课件里的排序')

    class Meta:
        db_table = 'bee_django_course_section_video'
        ordering = ['order']


COURSE_SECTION_QUESTION_TYPE_CHOICES = ((1, "单选"), (2, "多选"))


class SectionQuestion(models.Model):
    section = models.ForeignKey(Section, verbose_name='关联的课件')
    question = models.CharField(max_length=180, verbose_name='问题')
    question_type = models.IntegerField(default=1, verbose_name='问题类型', choices=COURSE_SECTION_QUESTION_TYPE_CHOICES)
    order_by = models.IntegerField(default=0, verbose_name='顺序')
    options = models.ManyToManyField("bee_django_course.SectionQuestionOption")
    tip_wrong = models.TextField(null=True, verbose_name="错误时提示词")
    tip_correct = models.TextField(null=True, verbose_name="正确时提示词")

    class Meta:
        db_table = 'bee_django_course_section_question'
        ordering = ['order_by']
        permissions = (
            ('view_sectionquestion', '可以查看问题列表'),
        )

    # 添加选项
    def add_options(self, count=1):
        # 单选 或多选
        if int(self.question_type) == 1 or int(self.question_type) == 2:
            new_options = []
            for i in range(1, count + 1):
                option = SectionQuestionOption()
                option.question = self
                option.option = '选项' + i.__str__()
                option.order_by = i
                option.save()
                self.options.add(option)
                new_options.append(option)
            return new_options

    # 获取答题的正确答案
    def get_correct_options(self):
        return SectionQuestionOption.objects.filter(question=self, is_correct=True)

    # 获取【无】正确答案的问题
    @classmethod
    def get_has_correct_questions(cls, has_correct=False):
        if has_correct:
            return cls.objects.filter(options__is_correct=True)
        else:
            return cls.objects.exclude(options__is_correct=True)


class SectionQuestionOption(models.Model):
    question = models.ForeignKey(SectionQuestion, verbose_name='问题')
    option = models.CharField(max_length=180, verbose_name='选项')
    order_by = models.IntegerField(default=0, verbose_name='顺序')
    is_correct = models.BooleanField(default=False, verbose_name='是否正确答案')

    class Meta:
        app_label = "bee_django_course"
        db_table = 'bee_django_course_section_question_option'
        ordering = ['order_by']


# 每添加一个问题，自动创建选项
@receiver(post_save, sender=SectionQuestion)
def create_user(sender, **kwargs):
    section_question = kwargs['instance']
    if kwargs['created']:
        section_question.add_options(3)


class UserQuestionAnswerRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)  # 学生
    question = models.ForeignKey(SectionQuestion)  # 问题
    answer = models.ForeignKey(SectionQuestionOption)  # 答案
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_user_question_answer_record'
        app_label = 'bee_django_course'
        ordering = ['-created_at']

    def __unicode__(self):
        return ("UserQuestionAnswerRecord->user:" + self.user.username + ",question:" + self.question.question)

    @classmethod
    def get_user_question_answer_options(cls, question, user):
        return cls.objects.filter(question=question, user=user)
        # answer_option_list = []
        # for record in records:
        #     option_id_list.append(record.answer)
        # return SectionQuestionOption.objects.filter(id__in=option_id_list)


class UserLive(models.Model):
    provider_name = models.CharField(max_length=180)  # 平台商
    cc_user_id = models.CharField(max_length=180, null=True)  # CC账号
    room_id = models.CharField(max_length=180, null=True)  # 直播间ID
    live_id = models.CharField(max_length=180, null=True)  # 直播ID
    stop_status = models.CharField(max_length=180, null=True)  # 直播结束状态，10：正常结束，20：非正常结束
    record_status = models.CharField(max_length=180, null=True)  # 直播录制状态，10：录制成功，20：录制失败，30：直播过长
    record_video_id = models.CharField(max_length=180, null=True)  # 录制视频ID（如果录制成功，则返回该参数）
    replay_url = models.CharField(max_length=180, null=True)  # 直播回放地址（如果录制成功，则返回该参数）
    start_time = models.DateTimeField(null=True)  # 直播开始时间
    end_time = models.DateTimeField(null=True)  # 直播结束时间
    user = models.ForeignKey(settings.AUTH_USER_MODEL)  # 学生
    duration = models.IntegerField(null=True)  # 秒
    record_video_duration = models.IntegerField(null=True)  # 秒 返回的视频时间
    status = models.IntegerField(default=1, null=True)  # 状态 1-正常，2-正常（删除视频），-1：删除 -2 删除（删除视频）
    created_at = models.DateTimeField(auto_now_add=True)
    call_count = models.IntegerField(default=1)  # 回调了几次
    coin_multiple = models.IntegerField(default=0)  # 加了几倍M币

    class Meta:
        db_table = 'bee_django_course_user_live'
        app_label = 'bee_django_course'
        ordering = ['-created_at']
        verbose_name = 'course学生录播'
        permissions = (
            ('view_all_userlives', '可以查看所有学生的录播'),
            ('view_teach_userlives', '可以查看所教的学生的录播'),
        )

    def __unicode__(self):
        return ("UserLive->room_id:" + self.room_id)

    def get_duration_str(self, format_str=None):
        if not self.duration:
            return 0
        # print(type(seconds))
        # seconds=int(seconds)
        hour = self.duration / 3600
        min = (self.duration - hour * 3600) / 60
        second = (self.duration - hour * 3600 - min * 60)

        if not format_str:
            return '%02d:%02d:%02d' % (hour, min, second)

        elif format_str == 'min':
            return '%s' % (hour * 60 + min)

        return

    # 检查学员的助教是否点评了此次录播
    def get_mentor_comments_status(self):
        user_profile = self.user.userprofile
        if user_profile:
            user_class = self.user.userprofile.user_class
            if user_class:
                mentor = user_class.assistant
                if mentor:
                    mentor_comments = self.userlivecomment_set.filter(user=mentor)
                    if mentor_comments.exists():
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False



class UserLiveComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者')
    user_live = models.ForeignKey(UserLive)
    comment = models.TextField(verbose_name='评论')
    submit_date = models.DateTimeField(verbose_name='提交日期', default=timezone.now, db_index=True)


class UserImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    image = models.ImageField(verbose_name='图片', upload_to='course/%Y/%m/%d')
    upload_at = models.DateTimeField(verbose_name='上传时间', auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_user_image'


class UserCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    course = models.ForeignKey(Course, verbose_name='课程')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0, verbose_name='状态')  # 0 学习中，1 已完成
    passed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bee_django_course_user_course'
        permissions = [
            ('assign_user_course', '能给学生分配课程'),
        ]

    def get_pass(self):
        self.status = 1
        self.passed_at = timezone.now()
        self.save()


class UserCourseSection(models.Model):
    user_course = models.ForeignKey(UserCourse)
    section = models.ForeignKey(Section)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=0)  # 0 未开始， 1 学习中，2 通过，3 退回重修, 4 提交
    score = models.IntegerField(blank=True, null=True, verbose_name='得分')
    work_time = models.IntegerField(verbose_name='总共练习时间',
                                    null=True, blank=True, default=0)  # 学生总共练习时间
    comment = models.TextField(null=True, blank=True, verbose_name='评语')
    question_passed = models.BooleanField(default=False)
    question_passed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bee_django_course_user_course_section'
        ordering = ['-created_at']
        verbose_name = 'course学生课件'
        permissions = [
            ('view_all_usercoursesection', '查看所有学生课件'),
            ('view_teach_usercoursessection', '查看所教的学生课件'),
            ('pass_ucs', '能通过学生课件'),
            ('close_ucs', '能关闭学生课件'),
            ('open_ucs', '能开启学生课件'),
            ('review_ucs', '能查看学生作业'),
            ('score_ucs', '能给学生作业评分')
        ]

    def close(self):
        self.status = 0
        self.work_time = 0
        self.score = 0
        self.comment = None
        self.updated_at = timezone.now()
        self.save()

    def pass_check(self):
        section = self.section
        textwork_check = False
        imagework_check = False
        videowork_check = False
        question_check = False

        if section.has_textwork:
            if self.userassignment_set.exists():
                textwork_check = True
        else:
            textwork_check = True

        if section.has_imagework:
            image_count = self.userassignmentimage_set.count()
            if image_count >= section.image_count_req:
                imagework_check = True
        else:
            imagework_check = True

        if section.has_videowork:
            if self.work_time >= section.video_length_req:
                videowork_check = True
        else:
            videowork_check = True

        if section.has_questionwork:
            if self.question_passed:
                question_check = True
        else:
            question_check = True

        # 所有检查条件都通过，才可自动通过
        if textwork_check & imagework_check & videowork_check & question_check:
            return True
        else:
            return False

    def auto_pass_check(self):
        if not self.section.auto_pass:
            return False

        return self.pass_check()

    def open_ucs(self):
        # 如果课件为自动通过 先检查是否满足通过条件
        rc = self.auto_pass_check()

        if rc:
            self.get_pass()
        else:
            self.status = 1
            self.updated_at = timezone.now()
            self.save()

    def is_learning(self):
        return self.status == 1

    def is_passed(self):
        return self.status == 2

    def is_rejected(self):
        return self.status == 3

    def is_submit(self):
        return self.status == 4

    def be_submit(self):
        self.status = 4
        self.updated_at = timezone.now()
        self.save()

    def is_tip(self):
        if self.section.type == 1:
            return True
        else:
            return False

    @transaction.atomic
    def get_pass(self, score=0, comment=None):
        if self.status == 2:  # 避免重复操作
            return

        self.score = score
        self.comment = comment
        self.updated_at = timezone.now()
        self.status = 2
        self.save()

        # 发送通过的信号
        ucs_passed.send(sender=UserCourseSection, user_course_section=self)

        # 检查是否还有其他开启的课程
        learning_ucs = self.user_course.usercoursesection_set.filter(status=1)
        if learning_ucs.count() == 0:
            # 自动开启下一课
            next_section = self.next_section()
            if next_section:
                next_section.open_ucs()
            else:
                self.user_course.get_pass()  # 所有课程都通过了，则此课学习完成，通过

    @transaction.atomic
    def reject(self):
        self.score = None
        self.updated_at = timezone.now()
        self.comment = None
        self.status = 3
        self.save()

    def update_work_time(self, minutes):
        if not self.work_time:
            self.work_time = 0
        self.work_time += minutes
        self.save()

        # 检查是否可以自动通过
        rc = self.auto_pass_check()
        if rc:
            self.get_pass()

    def next_section(self, is_open=False):
        order_sets = CourseSectionMid.objects.filter(course=self.user_course.course,
                                                     section=self.section)
        if order_sets.exists():
            order = order_sets.first().order_by
            mids = CourseSectionMid.objects.filter(course=self.user_course.course, order_by__gt=order)
            if mids.exists():
                mid = mids.first()
                if is_open:
                    ucs = UserCourseSection.objects.filter(user_course=self.user_course,
                                                           status__in=[1, 2, 3, 4],
                                                           section=mid.section)
                else:
                    ucs = UserCourseSection.objects.filter(user_course=self.user_course, section=mid.section)
                if ucs.exists():
                    return ucs.first()
                else:
                    return None
            else:
                return None
        else:
            return None

    def get_section_mid_prename(self):
        try:
            mid = CourseSectionMid.objects.get(course=self.user_course.course, section=self.section)
            return mid.pre_name
        except:
            return None

    def get_section_mid_points(self):
        try:
            mid = CourseSectionMid.objects.get(course=self.user_course.course, section=self.section)
            return mid.points
        except:
            return 0


class UserAssignment(models.Model):
    user_course_section = models.ForeignKey(UserCourseSection)
    content = models.TextField(verbose_name='正文', null=True, blank=True)  # 文字作业
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(blank=True, null=True, verbose_name='得分')

    class Meta:
        permissions = (
            ('can_review', 'can review'),
        )
        db_table = 'bee_django_course_user_assignment'

    def submit(self):
        self.status = 1
        self.submit_at = timezone.now()
        self.save()

    def reject(self):
        self.status = 2
        self.rejected_at = timezone.now()
        self.save()


class UserAssignmentImage(models.Model):
    user_course_section = models.ForeignKey(UserCourseSection, null=True, blank=True)
    image = models.ImageField(verbose_name='图片作业', upload_to='assignments/%Y/%m/%d')
    upload_at = models.DateTimeField(verbose_name='上传时间', auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_user_assignment_image'


class Preference(models.Model):
    how_to_pass = models.IntegerField(verbose_name='课程通过模式', default=0)  # 0 自动， 1 手动


# 提醒助教和客服的默认处理方式
from bee_django_message.exports import send_message
from .exports import get_current_user_course, get_user_last_course_section


def notify_mentor(self):
    user_class = self.userprofile.user_class
    if not user_class:
        return -1
    if not user_class.assistant:
        return -2

    mentor = self.userprofile.user_class.assistant
    ucs = get_user_last_course_section(self)
    title = self.userprofile.name() + u'学习的课程[' + ucs.section.name + u']已经达标'

    uc = get_current_user_course(self)
    url = '/course/user_course_detail/' + str(uc.id)

    send_message(to_user=mentor, title=title, url=url)

    return 0

def notify_agent(self):
    uc = get_current_user_course(self)
    ucs = get_user_last_course_section(self)
    url = '/course/user_course_detail/' + str(uc.id)

    title = self.userprofile.name() + u'学习的课程[' + ucs.section.name + u']已经达标'

    send_message(from_user=self, title=title, url=url, message_identity='course_notify')

    return 0


User.add_to_class('notify_mentor', notify_mentor)
User.add_to_class('notify_agent', notify_agent)