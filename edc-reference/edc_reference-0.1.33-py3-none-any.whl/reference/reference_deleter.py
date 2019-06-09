from django.apps import apps as django_apps
from django.db import transaction

from ..site_reference import site_reference_configs


class ReferenceDeleter:

    """A class to delete all instances for the reference
    model for this model instance.

    See signals.
    """

    def __init__(self, model_obj=None):
        reference_model = site_reference_configs.get_reference_model(
            name=model_obj.reference_name
        )
        self.reference_model_cls = django_apps.get_model(reference_model)
        self.model_obj = model_obj
        self.reference_objects = self.reference_model_cls.objects.filter(**self.options)
        with transaction.atomic():
            self.reference_objects.delete()

    @property
    def options(self):
        return dict(
            identifier=self.model_obj.visit.subject_identifier,
            report_datetime=self.model_obj.visit.report_datetime,
            timepoint=self.model_obj.visit.visit_code,
            model=self.model_obj.reference_name,
        )
