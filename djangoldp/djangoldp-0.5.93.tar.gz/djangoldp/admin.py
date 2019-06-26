from importlib import import_module

from django.conf import settings
from django.contrib import admin
from .models import LDPSource, Model

for package in settings.DJANGOLDP_PACKAGES:
    try:
        import_module('{}.admin'.format(package))
    except ModuleNotFoundError:
        pass

for package in settings.DJANGOLDP_PACKAGES:
    try:
        import_module('{}.models'.format(package))
    except ModuleNotFoundError:
        pass

model_classes = {cls.__name__: cls for cls in Model.__subclasses__()}

for class_name in model_classes:
    model_class = model_classes[class_name]
    if not admin.site.is_registered(model_class):
        admin.site.register(model_class)

admin.site.register(LDPSource)
