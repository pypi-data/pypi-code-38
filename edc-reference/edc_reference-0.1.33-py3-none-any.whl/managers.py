from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class ReferenceManager(models.Manager):
    def get_by_natural_key(
        self, identifier, timepoint, report_datetime, model, field_name
    ):
        return self.get(
            identifier=identifier,
            timepoint=timepoint,
            report_datetime=report_datetime,
            model=model,
            field_name=field_name,
        )

    def filter_crf_for_visit(self, name=None, visit=None):
        """Returns a queryset of reference model instances
        for this model on this visit.
        """
        return self.filter(
            identifier=visit.subject_identifier,
            model=name,
            report_datetime=visit.report_datetime,
            timepoint=visit.visit_code,
        )

    def get_crf_for_visit(self, name=None, visit=None, field_name=None):
        """Returns an instance of reference model
        for this model on this visit for this field.
        """
        try:
            model_obj = self.get(
                identifier=visit.subject_identifier,
                model=name,
                report_datetime=visit.report_datetime,
                timepoint=visit.visit_code,
                field_name=field_name,
            )
        except ObjectDoesNotExist:
            model_obj = None
        return model_obj

    def get_requisition_for_visit(self, name=None, visit=None):
        """Returns an instance of reference model
        for this requisition on this visit for this panel.
        """
        opts = dict(
            identifier=visit.subject_identifier,
            model=name,
            report_datetime=visit.report_datetime,
            timepoint=visit.visit_code,
            field_name="panel",
        )
        try:
            model_obj = self.get(**opts)
        except ObjectDoesNotExist:
            model_obj = None
        return model_obj
