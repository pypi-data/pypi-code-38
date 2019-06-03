#Import Oficiales
from django.db import models
from django.core.cache import cache

#Imports del proyecto

#Definimos nuestras funciones
def get_fields(clase):
    lista = []
    for field in clase._meta.fields:
        if field.is_relation:#If foreignKey
            lista.append((field.name, 'ForeingKey', field.get_internal_type(), field.related_model._meta.app_label, field.related_model._meta.model_name))
        else:
            lista.append((field.name, 'RegularField', field.get_internal_type()))
    for field in clase._meta.many_to_many:
        lista.append((field.name, 'ManyToMany', field.get_internal_type(), field.related_model._meta.app_label, field.related_model._meta.model_name))
    return lista
