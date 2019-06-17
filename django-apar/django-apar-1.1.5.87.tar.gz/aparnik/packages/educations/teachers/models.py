# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.sliders.models import SliderSegment

User = get_user_model()


# Create your models here.


class TeacherManager(BaseModelManager):
    def get_queryset(self):
        return super(TeacherManager, self).get_queryset()

    def get_this_teacher(self, user):
        return self.active().all()

    def active(self, user=None):
        return super(TeacherManager, self).active(user=user)

    def model_teachers(self, model_obj, user_obj=None):
        objs = self.active().filter(model_obj=model_obj)
        if user_obj:
            objs = objs | self.get_queryset().filter(model_obj=model_obj, user_obj=user_obj)
        return objs


class Teacher(BaseModel):
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    slider_segment_obj = models.ForeignKey(SliderSegment, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Slider Semgent'))
    biography = models.TextField(null=False, blank=False, verbose_name=_('Biography'))
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Start Date'))

    objects = TeacherManager()

    def __init__(self, *args, **kwargs):
        super(Teacher, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')

    def __str__(self):
        return str(self.user_obj)

    def get_models(self):
        return self.course_set.active().filter(parent_obj__isnull=True)

    def get_segments(self):
        self.get_models()

    def get_api_models_uri(self):
        return reverse('aparnik-api:educations:teachers:models-list', args=[self.id])


class DossierManager(BaseModelManager):
    def get_queryset(self):
        return super(DossierManager, self).get_queryset()


class Dossier(BaseModel):
    teacher_obj = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_('teacher'))
    activity = models.TextField(null=False, blank=False, verbose_name=_('activity'))
    start_date = models.DateTimeField(verbose_name=_('Start Date'))
    finish_date = models.DateTimeField(verbose_name=_('Finish Date'))

    objects = DossierManager()

    def __init__(self, *args, **kwargs):
        super(Dossier, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Dossier')
        verbose_name_plural = _('Dossiers')

    def __str__(self):
        return str(self.teacher_obj)
