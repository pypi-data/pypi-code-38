# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import datetime

from ckeditor_uploader.fields import RichTextUploadingField

from aparnik.contrib.settings.models import Setting
from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.segments.models import BaseSegment, BaseSegmentManager
from aparnik.contrib.categories.models import Category
from aparnik.packages.educations.teachers.models import Teacher
from aparnik.packages.shops.products.models import Product, ProductManager
from aparnik.packages.shops.files.models import File, FileManager

User = get_user_model()


# Total Time Manager
class TotalTimeManager(models.Manager):

    def get_queryset(self):
        return super(TotalTimeManager, self).get_queryset()


# Total Time Model
class CourseSummary(models.Model):
    total_time_seconds = models.BigIntegerField(default=0, verbose_name=_('Time'))
    file_count = models.PositiveIntegerField(default=0, verbose_name=_('File Count'))
    file_count_preview = models.PositiveIntegerField(default=0, verbose_name=_('File Count Preview'))
    type = models.CharField(max_length=1, choices=FileField.FILE_TYPE, verbose_name=_('Type'))
    course = models.ForeignKey('BaseCourse', related_name='total_times', on_delete=models.CASCADE, verbose_name=_('Course'))

    objects = TotalTimeManager()

    class Meta:
        ordering = ('id',)
        verbose_name = _('Course Summary')
        verbose_name_plural = _('Courses Summary')

    def __unicode__(self):
        return '%s' % self.id

    @property
    def total_time(self):
        time = self.total_time_seconds
        hours = time / (60 * 60)
        minutes = (time % (60 * 60)) / 60
        seconds = (time % (60 * 60)) % 60
        v_t = "{}:{}:{}".format(hours, minutes, seconds)
        return v_t

    @property
    def type_icon_url(self):
        return FileField.type_icon_url_with_custom_type(self.type)


# Base Course Manager
class BaseCourseManager(ProductManager):

    def get_queryset(self):
        return super(BaseCourseManager, self).get_queryset()

    def active(self, user=None):
        return super(BaseCourseManager, self).active(user=user)


# Base Course Model
class BaseCourse(Product):
    description = RichTextUploadingField(null=True, blank=True, config_name='custom', verbose_name=_('Description'))

    objects = BaseCourseManager()

    class Meta:
        verbose_name = _('Base Course')
        verbose_name_plural = _('Bases Courses')

    def __unicode__(self):
        return '%s' % self.id


# Course Manager
class CourseManager(BaseCourseManager):

    def get_queryset(self):
        return super(CourseManager, self).get_queryset().order_by('sort')

    def active(self, user=None):
        return super(CourseManager, self).active(user=user).filter(publish_date__lte=now())

    def get_this_user(self, user):
        # TODO: return course for this user
        return self.active()

    def courses(self):
        ids = []
        try:
            setting = Setting.objects.get(key='COURSE_IGNORE_IN_LIST_IDS')
            ids = [int(x.strip()) for x in setting.get_value().split(',')]
        except:
            pass

        return self.active().exclude(id__in=ids).filter(parent_obj=None, is_show_only_for_super_user=False)

    def childs(self, course_obj):
        return self.active().filter(parent_obj=course_obj)

    def childs_count(self, course_obj):
        return self.childs(course_obj).count()

    def children_deep(self, course=None, course_ids=None):
        if course_ids:
            courses_id = course_ids
        elif course:
            courses_id = [course.id]
        else:
            return Course.objects.none()

        course_children_ids = courses_id
        # get course children
        while True:
            course_children = Course.objects.active().filter(parent_obj__id__in=course_children_ids)

            if course_children.count() > 0:
                course_children_ids = list(course_children.values_list('id', flat=True))
                courses_id = courses_id + course_children_ids
            else:
                break
        return Course.objects.filter(id__in=courses_id)

    def parents_deep(self, course=None, course_id=None):
        course_obj = course
        if course_id:
            try:
                course_obj = Course.objects.get(id=course_id)
            except:
                return Course.objects.none()
        parent = [course_obj.id]
        while course_obj.parent_obj:
            course_obj = course_obj.parent_obj
            parent.append(course_obj.id)

        return Course.objects.filter(id__in=parent)


# Course Model
class Course(BaseCourse):
    MONTH_FARVARDIN = '1'
    MONTH_ORDIBEHESHT = '2'
    MONTH_KHORDAD = '3'
    MONTH_TIR = '4'
    MONTH_MORDAD = '5'
    MONTH_SHAHRIVAR = '6'
    MONTH_MEHR = '7'
    MONTH_ABAN = '8'
    MONTH_AZAR = '9'
    MONTH_DEY = '10'
    MONTH_BAHMAN = '11'
    MONTH_ESFAND = '12'

    MONTH_CHOICES = (
        (MONTH_FARVARDIN, _('Farvardin')),
        (MONTH_ORDIBEHESHT, _('Ordibehesht')),
        (MONTH_KHORDAD, _('Khordad')),
        (MONTH_TIR, _('Tir')),
        (MONTH_MORDAD, _('Mordad')),
        (MONTH_SHAHRIVAR, _('Shahrivar')),
        (MONTH_MEHR, _('Mehr')),
        (MONTH_ABAN, _('Aban')),
        (MONTH_AZAR, _('Azar')),
        (MONTH_DEY, _('Dey')),
        (MONTH_BAHMAN, _('Bahman')),
        (MONTH_ESFAND, _('Esfand')),

    )

    WEEK_FIRST = '1'
    WEEK_SECOND = '2'
    WEEK_THIRD = '3'
    WEEK_FOURTH = '4'
    WEEK_CHOICES = (
        (WEEK_FIRST, _('1')),
        (WEEK_SECOND, _('2')),
        (WEEK_THIRD, _('3')),
        (WEEK_FOURTH, _('4')),
    )

    DAY_FIRST = '1'
    DAY_SECOND = '2'
    DAY_THIRD = '3'
    DAY_FOURTH = '4'
    DAY_FIFTH = '5'
    DAY_SIXTH = '6'
    DAY_SEVENTH = '7'
    DAY_CHOICES = (
        (DAY_FIRST, _('Saturday')),
        (DAY_SECOND, _('Sunday')),
        (DAY_THIRD, _('Monday')),
        (DAY_FOURTH, _('Tuesday')),
        (DAY_FIFTH, _('Wednesday')),
        (DAY_SIXTH, _('Thursday')),
        (DAY_SEVENTH, _('Friday')),
    )
    
    cover = models.ForeignKey(FileField, related_name='course_cover', on_delete=models.CASCADE, verbose_name=_('Cover Image'))
    banner = models.ForeignKey(FileField, related_name='course_banner', on_delete=models.CASCADE, verbose_name=_('Banner Image'))
    # TODO: set category marboot be course
    category_obj = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Category'))
    parent_obj = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Parent'))
    dependency_obj = models.ForeignKey('self', related_name='dependency', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Dependency'))
    publish_date = models.DateTimeField(default=now, verbose_name=_('Publish Date'))
    publish_month = models.CharField(max_length=2, null=True, blank=True, choices=MONTH_CHOICES, verbose_name=_('Month'))
    publish_week = models.CharField(max_length=1, null=True, blank=True, choices=WEEK_CHOICES, verbose_name=_('Week'))
    publish_day = models.CharField(max_length=1, null=True, blank=True, choices=DAY_CHOICES, verbose_name=_('DAY'))
    teacher_obj = models.ManyToManyField(Teacher, blank=True, verbose_name=_('Teachers'))

    objects = CourseManager()

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Course, self).__init__(*args, **kwargs)

    def clean(self):
        if self.parent_obj:
            course = self
            while course:
                if course.parent_obj:
                    if course.parent_obj.id == self.id:
                        raise ValidationError({'parent_obj': [_('Can not be the parent itself.')]})
                course = course.parent_obj

            value_depth = 2
            try:
                value_depth = Setting.objects.get(key='COURSE_LEVEL').get_value()
            except:
                pass

            if self.depth > value_depth:
                raise ValidationError({'parent_obj': ValidationError(_('Depth must be less than %(value)s'),
                                                                     params={
                                                                         'value': value_depth
                                                                     })
                                       })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Course, self).save(*args, **kwargs)

    @property
    def depth(self):
        counter = 0
        course = self
        while course.parent_obj:
            counter += 1
            course = course.parent_obj

        return counter

    @property
    def teachers(self):
        teachers = None
        course = self
        while not course.teacher_obj or course.teacher_obj.count() == 0:
            last_course = course.parent_obj
            if not last_course:
                break
            course = last_course

        if course.teacher_obj:
            teachers = course.teacher_obj

        return teachers

    # def get_api_order_uri(self):
    #     return reverse("api:course:step:order", args=[self.course_obj.id, self.id])
    #
    def get_api_file_uri(self):
        return reverse('aparnik-api:educations:courses:files:list', args=[self.id])

    def get_api_file_create_uri(self):
        return reverse('aparnik-api:educations:courses:files:create', args=[self.id])

    # def get_order(self, user):
    #     from order.models import Order
    #     return Order.objects.get_order_product(user=user, product=self)

    def get_api_child_uri(self):
        return reverse('aparnik-api:educations:courses:detail', args=[self.id])

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def is_buy(self, user):

        is_buy = super(Course, self).is_buy(user=user)

        if is_buy:
            return True

        if self.parent_obj:
            return self.parent_obj.is_buy(user=user)

        return False

    def is_user_invited(self, user):
        is_user_invited = super(Course, self).is_user_invited(user=user)

        if is_user_invited:
            return True

        if self.parent_obj:
            return self.parent_obj.is_user_invited(user=user)

        return False

    @property
    def is_free(self):
        is_free = super(Course, self).is_free

        if is_free:
            return True

        if self.parent_obj:
            return self.parent_obj.is_free

        return False

    @property
    def is_subscription(self):

        is_subscription = super(Course, self).is_subscription

        if is_subscription:
            return True

        if self.parent_obj:
            return self.parent_obj.is_subscription

        return False

    def get_user_for_base_review_notification(self, instance, created):
        users = super(Course, self).get_user_for_base_review_notification(instance, created)
        if created:
            return users | User.objects.active().filter(pk__in=self.teachers.active().values_list('user_obj', flat=True))
        return users

    def has_permit_edit(self, user):
        permit = super(Course, self).has_permit_edit(user)
        if permit:
            return True
        return self.teachers.active().filter(user_obj=user).exists()


# File Manager
class CourseFileManager(FileManager):

    def get_queryset(self):
        return super(CourseFileManager, self).get_queryset().order_by('sort')

    def get_this_user(self, user):
        # TODO: return this user's course
        # return self.get_queryset().filter(users=user)
        return self.get_queryset().all()

    def get_total_time(self):
        return self.get_queryset().filter(is_free_field=False)

    def file_count(self, course_obj):
        return self.get_queryset().filter(course_obj=course_obj).count()


# File Model
class CourseFile(File):

    course_obj = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('Course'))
    # time = models.TimeField(verbose_name=_('Time'))
    seconds = models.BigIntegerField(default=0, verbose_name=_('Time'))

    objects = CourseFileManager()

    def __init__(self, *args, **kwargs):
        super(CourseFile, self).__init__(*args, **kwargs)

    def __unicode__(self):
        # self.file.size
        return "%s" % (self.title)

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')

    def save(self, *args, **kwargs):
        self.full_clean()
        # self.seconds = datetime.timedelta(hours=self.time.hour, minutes=self.time.minute, seconds=self.time.second).total_seconds()
        if self.file_obj:
            self.seconds = self.file_obj.seconds
        return super(CourseFile, self).save(*args, **kwargs)

    @property
    def is_free(self):

        is_free = super(CourseFile, self).is_free

        if is_free:
            return is_free

        if self.course_obj:
            return self.course_obj.is_free

        return False

    @property
    def is_subscription(self):
        is_subscription = super(CourseFile, self).is_subscription

        if is_subscription:
            return is_subscription

        if self.course_obj:
            return self.course_obj.is_subscription

        return False

    def is_buy(self, user):

        is_buy = super(CourseFile, self).is_buy(user=user)

        if is_buy:
            return is_buy

        if self.course_obj:
            return self.course_obj.is_buy(user=user)

        return False

    def is_user_invited(self, user):
        is_user_invited = super(CourseFile, self).is_user_invited(user=user)

        if is_user_invited:
            return is_user_invited

        if self.course_obj:
            return self.course_obj.is_user_invited(user=user)

        return False

    def get_user_for_base_review_notification(self, instance, created):
        users = super(CourseFile, self).get_user_for_base_review_notification(instance, created)
        if created:
            return users | User.objects.active().filter(pk__in=self.course_obj.teachers.active().values_list('user_obj', flat=True))
        return users

    def has_permit_edit(self, user):
        permit = super(CourseFile, self).has_permit_edit(user)
        if permit:
            return True
        return self.course_obj.teachers.active().filter(user_obj=user).exists()


def post_save_course_receiver(sender, instance, created, *args, **kwargs):
    if instance.sort == 0:
        max = Course.objects.filter(parent_obj=instance.parent_obj).aggregate(Max('sort'))['sort__max']
        instance.sort = max + 1
        instance.save()
    else:
        for course in Course.objects.exclude(id=instance.id).filter(parent_obj=instance.parent_obj, sort=instance.sort):
            course.sort = course.sort + 1
            course.save()


def post_save_file_receiver(sender, instance, created, *args, **kwargs):
    if instance.sort == 0:
        max = CourseFile.objects.filter(course_obj=instance.course_obj).aggregate(Max('sort'))['sort__max']
        instance.sort = max + 1
        instance.save()
    else:
        for file in CourseFile.objects.exclude(id=instance.id).filter(course_obj=instance.course_obj, sort=instance.sort):
            file.sort = file.sort + 1
            file.save()


post_save.connect(post_save_course_receiver, sender=Course)
post_save.connect(post_save_file_receiver, sender=CourseFile)


# Course Segment Model
class CourseSegment(BaseSegment):

    objects = BaseSegmentManager()

    def __unicode__(self):
        return super(CourseSegment, self).__unicode__()

    class Meta:
        verbose_name = _('Course Segment')
        verbose_name_plural = _('Courses Segments')
