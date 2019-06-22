# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.province.models import City

User = get_user_model()


# Create your models here.

class BaseEducationManager(BaseModelManager):
    def get_queryset(self):
        return super(BaseEducationManager, self).get_queryset()

    def get_this_education(self, user):
        return self.get_queryset().all()

    def active(self):
        return self.get_queryset().filter(is_published=True)

    def model_educations(self, model_obj, user_obj=None):
        objs = self.active().filter(model_obj=model_obj)
        if user_obj:
            objs = objs | self.get_queryset().filter(user_obj=user_obj)
        return objs


class BaseEducation(BaseModel):
    is_published = models.BooleanField(default=False, verbose_name=_('Published'))

    objects = BaseEducationManager()

    def __init__(self, *args, **kwargs):
        super(BaseEducation, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Base Education')
        verbose_name_plural = _('Base Education')

    # def get_education_url(self):
    #     return reverse('api:educations:detail', kwargs={'education_id':self.id})
    #
    # def get_institute_url(self):
    #     return reverse('api:educations:list', kwargs={'institute_id': self.id})


class DegreeManager(BaseEducationManager):
    def get_queryset(self):
        return super(DegreeManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_published=True)


class Degree(BaseEducation):
    name = models.CharField(max_length=50, verbose_name=_('Title'))
    objects = DegreeManager()

    def __init__(self, *args, **kwargs):
        super(Degree, self).__init__(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Degree')
        verbose_name_plural = _('Degrees')


class FieldSubjectManager(BaseEducationManager):
    def get_queryset(self):
        return super(FieldSubjectManager, self).get_queryset()


class FieldSubject(BaseEducation):
    name = models.CharField(max_length=50, verbose_name=_('Title'))
    parent_obj = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Parent Field Subject'))

    objects = FieldSubjectManager()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Field Subject')
        verbose_name_plural = _('Field Subjects')


class InstituteManager(BaseEducationManager):
    def get_queryset(self):
        return super(InstituteManager, self).get_queryset()


class Institute(BaseEducation):
    name = models.CharField(max_length=40, verbose_name=_('Institute Name'))
    cities = models.ManyToManyField(City, through='CityInstitute')
    objects = InstituteManager()

    class Meta:
        verbose_name = _('Institute')
        verbose_name_plural = _('Institutes')

    def __str__(self):
        return str(self.name)


class CityInstituteManager(BaseEducationManager):
    def get_queryset(self):
        return super(CityInstituteManager, self).get_queryset()


class CityInstitute(BaseEducation):
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name=_('City'))
    Institute = models.ForeignKey(Institute, null=True, on_delete=models.CASCADE, verbose_name=_('Institude'))

    objects = CityInstituteManager()

    # def get_queryset(self):
    #     return super(BaseEducationManager, self).get_queryset()

    class Meta:
        verbose_name = _('CityInstitute')
        verbose_name_plural = _('CityInstitutes')


class EducationManager(BaseEducationManager):
    def get_queryset(self):
        return super(EducationManager, self).get_queryset()


class Education(BaseEducation):
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    degree_obj = models.ForeignKey(Degree, null=True, on_delete=models.CASCADE, verbose_name=_('Degree'))
    institute_obj = models.ForeignKey(Institute, null=True, on_delete=models.CASCADE, verbose_name=_('Institute'))
    field_subject_obj = models.ForeignKey(FieldSubject, null=True, on_delete=models.CASCADE, verbose_name=_('Field Subject'))
    receive_date = models.DateTimeField(null=True, verbose_name=_('Receive Date'))
    average = models.FloatField(null=True, max_length=3, verbose_name=_('Average'))
    description = models.TextField(max_length=200, null=True, blank=True, verbose_name=_('Descritpion'))

    objects = EducationManager()

    def __init__(self, *args, **kwargs):
        super(Education, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Education')
        verbose_name_plural = _('Educations')

    def __str__(self):
        return str(self.user_obj)
