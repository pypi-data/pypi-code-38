# -*- coding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models

# Create your models here.


class Province(models.Model):

    title = models.CharField(max_length=100, verbose_name=_('Title'))

    class Meta:
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')

    def __str__(self):

        return self.title

    def get_api_url(self):
        return reverse("aparnik-api:provinces:detail", kwargs={"id": self.id})

    def get_api_url_city(self):
        return reverse("aparnik-api:provinces:city-api:list", kwargs={"province_id": self.id})

    def get_api_url_shahrak(self):
        return reverse("aparnik-api:provinces:shahrak-api:list", kwargs={"province_id": self.id})


class City(models.Model):

    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name=_('Province'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return "%s - %s"%(self.province.title, self.title)

    def get_api_url(self):
        return reverse("aparnik-api:provinces:city-api:detail", kwargs={"province_id": self.province.id, "id": self.id})

    def get_api_url_town(self):
        return reverse("aparnik-api:provinces:city-api:town-api:list", kwargs={"province_id": self.province.id, "city_id": self.id})


class Shahrak(models.Model):

    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name=_('Province'))
    title = models.TextField(verbose_name=_('Title'))

    class Meta:
        verbose_name = _('Shahrak')
        verbose_name_plural = _('Shahraks')

    def __str__(self):
        return "%s - %s"%(self.province.title, self.title)

    def get_api_url(self):
        return reverse("aparnik-api:provinces:shahrak-api:detail", kwargs={"province_id": self.province.id, "id": self.id})


class Town(models.Model):

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name=_('City'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))

    class Meta:
        verbose_name = _('Town')
        verbose_name_plural = _('Towns')

    def __str__(self):
        return "%s - %s"%(self.city.title, self.title)

    def get_api_url(self):
        return reverse("aparnik-api:provinces:city-api:town-api:detail", kwargs={"province_id": self.city.province.id, "city_id": self.city.id, "id": self.id})