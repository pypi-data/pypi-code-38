import os

from django.apps import apps as django_apps
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import MultipleObjectMixin
from django_orion_model.models.connectors import ServicePath, ContextBroker
from django_orion_model.models.entities import OrionEntity
from logging import getLogger


logger = getLogger(__name__)


def select_subclass(base_model, orion_type, orion_sub_type):
    class_to_use = None
    subclasses = [subclass for subclass in base_model.__subclasses__()]
    while subclasses:
        cls = subclasses.pop()
        if cls.orion_type == orion_type:
            if (orion_sub_type is None) or orion_sub_type == cls.ORION_SUB_TYPE:
                class_to_use = cls
                break
            elif cls.ORION_SUB_TYPE is None:
                class_to_use = cls
        subclasses.extend(subclass for subclass in cls.__subclasses__())
    class_to_use = class_to_use or base_model
    return class_to_use


def get_context_broker_and_service_path(context_broker, service_path):
    service_path = ServicePath.objects.get(name=service_path)
    context_broker = ContextBroker.objects.get(name=context_broker)
    return context_broker, service_path


def get_types(base_model, root=False):
    if root:
        subclasses = [base_model]
    else:
        try:
            subclasses = base_model.__subclasses__()
        except AttributeError as ex:
            logger.warning("While unraveling base class: %s", ex.message)
            return []
    types = []
    while subclasses:
        try:
            subclass = subclasses.pop()
            subclasses.extend(subclass.__subclasses__())
            types.append({
                "app": subclass._meta.app_label,
                "model": subclass.__name__,
                "orion_type": subclass.ORION_TYPE,
                "caption": subclass._meta.verbose_name
            })
        except AttributeError as ex:
            logger.warning("While unraveling subclasses: %s", ex.message)

    return types


class DynamicModelView(ModelFormMixin):

    app_label = None
    model_name = None

    model = None
    base_model = None

    def get_form_class(self):
        if self.model is None:
            self.app_label = self.kwargs.get("app",  self.request.GET.get("app", self.base_model._meta.app_label))
            self.model_name = self.kwargs.get("model", self.request.GET.get("model", self.base_model._meta.model_name))
            self.model = django_apps.get_model(self.app_label, self.model_name)
        return super().get_form_class()


class DynamicTemplate(SingleObjectTemplateResponseMixin):
    template_path = ""
    model = None
    base_model = None
    name_template = "{}{}/{}.html"

    def get_template_names(self):
        names = []

        file_name = self.name_template.format(self.template_path, self.model._meta.app_label, self.model._meta.model_name)
        # orion_manager/forms/waste_collection/waste.html
        names.append(file_name)
        # orion_manager/forms/waste.html
        names.append(os.path.join(self.template_path, file_name))
        backup_models = [p for p in self.model._meta.parents if issubclass(p, self.base_model)]
        while backup_models:
            next_model = backup_models.pop()

            # orion_manager/forms/waste_collection/waste.html
            file_name = self.name_template.format(
                self.template_path, next_model._meta.app_label, next_model._meta.model_name)
            names.append(file_name)
            # Add parents while are subclass of parent node and not yet included
            backup_models.extend(
                p for p in next_model._meta.parents if issubclass(p, self.base_model) if p not in backup_models)
        return names


class DynamicQuerySet(MultipleObjectMixin):

    def get_queryset(self):
        context_broker, service_path = get_context_broker_and_service_path(
            context_broker=self.request.GET.get("context_broker", "default"),
            service_path=self.request.GET.get("service_path", "real"))

        orion_type = self.request.GET.get("ORION_TYPE", OrionEntity.orion_type)
        orion_sub_type = self.request.GET.get("ORION_SUB_TYPE", OrionEntity.ORION_SUB_TYPE)
        class_to_use = select_subclass(self.model, orion_type, orion_sub_type)
        self.queryset = class_to_use.objects.filter(
            orion_context_broker=context_broker, orion_service_path=service_path)

        return super().get_queryset()