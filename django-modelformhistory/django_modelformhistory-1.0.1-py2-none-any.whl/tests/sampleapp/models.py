# coding: utf-8
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


FOO_CHOICES = (("ok", "It's OK"), ("nok", "It's not OK"))


@python_2_unicode_compatible
class Bar(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Baz(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Foo(models.Model):
    name = models.CharField("Name of this instance", max_length=100)
    integer = models.IntegerField("Type your favorite integer")
    choose_somthing = models.CharField("Make your choice", max_length=100, choices=FOO_CHOICES, default="ok")
    bar = models.ForeignKey(Bar, verbose_name="Name of the bar", null=True, blank=True)
    baz = models.ManyToManyField(Baz, verbose_name="Select some baz", blank=True)

    def __str__(self):
        return self.name
