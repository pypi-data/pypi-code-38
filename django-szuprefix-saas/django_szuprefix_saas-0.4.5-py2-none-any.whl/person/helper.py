# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from . import models
from django_szuprefix.utils.modelutils import translate_model_values

def init_person(worker):
    profile = worker.profile
    fns = "email,mobile,id_card,gender,ethnic,city".split(",")
    ps = translate_model_values(models.Person, profile, fns)
    ps['name'] = worker.name
    # print "init_person", ps
    return models.Person.objects.update_or_create(
        user=worker.user,
        defaults=ps)
