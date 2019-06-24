from importlib import import_module

from django.conf import settings
from django.conf.urls import url, include

from djangoldp.models import LDPSource, Model
from djangoldp.views import LDPSourceViewSet


def __clean_path(path):
    if path.startswith("/"):
        path = path[1:]
    if not path.endswith("/"):
        path = "{}/".format(path)
    return path


urlpatterns = [
    url(r'^sources/', LDPSourceViewSet.urls(model=LDPSource)),
]

for package in settings.DJANGOLDP_PACKAGES:
    try:
        import_module('{}.models'.format(package))
    except ModuleNotFoundError:
        pass

model_classes = {cls.__name__: cls for cls in Model.__subclasses__()}

for class_name in model_classes:
    model_class = model_classes[class_name]
    path = __clean_path(model_class.get_container_path())
    urls_fct = model_class.get_view_set().urls
    urlpatterns.append(url(r'^' + path, include(
        urls_fct(model=model_class,
                 lookup_field=Model.get_meta(model_class, 'lookup_field', 'pk'),
                 permission_classes=Model.get_meta(model_class, 'permission_classes', []),
                 fields=Model.get_meta(model_class, 'serializer_fields', []),
                 nested_fields=Model.get_meta(model_class, 'nested_fields', [])))))

for package in settings.DJANGOLDP_PACKAGES:
    try:
        urlpatterns.append(url(r'^', include('{}.djangoldp_urls'.format(package))))
    except ModuleNotFoundError:
        pass
