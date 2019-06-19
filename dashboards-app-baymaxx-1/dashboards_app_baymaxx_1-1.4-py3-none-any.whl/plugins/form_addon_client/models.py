# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from cms.models import CMSPlugin

# loggin Details#

from dashboards_app.plugins.blero_grid_client.models import  BleroGrid

import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)

@python_2_unicode_compatible
class FormPlugin(CMSPlugin):

    FORM_CHOICES = (
        ('new', 'New Form'),
        ('load', 'Load Form'),

    )



    form_name = models.CharField(max_length=250, null=True, blank=True)
    button_name = models.CharField(max_length=250, null=True, blank=True)
    ajax_function = models.CharField(max_length=250, null=True, blank=True)
    py_function = models.CharField(max_length=250, null=True, blank=True)


    def __str__(self):
        return self.form_name + " id: " +str(self.pk)

    class Meta:
        verbose_name = 'Addon Form New'
        verbose_name_plural = 'Addon Forms New'






@python_2_unicode_compatible
class FormInputs(models.Model):

    STATUS_CHOICES = (
        ('text', 'TextBox'),
        ('date', 'Date Field'),
        ('checkbox', 'Checkbox'),
    )
    id_fr = models.ForeignKey(FormPlugin, related_name="form_plugin")
    input_name = models.CharField(max_length=100, null=True, blank=True)
    input_type = models.CharField(choices=STATUS_CHOICES, max_length=250, null=True, blank=True)
    input_value = models.CharField(max_length=250, verbose_name="Default Value", null=True, blank=True)



    class Meta:
        verbose_name = 'New Field'
        verbose_name_plural = 'New Fields'


#child models

class BleroGridFormClient(BleroGrid):
    parent_form=models.ForeignKey(FormPlugin,on_delete=models.CASCADE)


#Models for position
class PluginPosition(models.Model):#FormSavePosition
    model = models.ForeignKey(FormPlugin,on_delete=models.CASCADE)
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)




class InputPluginPosition(models.Model):
    model = models.OneToOneField(FormInputs, on_delete=models.CASCADE, related_name="inp_position")
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)


class LabelPluginPosition(models.Model):
    model = models.OneToOneField(FormInputs, on_delete=models.CASCADE, related_name="label_position")
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)


class FormBtnPluginPosition(models.Model):
    model = models.OneToOneField(FormPlugin, on_delete=models.CASCADE, related_name="btn_position")
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)

