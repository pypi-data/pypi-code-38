#Import Standards
from django import template
from django.apps import apps
#Registramos el template
register = template.Library()

#definimos nuestros tags
@register.simple_tag
def get_modelos(app):
    models = []
    for x in apps.all_models:
        if x == app:
            for y in apps.all_models[x]:
                if apps.all_models[x][y]._meta.auto_created is False:
                    models.append(y)
    return models
